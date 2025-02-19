from typing import List, Dict

import pywbem

from config import esxi_config
from client import WBEMClient


class WBEMESXiVMService:

    def __init__(self):
        self.esxi_host = esxi_config.host
        self.esxi_username = esxi_config.username
        self.esxi_password = esxi_config.password
        self.esxi_computer_system_class_name = esxi_config.computer_system_class_name
        self.esxi_vm_namespace = esxi_config.vm_namespace

    def enumerate_vms(self) -> List[Dict]:
        with WBEMClient(
            host=self.esxi_host,
            username=self.esxi_username,
            password=self.esxi_password,
        ) as client:
            vms_info: List[Dict] = client.enumerate_instances(
                class_name=self.esxi_computer_system_class_name
            )
            return vms_info

    def create_vm(self, vm_settings: Dict):
        with WBEMClient(
            host=self.esxi_host,
            username=self.esxi_username,
            password=self.esxi_password,
        ) as client:
            if not all(
                [key in vm_settings for key in ("Name", "MemorySize", "CPUCount")]
            ):
                raise ValueError(
                    "Properties [Name], [MemorySize], [CPUCount] are required in vm settings"
                )

            client.create_instance(
                class_name=self.esxi_computer_system_class_name,
                properties={
                    **vm_settings,
                    "MemorySize": pywbem.Uint32(
                        vm_settings["MemorySize"] * 1024 * 1024
                    ),
                    "CPUCount": pywbem.Uint16(vm_settings["CPUCount"]),
                    "CreationClassName": self.esxi_computer_system_class_name,
                },
                namespace=self.esxi_vm_namespace,
            )
