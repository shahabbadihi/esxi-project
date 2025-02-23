import time
from datetime import datetime

from schemas import CreateVMSchema

from pyVmomi import vim
from pyVim.connect import SmartConnect, Disconnect
import ssl


class VmomiClient:

    def __init__(self, host: str, hostname: str, username: str, pwd: str, port=443):
        self.host = host
        self.hostname = hostname
        self.username = username
        self.pwd = pwd
        self.port = port
        self.si = None

    def __enter__(self):
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        context.verify_mode = ssl.CERT_NONE

        self.si = SmartConnect(
            host=self.host,
            user=self.username,
            pwd=self.pwd,
            port=self.port,
            sslContext=context,
        )

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.si:
            Disconnect(self.si)

    def create_vm(self, schema: CreateVMSchema):
        content = self.si.RetrieveContent()

        if schema.datacenter_name:
            datacenter = self.get_obj(content, [vim.Datacenter], schema.datacenter_name)
            if not datacenter:
                raise Exception(f"Datacenter '{schema.datacenter_name}' not found.")
            vm_folder = datacenter.vmFolder
        else:
            datacenter = content.rootFolder.childEntity[0]
            vm_folder = datacenter.vmFolder

        datastore = self.get_obj(content, [vim.Datastore], schema.datastore_name)
        if not datastore:
            raise Exception(f"Datastore '{schema.datastore_name}' not found.")

        resource_pool = self.get_obj(content, [vim.ResourcePool], "Resources")
        if not resource_pool:
            raise Exception(f"Resource pool 'Resources' not found.")

        network = self.get_obj(content, [vim.Network], schema.network_name)
        if not network:
            raise Exception(f"Network '{schema.network_name}' not found.")

        scsi_spec = vim.vm.device.VirtualDeviceSpec()
        scsi_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.add
        scsi_spec.device = vim.vm.device.ParaVirtualSCSIController()
        scsi_spec.device.key = 1000
        scsi_spec.device.sharedBus = (
            vim.vm.device.VirtualSCSIController.Sharing.noSharing
        )

        disk_size_kb = int(schema.disk_size_gb) * 1024 * 1024
        disk_spec = vim.vm.device.VirtualDeviceSpec()
        disk_spec.fileOperation = "create"
        disk_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.add
        disk_spec.device = vim.vm.device.VirtualDisk()
        disk_spec.device.backing = vim.vm.device.VirtualDisk.FlatVer2BackingInfo()
        disk_spec.device.backing.diskMode = "persistent"
        disk_spec.device.backing.fileName = (
            f"[{schema.datastore_name}] {schema.vm_name}/{schema.vm_name}.vmdk"
        )
        disk_spec.device.backing.thinProvisioned = True
        disk_spec.device.capacityInKB = disk_size_kb
        disk_spec.device.unitNumber = 0
        disk_spec.device.controllerKey = scsi_spec.device.key

        nic_spec = vim.vm.device.VirtualDeviceSpec()
        nic_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.add
        nic_spec.device = vim.vm.device.VirtualVmxnet3()
        nic_spec.device.backing = vim.vm.device.VirtualEthernetCard.NetworkBackingInfo()
        nic_spec.device.backing.network = network
        nic_spec.device.backing.deviceName = schema.network_name
        nic_spec.device.connectable = vim.vm.device.VirtualDevice.ConnectInfo()
        nic_spec.device.connectable.startConnected = True
        nic_spec.device.connectable.allowGuestControl = True
        nic_spec.device.connectable.connected = True
        nic_spec.device.deviceInfo = vim.Description()
        nic_spec.device.deviceInfo.summary = "vNetwork"

        vm_config_spec = vim.vm.ConfigSpec()
        vm_config_spec.name = schema.vm_name
        vm_config_spec.memoryMB = int(schema.memory_mb)
        vm_config_spec.numCPUs = int(schema.num_cpus)
        vm_config_spec.guestId = schema.guest_id
        vm_config_spec.deviceChange = [scsi_spec, disk_spec, nic_spec]
        vm_config_spec.files = vim.vm.FileInfo()
        vm_config_spec.files.vmPathName = f"[{schema.datastore_name}]"

        try:
            task = vm_folder.CreateVM_Task(config=vm_config_spec, pool=resource_pool)
            self.wait_for_task(task)
        except Exception as e:
            raise Exception(f"VM creation failed: {str(e)}")

    @staticmethod
    def get_obj(content, vimtype, name):
        obj = None
        container = content.viewManager.CreateContainerView(
            content.rootFolder, vimtype, True
        )
        for item in container.view:
            if item.name == name:
                obj = item
                break
        return obj

    @staticmethod
    def wait_for_task(task):
        while task.info.state not in [
            vim.TaskInfo.State.success,
            vim.TaskInfo.State.error,
        ]:
            pass
        if task.info.state == vim.TaskInfo.State.error:
            raise Exception(f"Task failed: {task.info.error}")

    def monitor_real_time_logs(self, interval=5):
        event_manager = self.si.content.eventManager
        filter_spec = vim.event.EventFilterSpec()

        event_handler = event_manager.CreateCollectorForEvents(filter_spec)

        while True:
            events = event_handler.ReadNextEvents(10)
            if events:
                for event in events:
                    timestamp = event.createdTime
                    formatted_timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")

                    print(
                        f"[{formatted_timestamp}] System Event: {event.fullFormattedMessage}"
                    )
            time.sleep(interval)
