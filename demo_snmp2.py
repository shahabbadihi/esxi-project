from pysnmp.hlapi.asyncio import *
import asyncio

# SNMP Configuration
SNMP_HOST = "192.168.43.43"
SNMP_PORT = 161
SNMP_COMMUNITY = "public"

# OIDs for CPU and Memory
CPU_LOAD_OID = "1.3.6.1.4.1.2021.10.1.3.1"  # 1-minute load
MEM_TOTAL_OID = "1.3.6.1.4.1.2021.4.5.0"  # Total RAM in KB
MEM_USED_OID = "1.3.6.1.4.1.2021.4.6.0"  # Used RAM in KB


# Async function to fetch SNMP values
async def get_snmp_value(oid):
    iterator = get_cmd(
        SnmpEngine(),
        CommunityData(SNMP_COMMUNITY, mpModel=1),
        await UdpTransportTarget.create((SNMP_HOST, SNMP_PORT)),
        ContextData(),
        ObjectType(ObjectIdentity(oid)),
    )

    error_indication, error_status, _, var_binds = await iterator

    if error_indication:
        print(f"Error: {error_indication}")
        return None
    elif error_status:
        print(f"Error Status: {error_status}")
        return None
    else:
        for var_bind in var_binds:
            return str(var_bind[1])  # Return SNMP value


# Monitor CPU and Memory Usage
async def monitor_resources():
    while True:
        cpu_load = await get_snmp_value(CPU_LOAD_OID)
        print(f"cpu_load: {cpu_load}")
        mem_total = await get_snmp_value(MEM_TOTAL_OID)
        print(f"mem_total: {mem_total}")
        mem_used = await get_snmp_value(MEM_USED_OID)
        print(f"mem_used: {mem_used}")

        if cpu_load and mem_total and mem_used:
            mem_total_mb = int(mem_total) // 1024
            mem_used_mb = int(mem_used) // 1024
            mem_usage_percent = (mem_used_mb / mem_total_mb) * 100

            print(f"CPU Load: {cpu_load}%")
            print(
                f"Memory Usage: {mem_used_mb} MB / {mem_total_mb} MB ({mem_usage_percent:.2f}%)"
            )
            print("-" * 40)

        await asyncio.sleep(10)  # Monitor every 10 seconds


# Run the monitor
asyncio.run(monitor_resources())
