from typing import Optional

from pydantic import BaseModel


class CreateVMSchema(BaseModel):
    datacenter_name: Optional[str] = None
    vm_name: str
    memory_mb: int
    num_cpus: int
    disk_size_gb: int
    datastore_name: str
    network_name: str
    guest_id: str

    class Config:
        str_min_length = 1
        str_strip_whitespace = True
