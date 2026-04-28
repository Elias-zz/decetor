import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'data', 'test.db')}"

SECRET_KEY = "sensitive_word_detect_secret_key_2024"

ACCESS_TOKEN_EXPIRE_MINUTES = 30

TEST_USERNAME = "admin"
TEST_PASSWORD = "123456"