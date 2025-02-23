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
    vm_config_file_oid: str
    vm_mem_size_oid: str
    vm_state_oid: str
    vm_cpu_cores_oid: str
    vm_entry_oid: str
    vm_uuid_oid: str
    host_cpu_load_percentage_oid: str
    host_memory_type_oid: str
    host_memory_used_kb_oid: str
    host_memory_total_kb_oid: str
    agent_ip: str
    agent_port: int
    request_community_name: str
    version: int

    class Config:
        env_prefix = "SNMP_"
        env_file = ".env"


snmp_config = SNMPConfig()
