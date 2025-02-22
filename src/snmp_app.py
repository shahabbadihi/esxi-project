from typing import List, Tuple, Dict, Any

from service import SNMPESXiService


from utils.logger import setup_logger

logger = setup_logger(__name__)


class SNMPManagerApp:

    def __init__(self):
        self._snmp_esxi_vm_service: SNMPESXiService = SNMPESXiService()

    def start(self):
        while True:
            self._display_init()

            option: int = self._wait_for_user_select_option()
            if option == 1:
                self._enter_monitor_vm_on_off_operation()
            elif option == 2:
                self._enter_view_all_vms_info()
            elif option == 3:
                print("Exiting ...")
                exit()

    @staticmethod
    def _display_init():
        print("Welcome to SNMP-based ESXi manager app!")
        print()
        print(
            "Please select one of these options, by just typing a number then press enter."
        )
        print(
            """
        1) Monitor VM on/off
        2) View all VMs info
        3) Exit
        """
        )

    @staticmethod
    def _wait_for_user_select_option() -> int:
        while True:
            user_input: str = input("Please enter a number of option: ")
            if user_input.isdigit() and (1 <= int(user_input) <= 3):
                return int(user_input)
            print("Invalid input! Please enter just a number of option.")

    def _enter_monitor_vm_on_off_operation(self):
        print("Now monitoring any VM powered on/off on ESXi server ...")
        print("You can press ctrl + C to back to main menu.")
        print()
        try:
            self._snmp_esxi_vm_service.start_monitoring_vm_power_off_on()
        except KeyboardInterrupt:
            logger.info("Shutting down monitoring...")

    def _enter_view_all_vms_info(self):
        try:
            vm_infos: List[Dict[str, Any]] = self._snmp_esxi_vm_service.list_all_vms()
            for info in vm_infos:
                for oid, val in info.items():
                    print(f"{oid} -> {val}")
                print("-" * 100)
        except Exception as e:
            logger.error(f"Error occurred while view all vms info: {str(e)}")


if __name__ == "__main__":
    app = SNMPManagerApp()
    app.start()
