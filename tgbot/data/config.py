from environs import Env

env = Env()
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN")
ADMINS = env.list("ADMINS")
BASE_URL = env.str("BASE_URL")

USE_REDIS = env.str("USE_REDIS")
REDIS_PASSWORD = env.str("REDIS_PASSWORD")
REDIS_PORT = env.str("REDIS_PORT")
REDIS_HOST = env.str("REDIS_HOST")