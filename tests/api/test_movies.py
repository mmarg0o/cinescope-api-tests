from data.movies.movie_data import get_movie_payload

class TestMovies:
    def test_get_movies(self, api_manager):
        response = api_manager.movies_api.get_movies()
        response_data = response.json()

        assert isinstance(response_data["movies"], list)
        assert isinstance(response_data["count"], int)
        assert isinstance(response_data["page"], int)
        assert isinstance(response_data["pageSize"], int)
        assert isinstance(response_data["pageCount"], int)

    def test_get_movies_filter_by_genre(self, api_manager, created_movie):
        response = api_manager.movies_api.get_movies(params={"genreId": created_movie["genreId"]})
        response_data = response.json()

        assert len(response_data["movies"]) > 0
        assert all(movie["genreId"] == created_movie["genreId"] for movie in response_data["movies"])
        assert any(movie["id"] == created_movie["id"] for movie in response_data["movies"])
    
    def test_get_movies_filter_combination(self, api_manager, created_movie):
        response = api_manager.movies_api.get_movies(params={
            "genreId": created_movie["genreId"],
            "location": created_movie["location"]
        })
        response_data = response.json()

        assert len(response_data["movies"]) > 0
        assert any(movie["id"] == created_movie["id"] for movie in response_data["movies"])

    def test_get_movies_filter_by_price_range(self, api_manager, created_movie):
        min_price = created_movie["price"] - 10
        max_price = created_movie["price"] + 10

        response = api_manager.movies_api.get_movies(params={
            "minPrice": min_price,
            "maxPrice": max_price
        })
        response_data = response.json()

        assert len(response_data["movies"]) > 0
        assert all(min_price <= movie["price"] <= max_price for movie in response_data["movies"])

    def test_get_movies_invalid_page(self, api_manager):
        response = api_manager.movies_api.get_movies(params = {"page": -1}, expected_status=400)
        response_data = response.json()
        assert "message" in response_data
        assert "page" in response_data["message"][0]

    def test_get_movie(self, api_manager, created_movie):
        response = api_manager.movies_api.get_movie(created_movie["id"])
        response_data = response.json()

        assert response_data["id"] == created_movie["id"]
        assert response_data["name"] == created_movie["name"]

    def test_get_movie_not_found(self, api_manager):
        response = api_manager.movies_api.get_movie(movie_id=99999, expected_status=404)
        response_data = response.json()
        assert "message" in response_data
        assert "не найден" in response_data["message"]

    def test_create_movie(self, super_admin_api_manager):
        movie = get_movie_payload()

        response = super_admin_api_manager.movies_api.create_movie(movie).json()

        assert response["name"] == movie["name"]
        assert response["description"] == movie["description"]
        assert response["price"] == movie["price"]
        assert response["location"] == movie["location"]
        assert response["imageUrl"] == movie["imageUrl"]
        assert response["published"] == movie["published"]
        assert response["genreId"] == movie["genreId"]

        get_response = super_admin_api_manager.movies_api.get_movie(response["id"]).json()

        assert get_response["id"] == response["id"]
        assert get_response["name"] == movie["name"]

    def test_create_movie_unauthorized(self, api_manager):
        response = api_manager.movies_api.create_movie(
            get_movie_payload(),
            expected_status=401
        )
        response_data = response.json()
        assert "message" in response_data
        assert response_data["message"] == "Unauthorized"

    def test_create_movie_with_existing_name(self, super_admin_api_manager, created_movie):
        duplicate_movie = get_movie_payload()
        duplicate_movie["name"] = created_movie["name"]

        response = super_admin_api_manager.movies_api.create_movie(
            duplicate_movie,
            expected_status=409
        )
        response_data = response.json()
        assert "message" in response_data
        assert "уже существует" in response_data["message"]

    def test_update_movie(self, super_admin_api_manager, created_movie):
        updated_movie = get_movie_payload()

        response = super_admin_api_manager.movies_api.update_movie(
            created_movie["id"],
            updated_movie
        ).json()

        assert response["id"] == created_movie["id"]
        assert response["name"] == updated_movie["name"]

        get_response = super_admin_api_manager.movies_api.get_movie(created_movie["id"]).json()
        assert get_response["id"] == created_movie["id"]
        assert get_response["name"] == updated_movie["name"]

    def test_update_movie_invalid_price(self, super_admin_api_manager, created_movie):
        response = super_admin_api_manager.movies_api.update_movie(
                created_movie["id"],
                {"price": -100},
                expected_status=400
            )
        response_data = response.json()
        assert "message" in response_data
        assert "price" in response_data["message"][0]

    def test_update_movie_not_found(self, super_admin_api_manager):
        response = super_admin_api_manager.movies_api.update_movie(
                movie_id=99999,
                movie_data=get_movie_payload(),
                expected_status=404
            )
        response_data = response.json()
        assert "message" in response_data 
        assert "не найден" in response_data["message"]

    def test_update_movie_unauthorized(self, api_manager, created_movie):
        response = api_manager.movies_api.update_movie(
            created_movie["id"],
            get_movie_payload(),
            expected_status=401
        )
        response_data = response.json()
        assert "message" in response_data
        assert response_data["message"] == "Unauthorized"

    def test_delete_movie(self, super_admin_api_manager, created_movie_for_delete):
        super_admin_api_manager.movies_api.delete_movie(created_movie_for_delete["id"], expected_status=200)
        super_admin_api_manager.movies_api.get_movie(created_movie_for_delete["id"], expected_status=404)

    def test_delete_movie_not_found(self, super_admin_api_manager):
        response = super_admin_api_manager.movies_api.delete_movie(movie_id=99999, expected_status=404)
        response_data = response.json()
        assert "message" in response_data
        assert "не найден" in response_data["message"]