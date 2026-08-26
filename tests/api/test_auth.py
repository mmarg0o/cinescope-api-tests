import pytest
from data.auth.register_data import get_register_payload
import requests
from models.base_models import RegisterUserResponse
from clients.api_manager import ApiManager
from db_models.user import UserDBModel
import uuid
from datetime import datetime

class TestAuth:

    def test_register_user(self, api_manager: ApiManager, test_user):
        response = api_manager.auth_api.register_user(user_data=test_user)
        register_user_response = RegisterUserResponse(**response.json())
        assert register_user_response.email == test_user.email, "Email не совпадает"

    def test_negative_register_duplicate_email(self, api_manager, test_user):
        api_manager.auth_api.register_user(test_user)
        api_manager.auth_api.register_user(test_user, expected_status=409)

    def test_negative_register_invalid_password(self, api_manager, test_user):
        test_user.password = "123"
        test_user.passwordRepeat = "123"
        api_manager.auth_api.register_user(test_user, expected_status=400)

    def test_login(self, api_manager, registered_user):
        login_data = {"email": registered_user["email"], "password": registered_user["password"]}
        response = api_manager.auth_api.login_user(login_data)
        assert response.json()["accessToken"]

    def test_negative_login_wrong_password(self, api_manager, registered_user):
        login_data = {"email": registered_user["email"], "password": "WrongPass123!"}
        api_manager.auth_api.login_user(login_data, expected_status=401)

    def test_negative_login_user_not_found(self, api_manager):
        login_data = {"email": "nonexistent@test.com", "password": "SomePass123!"}
        api_manager.auth_api.login_user(login_data, expected_status=401)

    def test_logout_user(self, api_manager, authenticated_user):
        response = api_manager.auth_api.logout_user()
        assert response.status_code == 200

    def test_get_user_info_unauthorized(self, api_manager):
        api_manager.user_api.get_user_info(user_id=1, expected_status=401)

    def test_get_user_info(self, authenticated_user, super_admin):
        response = super_admin.api.user_api.get_user_info(authenticated_user["id"])
        response_data = response.json()
        
        assert response_data["email"] == authenticated_user["email"]
        assert response_data["id"] == authenticated_user["id"]
        
    def test_register_timeout(self, api_manager, test_user):
        with pytest.raises(requests.exceptions.ConnectTimeout):
            api_manager.auth_api.register_user(test_user, timeout=0.001)

    def test_delete_users(self, super_admin):
        id1 = super_admin.api.auth_api.register_user(get_register_payload()).json()["id"]
        id2 = super_admin.api.auth_api.register_user(get_register_payload()).json()["id"]
        id3 = super_admin.api.auth_api.register_user(get_register_payload()).json()["id"]
        
        super_admin.api.user_api.delete_users(id1, id2, id3)


class TestUserAPI:
    def test_create_user(self, super_admin, creation_user_data):
        response = super_admin.api.user_api.create_user(creation_user_data).json()

        assert response.get('id') and response['id'] != '', "ID должен быть не пустым"
        assert response.get('email') == creation_user_data['email']
        assert response.get('fullName') == creation_user_data['fullName']
        assert response.get('roles', []) == creation_user_data['roles']
        assert response.get('verified') is True

    def test_get_user_by_locator(self, super_admin, creation_user_data):
        created_user_response = super_admin.api.user_api.create_user(creation_user_data).json()
        response_by_id = super_admin.api.user_api.get_user(created_user_response["id"]).json()
        response_by_email = super_admin.api.user_api.get_user(creation_user_data["email"]).json()

        assert response_by_id == response_by_email, "Содержание ответов должно быть идентичным"
        assert response_by_id.get('id') and response_by_id['id'] != '', "ID должен быть не пустым"
        assert response_by_id.get('email') == creation_user_data['email']
        assert response_by_id.get('fullName') == creation_user_data['fullName']
        assert response_by_id.get('roles', []) == creation_user_data['roles']
        assert response_by_id.get('verified') is True

    def test_get_user_by_id_common_user(self, common_user):
        common_user.api.user_api.get_user(common_user.email, expected_status=403)

class TestUserDB:
    def test_create_user_db(self, db_session):
            user_data = {
                "id": str(uuid.uuid4()),
                "email": f"test_{uuid.uuid4()}@test.com",
                "full_name": "Test User",
                "password": "password123",
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "verified": True,
                "banned": False,
            }
            user = UserDBModel(**user_data)
            db_session.add(user)
            db_session.commit()
            db_session.refresh(user)