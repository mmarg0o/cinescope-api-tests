from faker import Faker 
import random
import string
import uuid
import datetime

fake = Faker()

class DataGenerator:

    @staticmethod
    def generate_random_name():
        return fake.first_name() + " " + fake.last_name()

    @staticmethod
    def generate_random_password():
        letters = random.choices(string.ascii_letters, k=6)
        digits = random.choices(string.digits, k=2)
        special = random.choices("?@#$%^&*_", k=2)
        all_chars = letters + digits + special
        random.shuffle(all_chars)
        return "".join(all_chars)
    
    @staticmethod
    def generate_random_email():
        return fake.email()
    
    @staticmethod
    def generate_random_movie_name():
        return f"{fake.sentence(nb_words=3)} {uuid.uuid4().hex[:8]}"
    
    @staticmethod
    def generate_random_image_url():
        return fake.image_url()
    
    @staticmethod
    def generate_random_price():
        return fake.random_int(min=100, max=1000)

    @staticmethod
    def generate_random_description():
        return fake.sentence()

    @staticmethod
    def generate_user_data() -> dict:
        from uuid import uuid4

        return {
            'id': f'{uuid4()}',
            'email': DataGenerator.generate_random_email(),
            'full_name': DataGenerator.generate_random_name(),
            'password': DataGenerator.generate_random_password(),
            'created_at': datetime.datetime.now(),
            'updated_at': datetime.datetime.now(),
            'verified': False,
            'banned': False,
            'roles': '{USER}'
        }

    @staticmethod
    def generate_random_int(max_value: int) -> int:
        return random.randint(1, max_value)