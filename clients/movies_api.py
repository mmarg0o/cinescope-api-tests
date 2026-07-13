from config.base_urls import MOVIES_BASE_URL
from custom_requester.custom_requester import CustomRequester

class MoviesApi(CustomRequester):
    def __init__(self, session):
        super().__init__(session=session, base_url=MOVIES_BASE_URL)
        self.url = '/movies'

    def get_movies(self, params=None, expected_status=200, **kwargs):
        return self.send_request(
            method="GET",
            endpoint=self.url,
            params=params,
            expected_status=expected_status,
            **kwargs
        )
    
    def get_movie(self, movie_id, expected_status=200, **kwargs):
        return self.send_request(
            method="GET",
            endpoint=f"{self.url}/{movie_id}",
            expected_status=expected_status,
            **kwargs
        )
  
    def create_movie(self, movie_data, expected_status=201, **kwargs):
        return self.send_request(
            method="POST",
            endpoint=self.url,
            data=movie_data,
            expected_status=expected_status,
            **kwargs  
        )
    
    def update_movie(self, movie_id, movie_data, expected_status=200, **kwargs):
        return self.send_request(
            method="PATCH",
            endpoint=f"{self.url}/{movie_id}",
            data=movie_data,
            expected_status=expected_status,
            **kwargs
        )
    
    def delete_movie(self, movie_id, expected_status=200, **kwargs):
        return self.send_request(
            method="DELETE",
            endpoint=f"{self.url}/{movie_id}",
            expected_status=expected_status,
            **kwargs
        )
    
    def create_genre(self, genre_data, expected_status=201, **kwargs):
        return self.send_request(
            method="POST",
            endpoint="/genres",
            data=genre_data,
            expected_status=expected_status,
            **kwargs
        )

    def delete_genre(self, genre_id, expected_status=200, **kwargs):
        return self.send_request(
            method="DELETE",
            endpoint=f"/genres/{genre_id}",
            expected_status=expected_status,
            **kwargs
        )