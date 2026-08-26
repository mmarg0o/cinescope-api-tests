from models.base_models import TestUser
import allure
import pytest 
from playwright.sync_api import expect


@allure.epic("Тестирование UI")
@allure.feature("Регистрация")
@pytest.mark.ui
class TestRegistration:
    @allure.title("Успешная регистрация нового пользователя")
    def test_registration(self, register_page, page, test_user: TestUser):
        register_page.register(test_user.fullName, test_user.email, test_user.password)
        expect(page.get_by_text("Подтвердите свою почту")).to_be_visible()