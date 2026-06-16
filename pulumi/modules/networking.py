"""
networking.py — Networking for TalkingDB.

IMPORTANT: The existing VM `ttt-chat` is on GCP's DEFAULT VPC (not a custom VPC).
  Network : default
  Subnet  : default (asia-south1, 10.160.0.0/20)

We do NOT create a new VPC here — that would require migrating the running VM.

What this module does instead:
  - References the existing default network as a Pulumi data source
  - Exports the network self_link so firewall.py can attach rules to it
  - Leaves a TODO for migrating to a custom VPC later (when VM can be recreated)
"""

import pulumi
import pulumi_gcp as gcp


def get_default_network() -> gcp.compute.GetNetworkResult:
    """
    Look up the existing default VPC.
    Returns a data source (read-only) — does NOT create anything.
    """

    network = gcp.compute.get_network(name="default")

    pulumi.export("vpc_name", network.name)
    pulumi.export("vpc_self_link", network.self_link)

    return network


# ── Future: custom VPC migration ──────────────────────────────────────────────
# When you next recreate the VM (e.g. upgrading machine type or OS), switch to:
#
#   network = gcp.compute.Network("talkingdb-vpc", auto_create_subnetworks=False)
#   subnet  = gcp.compute.Subnetwork("talkingdb-subnet",
#                 ip_cidr_range="10.10.0.0/24",
#                 region="asia-south1",
#                 network=network.id)
#
# Until then, using default VPC is fine for dev.