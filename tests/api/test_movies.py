from data.movies.movie_data import get_movie_payload
import pytest
import uuid
from datetime import datetime
from db_models.movies import MovieDBModel
import allure

@allure.epic("Cinescope")
@allure.feature("Movies")
class TestMovies:

    @pytest.mark.smoke
    @allure.story("Получение фильмов")
    def test_get_movies(self, api_manager):
        with allure.step("Запрос на получение фильмов"):
            response = api_manager.movies_api.get_movies()
            response_data = response.json()

        with allure.step("Проверка структуры ответа"):
            assert isinstance(response_data["movies"], list)
            assert isinstance(response_data["count"], int)
            assert isinstance(response_data["page"], int)
            assert isinstance(response_data["pageSize"], int)
            assert isinstance(response_data["pageCount"], int)

    @allure.story("Фильтрация фильмов")
    @pytest.mark.parametrize(
    "movie_with_unique_genre",
    [{"genre": "Comedy"}, {"genre": "Drama"}],
    indirect=True)
    def test_get_movies_by_filters(self, api_manager, movie_with_unique_genre, db_helper):
        with allure.step("Запрос фильмов с фильтрами"):
            response = api_manager.movies_api.get_movies(
                params={
                    "genreId": movie_with_unique_genre["genreId"],
                    "location": movie_with_unique_genre["location"],
                    "minPrice": movie_with_unique_genre["price"] - 10,
                    "maxPrice": movie_with_unique_genre["price"] + 10
                }
            )
            movies = response.json()["movies"]

        with allure.step("Проверка, что созданный фильм есть в результатах фильтрации"):
            found_movie = None
            for movie in movies:
                if movie["id"] == movie_with_unique_genre["id"]:
                    found_movie = movie

            assert found_movie is not None

        with allure.step("Проверка соответствия данных из ответа API данным из бд"):
            movie_in_db = db_helper.get_movie_by_id(movie_with_unique_genre["id"])
            assert found_movie["id"] == movie_in_db.id
            assert found_movie["name"] == movie_in_db.name
            assert found_movie["price"] == movie_in_db.price
            assert found_movie["location"] == movie_in_db.location

    @allure.story("Валидация страницы")
    def test_get_movies_invalid_page(self, api_manager):
        with allure.step("Запрос с невалидным номером страницы"):
            response = api_manager.movies_api.get_movies(params = {"page": -1}, expected_status=400)
            response_data = response.json()

        with allure.step("Проверка текста ошибки"):
            assert response_data["message"][0] == "Поле page имеет минимальную величину 1"

    @pytest.mark.smoke
    @allure.story("Получение фильма")
    def test_get_movie(self, api_manager, created_movie, db_helper):

        with allure.step("Запрос на получение фильма"):
            response = api_manager.movies_api.get_movie(created_movie["id"])
            response_data = response.json()

        with allure.step("Проверка данных фильма"):
            assert response_data["id"] == created_movie["id"]
            assert response_data["name"] == created_movie["name"]

        with allure.step("Проверка соответствия данных из ответа API данным из бд"):
                    movie_in_db = db_helper.get_movie_by_id(response_data["id"])
                    assert movie_in_db is not None
                    assert movie_in_db.id == response_data["id"]
                    assert movie_in_db.name == response_data["name"]
                    assert movie_in_db.price == response_data["price"]
                    assert movie_in_db.genre_id == response_data["genreId"]
                    assert movie_in_db.location == response_data["location"]

    @allure.story("Получение фильма")
    def test_get_movie_not_found(self, api_manager):

        with allure.step("Запрос несуществующего фильма"):
            response = api_manager.movies_api.get_movie(movie_id=99999, expected_status=404)
            response_data = response.json()

        with allure.step("Проверка текста ошибки"):    
            assert response_data["message"] == "Фильм не найден"

    @pytest.mark.smoke
    @allure.story("Создание фильма")
    def test_create_movie(self, super_admin, unique_genre, db_helper):
        movie = get_movie_payload(genre_id=unique_genre["id"])

        with allure.step("Запрос на создание фильма"):
            response = super_admin.api.movies_api.create_movie(movie).json()

        with allure.step("Проверка созданных полей"):
            assert response["name"] == movie["name"]
            assert response["description"] == movie["description"]
            assert response["price"] == movie["price"]
            assert response["location"] == movie["location"]
            assert response["imageUrl"] == movie["imageUrl"]
            assert response["published"] == movie["published"]
            assert response["genreId"] == movie["genreId"]

        with allure.step("Проверка соответствия данных из ответа API данным из бд"):
            movie_in_db = db_helper.get_movie_by_id(response["id"])
            assert movie_in_db is not None
            assert movie_in_db.id == response["id"]
            assert movie_in_db.name == response["name"]
            assert movie_in_db.price == response["price"]
            assert movie_in_db.genre_id == response["genreId"]
            assert movie_in_db.location == response["location"]

        with allure.step("Проверка созданного фильма"):
            get_response = super_admin.api.movies_api.get_movie(response["id"]).json()
            assert get_response["id"] == response["id"]
            assert get_response["name"] == movie["name"]

    @allure.story("Создание фильма")
    def test_create_movie_unauthorized(self, api_manager, unique_genre):
        with allure.step("Запрос на создание фильма без авторизации"):
            response = api_manager.movies_api.create_movie(
                    get_movie_payload(genre_id=unique_genre["id"]),
                    expected_status=401
                )
            response_data = response.json()
           
        with allure.step("Проверка текста ошибки"):
            assert response_data["message"] == "Unauthorized"

    @allure.story("Создание фильма с существующим именем")
    def test_create_movie_with_existing_name(self, super_admin, created_movie, unique_genre):
        duplicate_movie = get_movie_payload(genre_id=unique_genre["id"])
        duplicate_movie["name"] = created_movie["name"]

        with allure.step("Создание фильма с уже существующим именем"):
            response = super_admin.api.movies_api.create_movie(
                duplicate_movie,
                expected_status=409
            )
            response_data = response.json()

        with allure.step("Проверка текста ошибки "):
            assert response_data["message"] == "Фильм с таким названием уже существует"

    @allure.story("Создание фильма без нужных прав")
    def test_create_movie_common_user(self, common_user, unique_genre):
        movie = get_movie_payload(genre_id=unique_genre["id"])

        with allure.step("Создание фильма пользователем без прав"):
           response = common_user.api.movies_api.create_movie(movie, expected_status=403)
           response_data = response.json()

        with allure.step("Проверка текста ошибки"):
            assert response_data["message"] == "Forbidden resource"

    @pytest.mark.smoke
    @allure.story("Обновление фильма")
    def test_update_movie(self, super_admin, created_movie, unique_genre, db_helper):
        updated_movie = get_movie_payload(genre_id=unique_genre["id"])

        with allure.step("Запрос на обновление фильма"):
            response = super_admin.api.movies_api.update_movie(
                created_movie["id"],
                updated_movie
            ).json()

        with allure.step("Проверка обновленных полей"):
            assert response["id"] == created_movie["id"]
            assert response["name"] == updated_movie["name"]

        with allure.step("Проверка соответствия данных из ответа API данным из бд"):
            movie_in_db = db_helper.get_movie_by_id(response["id"])
            assert movie_in_db is not None
            assert movie_in_db.id == response["id"]
            assert movie_in_db.name == response["name"]
            assert movie_in_db.price == response["price"]
            assert movie_in_db.genre_id == response["genreId"]
            assert movie_in_db.location == response["location"]

        with allure.step("Проверка обновления"):
            get_response = super_admin.api.movies_api.get_movie(created_movie["id"]).json()
            assert get_response["id"] == created_movie["id"]
            assert get_response["name"] == updated_movie["name"]

    @allure.story("Обновление фильма")
    def test_update_movie_invalid_price(self, super_admin, created_movie):
        with allure.step("Запрос на обновление с невалидной ценой"):
            response = super_admin.api.movies_api.update_movie(
                created_movie["id"],
                {"price": -100},
                expected_status=400
            )
            response_data = response.json()

        with allure.step("Проверка текста ошибки"):
            assert response_data["message"][0] == "price must not be less than 1"

    @allure.story("Обновление фильма")
    def test_update_movie_not_found(self, super_admin, unique_genre):
        with allure.step("Запрос на обновление несуществующего фильма"):
            response = super_admin.api.movies_api.update_movie(
                movie_id=99999,
                movie_data=get_movie_payload(unique_genre["id"]),
                expected_status=404
            )
            response_data = response.json()

        with allure.step("Проверка текста ошибки"):
            assert response_data["message"] == "Фильм не найден"

    @allure.story("Обновление фильма")
    def test_update_movie_unauthorized(self, api_manager, created_movie, unique_genre):
        with allure.step("Запрос на обновление без авторизации"):
            response = api_manager.movies_api.update_movie(
                created_movie["id"],
                get_movie_payload(unique_genre["id"]),
                expected_status=401
            )
            response_data = response.json()

        with allure.step("Проверка текста ошибки"):
            assert response_data["message"] == "Unauthorized"

    @pytest.mark.smoke
    @allure.story("Удаление фильма")
    @pytest.mark.parametrize("created_movie", [False], indirect=True)
    def test_delete_movie(self, super_admin, created_movie, db_helper): 
        with allure.step("Запрос на удаление фильма"):
            super_admin.api.movies_api.delete_movie(created_movie["id"], expected_status=200)
        with allure.step("Проверка что фильм удален"):
            super_admin.api.movies_api.get_movie(created_movie["id"], expected_status=404)

        with allure.step("Проверка что фильм удален из бд"): 
            deleted_movie_in_db = db_helper.get_movie_by_id(created_movie["id"])
            assert deleted_movie_in_db is None

    @allure.story("Удаление фильма")
    def test_delete_movie_not_found(self, super_admin):
        with allure.step("Запрос на удаление несуществующего фильма"):
            response = super_admin.api.movies_api.delete_movie(movie_id=99999, expected_status=404)
            response_data = response.json()

        with allure.step("Проверка текста ошибки"):
            assert response_data["message"] == "Фильм не найден"

    @allure.story("Удаление фильма с ролью супер админа")
    @pytest.mark.parametrize("created_movie", [False], indirect=True)
    def test_delete_movie_super_admin(self, super_admin, created_movie, db_helper):
        with allure.step("Удаление фильма супер админом"):
            super_admin.api.movies_api.delete_movie(created_movie["id"], expected_status=200)

        with allure.step("Проверка, что фильм удалён из бд"):
            assert db_helper.get_movie_by_id(created_movie["id"]) is None

    @allure.story("Удаление фильма с ролью админа")
    def test_delete_movie_admin(self, admin_user, created_movie, db_helper):
        with allure.step("Попытка удаления админом без прав"):
            admin_user.api.movies_api.delete_movie(created_movie["id"], expected_status=403)

        with allure.step("Проверка, что фильм остался в бд"):
            assert db_helper.get_movie_by_id(created_movie["id"]) is not None

    @allure.story("Удаление фильма с ролью юзера")
    def test_delete_movie_common_user(self, common_user, created_movie, db_helper):
        with allure.step("Попытка удаления обычным пользователем"):
            common_user.api.movies_api.delete_movie(created_movie["id"], expected_status=403)

        with allure.step("Проверка, что фильм остался в бд"):
            assert db_helper.get_movie_by_id(created_movie["id"]) is not None

