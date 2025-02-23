from client import VmomiClient
from schemas import CreateVMSchema
from config import esxi_config
from utils.logger import setup_logger

logger = setup_logger(__name__)


class VmomiESXiService:

    def __init__(self):
        self._ip = esxi_config.ip
        self._hostname = esxi_config.hostname
        self._username = esxi_config.username
        self._password = esxi_config.password

    def create_vm(
        self,
        vm_name,
        memory_mb,
        num_cpus,
        disk_size_gb,
        guest_id,
    ):
        with VmomiClient(
            host=self._ip,
            hostname=self._hostname,
            username=self._username,
            pwd=self._password,
        ) as client:
            client.create_vm(
                CreateVMSchema(
                    vm_name=vm_name,
                    memory_mb=memory_mb,
                    num_cpus=num_cpus,
                    disk_size_gb=disk_size_gb,
                    datastore_name="datastore1",
                    network_name="VM Network",
                    guest_id=guest_id,
                )
            )
