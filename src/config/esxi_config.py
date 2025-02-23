from pydantic_settings import BaseSettings


class ESXiConfig(BaseSettings):
    host: str
    ip: str
    hostname: str
    username: str
    password: str
    processor_cim_class_name: str
    processor_cim_namespace: str

    class Config:
        env_prefix = "ESXI_"
        env_file = ".env"


esxi_config = ESXiConfig()
