import pywbem
from pywbem import CIMInstance


# Define connection parameters
hostname = "192.168.43.43"
username = "root"
password = "pass"
namespace = "root/cimv2"  # The base namespace for VMware-related namespaces

# Connect to the WBEM server on ESXi
connection = pywbem.WBEMConnection(
    f"https://{hostname}:5989",
    (username, password),
    default_namespace=namespace,
    no_verification=True,
)


def list_namespaces(conn, namespace="root"):
    """
    Recursively list all namespaces starting from the given namespace.
    """
    print(f"Namespaces under '{namespace}':")
    try:
        # Enumerate instances of __Namespace class in the current namespace
        namespaces = conn.EnumerateInstances("__Namespace", namespace=namespace)
        for ns in namespaces:
            ns_name = ns["Name"]
            print(f" - {ns_name}")
            # Recursively list namespaces under the current namespace
            list_namespaces(conn, namespace=f"{namespace}/{ns_name}")
    except ValueError as e:
        # Handle cases where the namespace does not exist or is inaccessible
        print(f"Error accessing namespace '{namespace}': {e}")


try:
    list_namespaces(connection)
except Exception as e:
    print("Failed to connect to ESXi host:", str(e))

# exit(0)

# Test connection by querying for the ESXi host's name
try:
    classnames = connection.EnumerateClassNames(namespace="root/cimv2")
    print(f"classnames of root/cimv2:")
    for c in classnames:
        print(c)
    print()
    classnames = connection.EnumerateClassNames(namespace="root/interop")
    print(f"classnames of root/interop:")
    for c in classnames:
        print(c)
    print()
    hosts = connection.EnumerateInstances("CIM_ComputerSystem", namespace="root/cimv2")
    for host in hosts:
        print(host.keys())
        print(host["RequestedState"])
except Exception as e:
    print("Failed to connect to ESXi host:", str(e))

exit(0)

vm_name = "MyNewVM"
memory_mb = 1024  # Memory in MB
num_cpus = 1  # Number of CPUs
disk_size_gb = 5  # Disk size in GB

vm_config = {
    "InstanceID": vm_name,
    "ElementName": vm_name,
    "VirtualSystemType": "vmx-07",  # VMware virtual hardware version
    "MemoryMB": memory_mb,
    "NumCPUs": num_cpus,
    "DiskSizeGB": disk_size_gb,
}

try:
    # result = connection.InvokeMethod(
    #     "CreateVirtualMachine", "VMware_VirtualMachineCreationService", vm_config
    # )
    connection.CreateInstance(CIMInstance(classname=class_name, properties=properties))
    print("VM created successfully:", result)
except Exception as e:
    print("Failed to create VM:", str(e))
