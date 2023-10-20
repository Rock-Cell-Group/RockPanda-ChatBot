from dotenv import load_dotenv
from os import environ

load_dotenv()

flask_env = environ.get("FLASK_ENV")

"""
之後要區分開發環境，可以從這裡控制flask app的環境變數
"""


class BaseConfig(object):
    CONFIG_TYPE = "BaseConfig"
    PINECONE_API_KEY = environ.get("PINECONE_API_KEY")  # 從.env來的
    PINECONE_ENV = environ.get("PINECONE_ENV")
    OPENAI_API_KEY = environ.get("OPENAI_API_KEY")
    # sqlalchemy_database
    DATABASE_URL = environ.get("LOCAL_DATABASE_URL")
    # Linebot
    CHANNEL_ACCESS_TOKEN = environ.get("CHANNEL_ACCESS_TOKEN")
    CHANNEL_SECRET = environ.get("CHANNEL_SECRET")
    # openai
    OPENAI_API_KEY = environ.get("OPENAI_API_KEY")
    # redis
    REDIS_URL = environ.get("REDIS_URL")


class PrdConfig(object):
    CONFIG_TYPE = "PrdConfig"
    PINECONE_API_KEY = environ.get("PINECONE_API_KEY")  # 從.env來的
    PINECONE_ENV = environ.get("PINECONE_ENV")
    OPENAI_API_KEY = environ.get("OPENAI_API_KEY")
    # sqlalchemy_database
    DATABASE_URL = environ.get("PROD_DATABASE_URL")
    # Linebot
    CHANNEL_ACCESS_TOKEN = environ.get("CHANNEL_ACCESS_TOKEN")
    CHANNEL_SECRET = environ.get("CHANNEL_SECRET")
    # openai
    OPENAI_API_KEY = environ.get("OPENAI_API_KEY")
    # redis
    REDIS_URL = environ.get("REDIS_URL")


def get_config_by_flask_env():
    configs = {
        None: BaseConfig,  # 預設不寫FLASK_ENV的話就是BaseConfig
        "production": PrdConfig,
    }
    _env = environ.get("FASTAPI_ENV")
    return configs.get(_env)()


settings = get_config_by_flask_env()
