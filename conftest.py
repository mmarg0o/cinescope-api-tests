import requests
import pytest
from clients.api_manager import ApiManager
from data.auth.register_data import get_register_payload 
from config.credentials import SUPER_ADMIN_EMAIL, SUPER_ADMIN_PASSWORD

@pytest.fixture(scope="function") #поменяла scope на function, потому что при class одна сессия переиспользовалась между тестами из-за чего переносилась авторизация и тесты влияли друг на друга
def session():
    http_session = requests.Session()
    yield http_session
    http_session.close()


@pytest.fixture(scope="function")
def api_manager(session):
    return ApiManager(session)


@pytest.fixture(scope="function")
def test_user():
    return get_register_payload()


@pytest.fixture(scope="function")
def registered_user(api_manager, test_user):
    response = api_manager.auth_api.register_user(test_user).json()
    test_user["id"] = response["id"]
    return test_user


@pytest.fixture(scope="function")
def authenticated_user(api_manager, test_user):
    response = api_manager.auth_api.register_user(test_user).json()
    api_manager.auth_api.authenticate((test_user["email"], test_user["password"]))
    return {
        "id": response["id"],
        "email": response["email"],
        "password": test_user["password"],
        "roles": response["roles"]
    }

@pytest.fixture(scope="function")
def super_admin_api_manager():
    admin_session = requests.Session()
    api = ApiManager(admin_session)
    api.auth_api.authenticate((SUPER_ADMIN_EMAIL, SUPER_ADMIN_PASSWORD))
    yield api
    admin_session.close()