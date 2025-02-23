from typing import List, Dict

from config import esxi_config
from client import WBEMClient

from utils.logger import setup_logger

logger = setup_logger(__name__)


class WBEMESXiService:

    def __init__(self):
        self.esxi_host = esxi_config.host
        self.esxi_username = esxi_config.username
        self.esxi_password = esxi_config.password
        self.esxi_processor_cim_class_name = esxi_config.processor_cim_class_name
        self.esxi_processor_cim_namespace = esxi_config.processor_cim_namespace

    def get_info_about_system(self) -> List[Dict]:
        with WBEMClient(
            host=self.esxi_host,
            username=self.esxi_username,
            password=self.esxi_password,
        ) as client:
            try:
                return [
                    {
                        "Processor Model Name": ins["ModelName"],
                        "Processor Device ID": ins["DeviceID"],
                        "CPU Status": ins["CPUStatus"],
                        "CPU Max Clock Speed": ins["MaxClockSpeed"],
                        "CPU Health Status": ins["HealthState"],
                    }
                    for ins in client.enumerate_instances(
                        class_name=self.esxi_processor_cim_class_name,
                        namespace=self.esxi_processor_cim_namespace,
                    )
                ]
            except Exception as e:
                logger.error(f"An error occurred while getting system info: {str(e)}")
                raise
