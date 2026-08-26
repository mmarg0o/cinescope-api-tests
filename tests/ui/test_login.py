import allure
import pytest
from playwright.sync_api import expect

@allure.epic("Тестирование UI")
@allure.feature("Логин")
@pytest.mark.ui
class TestLogin:
    @allure.title("Успешный логин существующего пользователя")
    def test_login(self, login_page, page, registered_user):
        login_page.login(registered_user["email"], registered_user["password"])
        page.wait_for_url("https://dev-cinescope.coconutqa.ru/")
        expect(page.get_by_text("Вы вошли в аккаунт")).to_be_visible()