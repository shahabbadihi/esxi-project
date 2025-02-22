from typing import Callable
import threading
import asyncio

from pysnmp.entity import engine, config
from pysnmp.carrier.asyncio.dgram import udp
from pysnmp.entity.rfc3413 import ntfrcv

from utils.logger import setup_logger

logger = setup_logger(__name__)


class SNMPTrapClient:

    def __init__(
        self,
        trap_receiver_host: str,
        trap_receiver_port: int,
        community_str: str,
        community_index: str,
        trap_callback_func: Callable,
    ):
        self._trap_receiver_host = trap_receiver_host
        self._trap_receiver_port = trap_receiver_port
        self._community_str = community_str
        self._community_index = community_index
        self.running = False
        self.thread = None

        self._snmp_engine = engine.SnmpEngine()
        self._trap_callback_func = trap_callback_func

        self._setup()

    def _setup(self):
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            asyncio.set_event_loop(asyncio.new_event_loop())
        config.add_transport(
            self._snmp_engine,
            udp.DOMAIN_NAME + (1,),
            udp.UdpTransport().open_server_mode(
                (self._trap_receiver_host, self._trap_receiver_port)
            ),
        )

        config.add_v1_system(
            self._snmp_engine, self._community_index, self._community_str
        )

        def _trap_callback(
            snmp_engine,
            state_reference,
            context_engine_id,
            context_name,
            var_binds,
            cb_ctx,
        ):
            logger.info("Received SNMP trap:")
            for name, val in var_binds:
                logger.info(f"{name.prettyPrint()} = {val.prettyPrint()}")

            if self._trap_callback_func:
                self._trap_callback_func(var_binds)

        ntfrcv.NotificationReceiver(self._snmp_engine, _trap_callback)

    def _run_dispatcher(self):
        self.running = True
        self._snmp_engine.transport_dispatcher.job_started(1)

        try:
            logger.info(
                f"Listening for SNMP traps on {self._trap_receiver_host}:{self._trap_receiver_port}..."
            )
            self._snmp_engine.transport_dispatcher.run_dispatcher()
        except Exception as e:
            logger.error(f"SNMP dispatcher stopped: {e}")
        finally:
            self.running = False

    def __enter__(self):
        if not self.running:
            self.thread = threading.Thread(target=self._run_dispatcher, daemon=True)
            self.thread.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.running:
            logger.info("Stopping SNMP trap listener...")
            self.running = False
            if self.thread and self.thread.is_alive():
                self.thread.join(timeout=0.5)
        logger.info("SNMPTrapClient exited successfully")