@allure.epic("Cinescope")
@allure.feature("Movies DB")
class TestMoviesDB:

    @pytest.mark.db
    @allure.story("Создание и удаление фильма")
    def test_movie_in_db(self, super_admin, unique_genre, db_helper):
      with allure.step("Создание фильма через API"): 
          movie_data = get_movie_payload(genre_id=unique_genre["id"])
          response = super_admin.api.movies_api.create_movie(movie_data).json()
          movie_id = response["id"]

      with allure.step("Проверка что фильм появился в бд"):
          movie_in_db = db_helper.get_movie_by_id(movie_id)
          assert movie_in_db is not None

      with allure.step("Удаление фильма через API"):
          super_admin.api.movies_api.delete_movie(movie_id)

      with allure.step("Проверка что фильм удален из бд"):
          deleted_movie_in_db = db_helper.get_movie_by_id(movie_id)
          assert deleted_movie_in_db is None

    @pytest.mark.db
    @allure.story("Удаление фильма из бд")
    def test_delete_movie_in_db(self, super_admin, db_session, db_helper, unique_genre):
        with allure.step("Создание тестового фильма напрямую в БД"):
            test_movie = MovieDBModel(
                name=f"Test movie for delete {uuid.uuid4()}",
                price=100,
                description="test",
                image_url="https://image.url",
                location="MSK",
                published=True,
                rating=0,
                genre_id=unique_genre["id"],
                created_at=datetime.now()
            )
            db_session.add(test_movie)
            db_session.commit()
            db_session.refresh(test_movie)

        with allure.step("Удаление фильма через API"):
            delete_response = super_admin.api.movies_api.delete_movie(test_movie.id)
            assert delete_response.status_code == 200, "Фильм должен успешно удалиться"

        with allure.step("Проверка отсутствия фильма в БД"):
            deleted_movie_in_db = db_helper.get_movie_by_id(test_movie.id)
            assert deleted_movie_in_db is None, "Фильм не должен существовать после удаления"