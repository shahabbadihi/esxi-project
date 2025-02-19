from pydantic_settings import BaseSettings


class BasicConfig(BaseSettings):
    stream_log: bool = False

    class Config:
        env_file = ".env"


basic_config = BasicConfig()
