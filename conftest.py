import requests
import pytest
from clients.api_manager import ApiManager
from utils.data_generator import DataGenerator 
from resources.user_creds import SuperAdminCreds
from data.movies.movie_data import get_movie_payload
import uuid
from entities.user import User
from constants.roles import Roles
from models.base_models import TestUser
from sqlalchemy.orm import Session
from db_requester.db_client import get_db_session
from db_requester.db_helpers import DBHelper
from playwright.sync_api import Page
from pages.register_page import CinescopeRegisterPage
from pages.login_page import CinescopeLoginPage
from pages.movie_page import CinescopeMoviePage

@pytest.fixture
def session():
    http_session = requests.Session()
    yield http_session
    http_session.close()


@pytest.fixture
def api_manager(session):
    return ApiManager(session)


@pytest.fixture
def test_user() -> TestUser:
    random_password = DataGenerator.generate_random_password()

    return TestUser(
        email=DataGenerator.generate_random_email(),
        fullName=DataGenerator.generate_random_name(),
        password=random_password,
        passwordRepeat=random_password,
        roles=[Roles.USER.value]
    )


@pytest.fixture
def registered_user(api_manager, test_user):
    response = api_manager.auth_api.register_user(test_user).json()
    user_data = test_user.model_dump()
    user_data["id"] = response["id"]
    return user_data


@pytest.fixture
def authenticated_user(api_manager, test_user):
    response = api_manager.auth_api.register_user(test_user).json()
    api_manager.auth_api.authenticate((test_user.email, test_user.password))
    return {
        "id": response["id"],
        "email": response["email"],
        "password": test_user.password,
        "roles": response["roles"]
    }


@pytest.fixture
def creation_user_data(test_user: TestUser) -> dict:
    updated_data = test_user.model_dump(mode="json")
    updated_data.update({
        "verified": True,
        "banned": False
    })
    return updated_data


@pytest.fixture
def user_session():
    user_pool = []

    def _create_user_session():
        session = requests.Session()
        user_session = ApiManager(session)
        user_pool.append(user_session)
        return user_session

    yield _create_user_session

    for user in user_pool:
        user.close_session()


@pytest.fixture
def super_admin(user_session):
    new_session = user_session()

    super_admin = User(
        SuperAdminCreds.USERNAME,
        SuperAdminCreds.PASSWORD,
        [Roles.SUPER_ADMIN.value],
        new_session)

    super_admin.api.auth_api.authenticate(super_admin.creds)
    return super_admin

@pytest.fixture
def common_user(user_session, super_admin, creation_user_data):
    new_session = user_session()

    common_user = User(
        creation_user_data['email'],
        creation_user_data['password'],
        list(Roles.USER.value),
        new_session)

    super_admin.api.user_api.create_user(creation_user_data)
    common_user.api.auth_api.authenticate(common_user.creds)
    return common_user


@pytest.fixture
def admin_user(user_session, super_admin, creation_user_data):
    new_session = user_session()

    admin_data = creation_user_data.copy()
    admin_data["roles"] = [Roles.ADMIN.value]

    admin_user = User(
        admin_data['email'],
        admin_data['password'],
        [Roles.ADMIN.value],
        new_session)

    super_admin.api.user_api.create_user(admin_data)
    admin_user.api.auth_api.authenticate(admin_user.creds)
    return admin_user


@pytest.fixture
def unique_genre(super_admin):
    genre_data = {"name": f"Tests genre: {uuid.uuid4().hex[:8]}"}
    genre = super_admin.api.genres_api.create_genre(genre_data).json()
    yield genre
    super_admin.api.genres_api.delete_genre(genre["id"])


@pytest.fixture
def created_movie(request, super_admin, unique_genre):

    should_delete = getattr(request, "param", True)

    movie = get_movie_payload(genre_id=unique_genre["id"])
    response = super_admin.api.movies_api.create_movie(movie).json()
    movie["id"] = response["id"]
    yield movie

    if should_delete:
        check = super_admin.api.movies_api.get_movie(movie["id"], expected_status=None)
        if check.status_code == 200:
            super_admin.api.movies_api.delete_movie(movie["id"])


@pytest.fixture
def movie_with_unique_genre(request, super_admin):
    params = request.param

    genre_data = {"name": f"{params['genre']}_{uuid.uuid4().hex[:8]}"}
    genre = super_admin.api.genres_api.create_genre(genre_data).json()

    movie = get_movie_payload(genre_id=genre["id"])
    response = super_admin.api.movies_api.create_movie(movie).json()
    movie["id"] = response["id"]

    yield movie

    super_admin.api.movies_api.delete_movie(movie["id"])
    super_admin.api.genres_api.delete_genre(genre["id"])

@pytest.fixture(scope="module")
def db_session() -> Session:
    
    db_session = get_db_session()
    yield db_session
    db_session.close()

@pytest.fixture(scope="function")
def db_helper(db_session) -> DBHelper:

    db_helper = DBHelper(db_session)
    return db_helper

@pytest.fixture(scope="function")
def created_test_user(db_helper):
    user = db_helper.create_test_user(DataGenerator.generate_user_data())
    yield user
    if db_helper.get_user_by_id(user.id):
        db_helper.delete_user(user)

@pytest.fixture(scope="session")
def browser(playwright):
    browser = playwright.chromium.launch(headless=False)
    yield browser
    browser.close()

@pytest.fixture
def context(browser):
    context = browser.new_context()
    yield context
    context.close()

@pytest.fixture
def page(context):
    page = context.new_page()
    yield page
    page.close()

@pytest.fixture
def register_page(page: Page) -> CinescopeRegisterPage:
    register_page = CinescopeRegisterPage(page)
    register_page.open()
    return register_page

@pytest.fixture
def login_page(page: Page) -> CinescopeLoginPage:
    login_page = CinescopeLoginPage(page)
    login_page.open()
    return login_page

@pytest.fixture
def authenticated_page(page: Page, registered_user, test_user) -> Page:
    login_page = CinescopeLoginPage(page)
    login_page.open()
    login_page.login(test_user.email, test_user.password)
    return page


@pytest.fixture
def movie_page(authenticated_page: Page, created_movie) -> CinescopeMoviePage:
    movie_page = CinescopeMoviePage(authenticated_page, created_movie["id"])
    movie_page.open()
    return movie_page