import allure
import pytest
from playwright.sync_api import expect

@allure.epic("Тестирование UI")
@allure.feature("Отзывы")
@pytest.mark.ui
class TestReview:

    @allure.title("Добавление отзыва под фильмом")
    def test_add_review(self, movie_page):
        with allure.step("Оставить отзыв под фильмом"):
            movie_page.add_review("Test review")

        with allure.step("Проверить, что отзыв успешно создан"):
            expect(movie_page.page.get_by_text("Отзыв успешно создан")).to_be_visible()