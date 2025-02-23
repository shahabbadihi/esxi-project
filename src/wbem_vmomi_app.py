from typing import Dict, List

from service import WBEMESXiService, VmomiESXiService

from utils.logger import setup_logger

logger = setup_logger(__name__)


class WBEMVmomiManagerApp:

    def __init__(self):
        self._wbem_esxi_service: WBEMESXiService = WBEMESXiService()
        self._vmomi_service: VmomiESXiService = VmomiESXiService()

    def start(self):
        while True:
            self._display_init()
            option: int = self._wait_for_user_select_option()
            if option == 1:
                self._enter_display_info_operation()
            elif option == 2:
                self._enter_create_vm_operation()
            elif option == 3:
                self._enter_monitor_logs_operation()
            elif option == 4:
                print("Exiting ...")
                exit()

    @staticmethod
    def _display_init():
        print("Welcome to WBEM+Vmomi based ESXi VM manager app!")
        print()
        print(
            "Please select one of these options, by just typing a number then press enter."
        )
        print(
            """
        1) Display ESXi System info
        2) Create VM
        3) Monitor Logs
        4) Exit
        """
        )

    @staticmethod
    def _wait_for_user_select_option() -> int:
        while True:
            user_input: str = input("Please enter a number of option: ")
            if user_input.isdigit() and (1 <= int(user_input) <= 4):
                return int(user_input)
            print("Invalid input! Please enter just a number of option.")

    def _enter_display_info_operation(self):
        system_info: List[Dict] = self._wbem_esxi_service.get_info_about_system()
        for info in system_info:
            for key, val in info.items():
                print(f"{key}: {val}")
            print("-" * 100)

    def _enter_create_vm_operation(self):
        vm_name: str = input("Please enter VM name you want to create: ")
        while True:
            vm_memory_size_in_mbs_str: str = input(
                "Please enter VM memory size (in MBs): "
            )
            if vm_memory_size_in_mbs_str.isdigit():
                vm_memory_size_in_mbs: int = int(vm_memory_size_in_mbs_str)
                break
            else:
                print("VM memory size must be just an integer in MBs.")
        while True:
            vm_cpu_count_str: str = input("Please enter VM CPU cores count: ")
            if vm_cpu_count_str.isdigit():
                vm_cpu_count: int = int(vm_cpu_count_str)
                break
            else:
                print("VM CPU core count must be just an integer.")
        while True:
            vm_disk_size_gb_str: str = input(
                "Please enter VM disk storage size (in GBs): "
            )
            if vm_disk_size_gb_str.isdigit():
                vm_disk_size_gb: int = int(vm_disk_size_gb_str)
                break
            else:
                print("VM disk size must be just an integer.")
        while True:
            print(
                "Please select one of these options for guest OS, by just typing a number then press enter."
            )
            print(
                """
            1) windows9_64Guest
            2) ubuntu64Guest
            3) rhel8_64Guest
            4) darwin18_64Guest
            """
            )
            os_option_str: str = input()
            if os_option_str.isdigit() and 1 <= int(os_option_str) <= 4:
                if os_option_str == "1":
                    guest_os = "windows9_64Guest"
                elif os_option_str == "2":
                    guest_os = "ubuntu64Guest"
                elif os_option_str == "3":
                    guest_os = "rhel8_64Guest"
                elif os_option_str == "4":
                    guest_os = "darwin18_64Guest"
                else:
                    raise ValueError("Option not correct!")
                break
            else:
                print("You should just type a number of options for OS!")

        print("Creating VM ...")
        self._vmomi_service.create_vm(
            vm_name=vm_name,
            memory_mb=vm_memory_size_in_mbs,
            num_cpus=vm_cpu_count,
            disk_size_gb=vm_disk_size_gb,
            guest_id=guest_os,
        )
        print(
            f"VM with name: '{vm_name}',"
            f" memory size: {vm_memory_size_in_mbs} MB, CPU cores: {vm_cpu_count} "
            f", disk size: {vm_disk_size_gb} GB, with guest os: {guest_os}"
            f"has been successfully created."
        )

    def _enter_monitor_logs_operation(self):
        print("Now monitoring logs of ESXi server that upadated each 5s ...")
        print("You can press ctrl + C to back to main menu.")
        print()
        try:
            self._vmomi_service.start_monitoring_logs()
        except KeyboardInterrupt:
            logger.info("Monitoring logs finished")
        except Exception as e:
            logger.error(f"Error occurred while monitoring logs: {str(e)}")


if __name__ == "__main__":
    app = WBEMVmomiManagerApp()
    app.start()
