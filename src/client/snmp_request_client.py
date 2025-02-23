from pysnmp.entity.engine import SnmpEngine
from pysnmp.hlapi.v3arch import UdpTransportTarget
from pysnmp.hlapi.v3arch import CommunityData, ContextData
from pysnmp.smi.rfc1902 import ObjectType, ObjectIdentity
from pysnmp.hlapi.v3arch.asyncio import next_cmd

from utils.logger import setup_logger

logger = setup_logger(__name__)


class SNMPRequestClient:

    def __init__(self, host: str, port: int, community: str, version: int):
        self.host = host
        self.port = port
        self.community = community
        self.version = version

    async def walk(self, oid: str):
        results = []
        original_oid = oid
        is_walk_finished = False
        snmp_engine = SnmpEngine()

        while True:
            error_indication, error_status, _, var_binds = await next_cmd(
                snmp_engine,
                CommunityData(self.community, mpModel=0 if self.version == 1 else 1),
                await UdpTransportTarget.create((self.host, self.port)),
                ContextData(),
                ObjectType(ObjectIdentity(oid)),
                lexicographicMode=False,
            )

            if error_indication:
                logger.error(f"Error: {error_indication}")
                break
            elif error_status:
                logger.error(f"SNMP Error: {error_status}")
                break
            elif not var_binds:
                break
            else:
                for var_bind in var_binds:
                    var_oid, var_value = var_bind[0], var_bind[1]
                    logger.info(f"{var_oid} = {var_value}")

                    if not str(var_oid).startswith(str(original_oid)):
                        logger.info(
                            f"Walk finished: {var_oid} is outside the subtree {oid}"
                        )
                        is_walk_finished = True
                        break

                    results.append((str(var_oid), str(var_value)))

            oid = var_binds[-1][0]

            if not results or is_walk_finished:
                logger.warning("No more results, exiting walk.")
                break

        snmp_engine.transportDispatcher.closeDispatcher()
        return results
