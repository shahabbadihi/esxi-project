from service import WBEMESXiVMService


class WBEMVMManagerApp:

    def __init__(self):
        self._wbem_esxi_vm_service: WBEMESXiVMService = WBEMESXiVMService()

    def start(self):
        self._display_init()
        while True:
            option: int = self._wait_for_user_select_option()
            if option == 1:
                self._enter_display_vms_operation()
            elif option == 2:
                self._enter_create_vm_operation()
            elif option == 3:
                print("Exiting ...")
                exit()

    @staticmethod
    def _display_init():
        print("Welcome to WBEM-based ESXi VM manager app!")
        print()
        print(
            "Please select one of these options, by just typing a number then press enter."
        )
        print(
            """
        1) Display VMs info
        2) Create VM
        """
        )

    @staticmethod
    def _wait_for_user_select_option() -> int:
        while True:
            user_input: str = input("Please enter a number of option: ")
            if user_input.isdigit() and (1 <= int(user_input) <= 3):
                return int(user_input)
            print("Invalid input! Please enter just a number of option.")

    def _enter_display_vms_operation(self):
        pass

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

        print("Creating VM ...")
        self._wbem_esxi_vm_service.create_vm(
            vm_settings={
                "Name": vm_name,
                "MemorySize": vm_memory_size_in_mbs,
                "CPUCount": vm_cpu_count,
            }
        )
        print(
            f"VM with name: '{vm_name}',"
            f" memory size: {vm_memory_size_in_mbs} MB, CPU cores: {vm_cpu_count} "
            f"has been successfully created."
        )


if __name__ == "__main__":
    app = WBEMVMManagerApp()
    app.start()
