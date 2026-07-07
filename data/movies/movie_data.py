from utils.data_generator import DataGenerator

def get_movie_payload(genre_id=4):
    return {
        "name": DataGenerator.generate_random_movie_name(),
        "imageUrl": DataGenerator.generate_random_image_url(),
        "price": DataGenerator.generate_random_price(),
        "description": DataGenerator.generate_random_description(),
        "published": True,
        "location": "MSK",
        "genreId": genre_id
    }