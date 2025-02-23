from pysnmp.hlapi.asyncio import *
import asyncio

# SNMP Configuration
SNMP_HOST = "192.168.43.43"
SNMP_PORT = 161
SNMP_COMMUNITY = "public"

# OIDs for CPU and Memory
CPU_LOAD_OID = "1.3.6.1.2.1.25.3.3.1.2"  # 1-minute load
MEM_TOTAL_OID = "1.3.6.1.2.1.25.2.3.1.5"  # Total RAM in KB
MEM_USED_OID = "1.3.6.1.2.1.25.2.3.1.6"  # Used RAM in KB


# Async function to fetch SNMP values
async def walk_next_value(oid):
    results = []
    original_oid = oid
    is_walk_finished = False
    snmp_engine = SnmpEngine()

    while True:
        error_indication, error_status, _, var_binds = await next_cmd(
            snmp_engine,
            CommunityData(SNMP_COMMUNITY, mpModel=1),
            await UdpTransportTarget.create((SNMP_HOST, SNMP_PORT)),
            ContextData(),
            ObjectType(ObjectIdentity(oid)),
            lexicographicMode=False,
        )

        if error_indication:
            print(f"Error: {error_indication}")
            break
        elif error_status:
            print(f"SNMP Error: {error_status}")
            break
        elif not var_binds:
            break
        else:
            for var_bind in var_binds:
                var_oid, var_value = var_bind[0], var_bind[1]
                print(f"{var_oid} = {var_value}")

                if not str(var_oid).startswith(str(original_oid)):
                    print(f"Walk finished: {var_oid} is outside the subtree {oid}")
                    is_walk_finished = True
                    break

                results.append((str(var_oid), str(var_value)))

        oid = var_binds[-1][0]

        if not results or is_walk_finished:
            print("No more results, exiting walk.")
            break

    snmp_engine.transportDispatcher.closeDispatcher()
    return results


async def get_value(oid):
    results = []
    original_oid = oid
    is_walk_finished = False
    snmp_engine = SnmpEngine()

    error_indication, error_status, _, var_binds = await next_cmd(
        snmp_engine,
        CommunityData(SNMP_COMMUNITY, mpModel=1),
        await UdpTransportTarget.create((SNMP_HOST, SNMP_PORT)),
        ContextData(),
        ObjectType(ObjectIdentity(oid)),
        lexicographicMode=False,
    )

    if error_indication:
        print(f"Error: {error_indication}")
    elif error_status:
        print(f"SNMP Error: {error_status}")
    elif not var_binds:
        return
    else:
        for var_bind in var_binds:
            var_oid, var_value = var_bind[0], var_bind[1]
            return var_value
            print(f"{var_oid} = {var_value}")

            if not str(var_oid).startswith(str(original_oid)):
                print(f"Walk finished: {var_oid} is outside the subtree {oid}")
                is_walk_finished = True

            results.append((str(var_oid), str(var_value)))

    if not results or is_walk_finished:
        print("No more results, exiting walk.")

    snmp_engine.transportDispatcher.closeDispatcher()
    return results


# Monitor CPU and Memory Usage
async def monitor_resources():
    while True:
        # cpu_load = await walk_next_value("1.3.6.1.2.1.25.2.1")
        cpu_load = await get_value("1.3.6.1.2.1.25.2.1.8")

        # print(f"cpu_load: {cpu_load}")
        # mem_total = await walk_next_value(MEM_TOTAL_OID)
        # print(f"mem_total: {mem_total}")
        # mem_used = await walk_next_value(MEM_USED_OID)
        # print(f"mem_used: {mem_used}")

        print(cpu_load)
        return

        for c in cpu_load:
            print(f"CPU Load: {c}%")

        # if cpu_load and mem_total and mem_used:
        #     mem_total_mb = int(mem_total) // 1024
        #     mem_used_mb = int(mem_used) // 1024
        #
        #     if mem_total_mb > 0:
        #         mem_usage_percent = (mem_used_mb / mem_total_mb) * 100
        #     else:
        #         mem_usage_percent = 0.0
        #
        #     print(f"CPU Load: {cpu_load}%")
        #     print(
        #         f"Memory Usage: {mem_used_mb} MB / {mem_total_mb} MB ({mem_usage_percent:.2f}%)"
        #     )
        #     print("-" * 40)

        await asyncio.sleep(10)  # Monitor every 10 seconds


if __name__ == "__main__":
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(monitor_resources())
    except KeyboardInterrupt:
        print("Monitoring stopped.")
    finally:
        loop.close()
