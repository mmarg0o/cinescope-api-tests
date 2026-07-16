import requests
import pytest
from clients.api_manager import ApiManager
from data.auth.register_data import get_register_payload 
from config.credentials import SUPER_ADMIN_EMAIL, SUPER_ADMIN_PASSWORD
from data.movies.movie_data import get_movie_payload
import uuid

@pytest.fixture
def session():
    http_session = requests.Session()
    yield http_session
    http_session.close()


@pytest.fixture
def api_manager(session):
    return ApiManager(session)


@pytest.fixture
def test_user():
    return get_register_payload()


@pytest.fixture
def registered_user(api_manager, test_user):
    response = api_manager.auth_api.register_user(test_user).json()
    test_user["id"] = response["id"]
    return test_user


@pytest.fixture
def authenticated_user(api_manager, test_user):
    response = api_manager.auth_api.register_user(test_user).json()
    api_manager.auth_api.authenticate((test_user["email"], test_user["password"]))
    return {
        "id": response["id"],
        "email": response["email"],
        "password": test_user["password"],
        "roles": response["roles"]
    }

@pytest.fixture
def super_admin_api_manager():
    admin_session = requests.Session()
    api = ApiManager(admin_session)
    api.auth_api.authenticate((SUPER_ADMIN_EMAIL, SUPER_ADMIN_PASSWORD))
    yield api
    admin_session.close()


@pytest.fixture
def unique_genre(super_admin_api_manager):
    genre_data = {"name": f"Tests genre: {uuid.uuid4().hex[:8]}"}
    genre = super_admin_api_manager.genres_api.create_genre(genre_data).json()
    yield genre
    super_admin_api_manager.genres_api.delete_genre(genre["id"])


@pytest.fixture
def created_movie(super_admin_api_manager, unique_genre):
    movie = get_movie_payload(genre_id=unique_genre["id"])
    response = super_admin_api_manager.movies_api.create_movie(movie).json()
    movie["id"] = response["id"]
    yield movie
    super_admin_api_manager.movies_api.delete_movie(movie["id"])


@pytest.fixture
def created_movie_for_delete(super_admin_api_manager):
     movie = get_movie_payload()
     response = super_admin_api_manager.movies_api.create_movie(movie).json()
     movie["id"] = response["id"]
     return movie