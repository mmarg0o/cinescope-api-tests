from config.base_urls import MOVIES_BASE_URL
from custom_requester.custom_requester import CustomRequester

GENRES = '/genres'

class GenresApi(CustomRequester):
    def __init__(self, session):
        super().__init__(session=session, base_url=MOVIES_BASE_URL)

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