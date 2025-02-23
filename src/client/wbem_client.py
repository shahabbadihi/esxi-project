from typing import List, Dict, Optional

from pywbem import WBEMConnection, CIMInstance


class WBEMClient:

    def __init__(self, host: str, username: str, password: str, no_verify=True):
        self.host: str = host
        self.username: str = username
        self.password: str = password
        self.no_verify: bool = no_verify
        self.conn: Optional[WBEMConnection] = None

    def __enter__(self):
        self.conn = WBEMConnection(
            self.host,
            (self.username, self.password),
            no_verification=self.no_verify,
        )
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.conn:
            self.conn.close()

    def enumerate_instances(self, class_name: str, namespace: str) -> List[Dict]:
        if not self.conn:
            raise RuntimeError("Connection is not established.")
        return self.conn.EnumerateInstances(class_name, namespace=namespace)
