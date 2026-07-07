from faker import Faker 
import random
import string

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