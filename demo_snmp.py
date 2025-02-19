from pysnmp.entity import engine, config
from pysnmp.carrier.asyncio.dgram import udp
from pysnmp.entity.rfc3413 import ntfrcv

snmpEngine = engine.SnmpEngine()

config.add_transport(
    snmpEngine,
    udp.DOMAIN_NAME + (1,),
    udp.UdpTransport().open_server_mode(("0.0.0.0", 162)),
)

config.add_v1_system(snmpEngine, "my-area", "public")


def cb_fun(snmpEngine, stateReference, contextEngineId, contextName, varBinds, cbCtx):
    print("Received SNMP trap:")
    for name, val in varBinds:
        print(f"{name.prettyPrint()} = {val.prettyPrint()}")


ntfrcv.NotificationReceiver(snmpEngine, cb_fun)

snmpEngine.transport_dispatcher.job_started(1)

try:
    print("Listening for SNMP traps...")
    snmpEngine.transport_dispatcher.run_dispatcher()
except:
    snmpEngine.transport_dispatcher.close_dispatcher()
    raise
