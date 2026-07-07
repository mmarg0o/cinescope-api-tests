from data.movies.movie_data import get_movie_payload

class TestMovies:
    def test_get_movies(self, api_manager):
        response = api_manager.movies_api.get_movies()
        response_data = response.json()

        assert isinstance(response_data["movies"], list)
        assert "count" in response_data
        assert "page" in response_data
        assert "pageSize" in response_data
        assert "pageCount" in response_data

    def test_get_movies_filter_by_genre(self, api_manager, created_movie):
        response = api_manager.movies_api.get_movies(params={"genreId": created_movie["genreId"]})
        response_data = response.json()

        assert len(response_data["movies"]) > 0
        assert all(movie["genreId"] == created_movie["genreId"] for movie in response_data["movies"])

    def test_get_movies_invalid_page(self, api_manager):
        api_manager.movies_api.get_movies(params = {"page": -1}, expected_status=400)

    def test_get_movie(self, api_manager, created_movie):
        response = api_manager.movies_api.get_movie(created_movie["id"])
        response_data = response.json()

        assert response_data["id"] == created_movie["id"]
        assert response_data["name"] == created_movie["name"]

    def test_get_movie_not_found(self, api_manager):
        api_manager.movies_api.get_movie(movie_id=99999, expected_status=404)

    def test_update_movie(self, super_admin_api_manager, created_movie):
        updated_movie = get_movie_payload()

        response = super_admin_api_manager.movies_api.update_movie(
            created_movie["id"],
            updated_movie
        ).json()

        assert response["id"] == created_movie["id"]
        assert response["name"] == updated_movie["name"]

    def test_update_movie_invalid_price(self, super_admin_api_manager, created_movie):
        super_admin_api_manager.movies_api.update_movie(
            created_movie["id"],
            {"price": -100},
            expected_status=400
        )
           
    def test_update_movie_not_found(self, super_admin_api_manager):
        super_admin_api_manager.movies_api.update_movie(
            movie_id=99999,
            movie_data=get_movie_payload(),
            expected_status=404
        )

    def test_delete_movie(self, super_admin_api_manager, created_movie):
        super_admin_api_manager.movies_api.delete_movie(created_movie["id"], expected_status=200)
        super_admin_api_manager.movies_api.get_movie(created_movie["id"], expected_status=404)

    def test_delete_movie_not_found(self, super_admin_api_manager):
        super_admin_api_manager.movies_api.delete_movie(movie_id=99999, expected_status=404)