from typing import Optional

try:
    from diffsync import Adapter
except ImportError:
    from diffsync import DiffSync as Adapter
from nautobot.ipam.models import VLAN
from nautobot.apps.jobs import Job, register_jobs
from nautobot_ssot.contrib import NautobotModel, NautobotAdapter
from nautobot_ssot.jobs import DataSource

class APIClient:
    pass


# Step 1 - data modeling
class VLANModel(NautobotModel):
    """DiffSync model for VLANs."""
    _model = VLAN
    _modelname = "vlan"
    _identifiers = ("vid", "group__name")
    _attributes = ("description",)

    vid: int
    group__name: Optional[str] = None
    description: Optional[str] = None

# Step 2.1 - the Nautobot adapter
class MySSoTNautobotAdapter(NautobotAdapter):
    """DiffSync adapter for Nautobot."""
    vlan = VLANModel
    top_level = ("vlan",)

# Step 2.2 - the remote adapter
class MySSoTRemoteAdapter(Adapter):
    """DiffSync adapter for remote system."""
    vlan = VLANModel
    top_level = ("vlan",)

    def __init__(self, *args, api_client, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_client = api_client

    def load(self):
        for vlan in self.api_client.get_vlans():
            loaded_vlan = self.vlan(vid=vlan["vlan_id"], group__name=vlan["grouping"], description=vlan["description"])
            self.add(loaded_vlan)

# Step 3 - the job
class ExampleDataSource(DataSource, Job):
    """SSoT Job class."""
    class Meta:
        name = "Example Data Source"

    def load_source_adapter(self):
        self.source_adapter = MySSoTRemoteAdapter(api_client=APIClient())
        self.source_adapter.load()

    def load_target_adapter(self):
        self.target_adapter = MySSoTNautobotAdapter()
        self.target_adapter.load()

jobs = [ExampleDataSource]
register_jobs(*jobs)