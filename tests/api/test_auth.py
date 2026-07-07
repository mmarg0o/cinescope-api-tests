import pytest
from data.auth.register_data import get_register_payload
import requests

class TestAuth:
    def test_register(self, api_manager, test_user): 
        response = api_manager.auth_api.register_user(test_user)
        assert response.json()["email"] == test_user["email"]

    def test_negative_register_duplicate_email(self, api_manager, test_user):
        api_manager.auth_api.register_user(test_user)
        api_manager.auth_api.register_user(test_user, expected_status=409)

    def test_negative_register_invalid_password(self, api_manager, test_user):
        test_user["password"] = "123"
        test_user["passwordRepeat"] = "123"
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

    def test_get_user_info(self, authenticated_user, super_admin_api_manager):
        response = super_admin_api_manager.user_api.get_user_info(authenticated_user["id"])
        response_data = response.json()
        
        assert response_data["email"] == authenticated_user["email"]
        assert response_data["id"] == authenticated_user["id"]
        
    def test_register_timeout(self, api_manager, test_user):
        with pytest.raises(requests.exceptions.ConnectTimeout):
            api_manager.auth_api.register_user(test_user, timeout=0.001)

    def test_delete_users(self, super_admin_api_manager):
        id1 = super_admin_api_manager.auth_api.register_user(get_register_payload()).json()["id"]
        id2 = super_admin_api_manager.auth_api.register_user(get_register_payload()).json()["id"]
        id3 = super_admin_api_manager.auth_api.register_user(get_register_payload()).json()["id"]
        
        super_admin_api_manager.user_api.delete_users(id1, id2, id3)