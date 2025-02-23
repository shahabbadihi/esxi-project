from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
import ssl


class VmomiClient:
    def __init__(self, host, username, pwd, port=443):
        self.host = host
        self.username = username
        self.pwd = pwd
        self.port = port
        self.si = None

    def __enter__(self):
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        context.verify_mode = ssl.CERT_NONE

        # Connect to the ESXi host
        self.si = SmartConnect(
            host=self.host,
            user=self.username,
            pwd=self.pwd,
            port=self.port,
            sslContext=context,
        )

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.si:
            Disconnect(self.si)

    def list_all_hosts(self):
        content = self.si.RetrieveContent()
        # Create a container view from the root folder
        container = content.viewManager.CreateContainerView(
            content.rootFolder, [vim.HostSystem], True
        )

        # Iterate over the view and print out the host names
        for item in container.view:
            print(f"Found host: {item.name}")


# Usage
with VmomiClient(host="192.168.43.43", username="root", pwd="Sepahan55555&") as client:
    client.list_all_hosts()
