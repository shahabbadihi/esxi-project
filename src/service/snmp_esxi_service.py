import time

from client import SNMPTrapClient
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

    def _handle_monitoring_vm_power_off_on_trap(self, var_binds):
        logger.info("Handling SNMP monitor VM power off/on trap:")
        try:
            var_bind_dict = {str(name): val.prettyPrint() for name, val in var_binds}
            if snmp_config.vm_display_name_oid not in var_bind_dict:
                return
            vm_name = var_bind_dict[snmp_config.vm_display_name_oid]
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
