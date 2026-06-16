"""
__main__.py — TalkingDB GCP infrastructure entrypoint.

Current Pulumi state (synced with GCP as of Jun 2026):
  - ttt-chat VM        : imported (update #1)
  - default VPC        : read-only lookup
  - Firewall rules     : imported (update #2) — default-allow-ssh/http/https/internal
  - GCS buckets        : TODO — not yet created, uncomment when ready
"""

import pulumi
from modules.networking import get_default_network
from modules import compute
from modules import firewall

# ── Config ────────────────────────────────────────────────────────────────────
cfg = pulumi.Config("talkingdb")
gcp_cfg = pulumi.Config("gcp")

ENV = cfg.require("env")
PROJECT = gcp_cfg.require("project")

# ── Networking (read-only lookup of existing default VPC) ─────────────────────
network = get_default_network()

# ── Storage ───────────────────────────────────────────────────────────────────
# TODO when ready to create GCS buckets:
#
# from modules.storage import create_storage
# create_storage(ENV, PROJECT)
