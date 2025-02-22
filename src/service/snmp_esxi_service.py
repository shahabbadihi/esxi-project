import asyncio
import time
from collections import defaultdict
from typing import List, Tuple, Dict, Any

from client import SNMPTrapClient, SNMPRequestClient
from config import snmp_config
from utils.logger import setup_logger

logger = setup_logger(__name__)


class SNMPESXiService:

    def __init__(self):
        self._trap_host = snmp_config.trap_receiver_ip
        self._trap_port = snmp_config.trap_receiver_port
        self._community_str = snmp_config.trap_receiver_community_name
        self._community_index = snmp_config.trap_receiver_community_index
        self.trap_client = None
        self._esxi_host = snmp_config.agent_ip
        self._esxi_snmp_port = snmp_config.agent_port
        self._req_community_str = snmp_config.request_community_name
        self._snmp_version = snmp_config.version

    def _handle_monitoring_vm_power_off_on_trap(self, var_binds):
        logger.info("Handling SNMP monitor VM power off/on trap:")
        try:
            var_bind_dict = {str(name): val.prettyPrint() for name, val in var_binds}
            if not any(
                [k.startswith(snmp_config.vm_display_name_oid) for k in var_bind_dict]
            ):
                return
            vm_name = var_bind_dict[
                next(
                    k
                    for k in var_bind_dict
                    if k.startswith(snmp_config.vm_display_name_oid)
                )
            ]
            uptime_seconds = int(var_bind_dict[snmp_config.uptime_oid]) / 100
            if (
                var_bind_dict[snmp_config.trap_type_oid]
                == snmp_config.vm_power_on_trap_oid
            ):
                print(
                    f"VM with name {vm_name} is now powered on at uptime {uptime_seconds} secs."
                )
            elif (
                var_bind_dict[snmp_config.trap_type_oid]
                == snmp_config.vm_power_off_trap_oid
            ):
                print(
                    f"VM with name {vm_name} is now powered off at uptime {uptime_seconds} secs."
                )
        except Exception as e:
            raise Exception(
                f"An error occurred while monitoring vm power off/on, Error: {str(e)}"
            )

    def start_monitoring_vm_power_off_on(self):
        with SNMPTrapClient(
            trap_receiver_host=self._trap_host,
            trap_receiver_port=self._trap_port,
            community_str=self._community_str,
            community_index=self._community_index,
            trap_callback_func=self._handle_monitoring_vm_power_off_on_trap,
        ) as self.trap_client:
            logger.info(
                f"SNMP trap listener started on {self._trap_host}:{self._trap_port}."
            )
            while True:
                time.sleep(1)

    def list_all_vms(self) -> List[Dict[str, Any]]:
        req_client = SNMPRequestClient(
            host=self._esxi_host,
            port=self._esxi_snmp_port,
            community=self._req_community_str,
            version=self._snmp_version,
        )
        vm_info: List[Tuple] = asyncio.run(req_client.walk(snmp_config.vm_entry_oid))
        vms_var_bind_dict: Dict[str, List] = defaultdict(list)
        for oid, val in vm_info:
            if oid.startswith(snmp_config.vm_uuid_oid):
                vms_var_bind_dict["VM UUID"].append(val)
            elif oid.startswith(snmp_config.vm_display_name_oid):
                vms_var_bind_dict["VM Display Name"].append(val)
            elif oid.startswith(snmp_config.vm_config_file_oid):
                vms_var_bind_dict["VM Config File"].append(val)
            elif oid.startswith(snmp_config.vm_mem_size_oid):
                vms_var_bind_dict["VM Memory Size"].append(val)
            elif oid.startswith(snmp_config.vm_state_oid):
                vms_var_bind_dict["VM state"].append(val)
            elif oid.startswith(snmp_config.vm_cpu_cores_oid):
                vms_var_bind_dict["VM CPU cores"].append(val)

        return [
            dict(zip(vms_var_bind_dict.keys(), values))
            for values in zip(*vms_var_bind_dict.values())
        ]
