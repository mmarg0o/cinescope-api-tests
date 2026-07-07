from faker import Faker 
import random
import string
import uuid

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
    def generate_random_movie_name(): #добавила uuid потому что faker генерит имена из ограниченного набора слов и из за этого иногда тесты падают с 409
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