from pydantic_settings import BaseSettings


class ESXiConfig(BaseSettings):
    host: str
    username: str
    password: str
    computer_system_class_name: str
    vm_namespace: str

    class Config:
        env_prefix = "ESXI_"
        env_file = ".env"


esxi_config = ESXiConfig()
