from pydantic_settings import BaseSettings


class SNMPConfig(BaseSettings):
    trap_receiver_community_name: str
    trap_receiver_community_index: str
    trap_receiver_ip: str
    trap_receiver_port: int

    uptime_oid: str
    trap_type_oid: str
    vm_power_on_trap_oid: str
    vm_power_off_trap_oid: str
    vm_display_name_oid: str

    class Config:
        env_prefix = "SNMP_"
        env_file = ".env"


snmp_config = SNMPConfig()
