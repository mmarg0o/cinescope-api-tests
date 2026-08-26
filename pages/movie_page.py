from playwright.sync_api import Page
from pages.base_page import BasePage


class CinescopeMoviePage(BasePage):

    def __init__(self, page: Page, movie_id: int):
        super().__init__(page)
        self.url = f"{self.home_url}movies/{movie_id}"
        self.review_input = '[data-qa-id="movie_review_input"]'
        self.submit_review_button = '[data-qa-id="movie_review_submit_button"]'

    def open(self):
        self.open_url(self.url)

    def add_review(self, text: str):
        self.enter_text(self.review_input, text)
        self.click(self.submit_review_button)