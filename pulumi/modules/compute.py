"""
compute.py — Existing VM management for TalkingDB.

The VM `ttt-chat` has been imported into Pulumi state (update #1).
This file reflects the exact state GCP returned during import.
DO NOT modify values here unless you intend to change something on the actual VM.

Key facts:
  Project      : talkingdb-40099
  Zone         : asia-south1-c
  machine_type : e2-standard-2
  External IP  : 8.231.114.203  (ephemeral — reserve a static IP before setting up DNS)
  Internal IP  : 10.160.0.3
  Network      : default VPC
  Tags         : http-server, https-server
"""

import pulumi
import pulumi_gcp as gcp


ttt_chat = gcp.compute.Instance("ttt-chat",
                                boot_disk={
                                    "device_name": "ttt-chat",
                                    "guest_os_features": [
                                        "VIRTIO_SCSI_MULTIQUEUE",
                                        "SEV_CAPABLE",
                                        "SEV_SNP_CAPABLE",
                                        "SEV_LIVE_MIGRATABLE",
                                        "SEV_LIVE_MIGRATABLE_V2",
                                        "SNP_SVSM_CAPABLE",
                                        "IDPF",
                                        "TDX_CAPABLE",
                                        "UEFI_COMPATIBLE",
                                        "GVNIC",
                                    ],
                                    "initialize_params": {
                                        "architecture": "X86_64",
                                        "image": "https://www.googleapis.com/compute/beta/projects/ubuntu-os-cloud/global/images/ubuntu-2604-resolute-amd64-v20260527",
                                        "resource_policies": "https://www.googleapis.com/compute/beta/projects/talkingdb-40099/regions/asia-south1/resourcePolicies/default-schedule-1",
                                        "size": 30,
                                        "type": "pd-ssd",
                                    },
                                    "source": "https://www.googleapis.com/compute/v1/projects/talkingdb-40099/zones/asia-south1-c/disks/ttt-chat",
                                },
                                key_revocation_action_type="NONE",
                                machine_type="e2-standard-2",
                                allow_stopping_for_update=True,
                                metadata={
                                    "ssh-keys": """maansi_b:ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBAOVLoqKv72WpLpVEZxclkBty6fFeihARKAnD2x1cekJyoU8hsQIiWZB03tbUxTXk23w31b7mddv4OvWM/3PZGU= google-ssh {"userName":"maansi.b@smarter.codes","expireOn":"2026-06-12T03:43:59+0000"}
maansi_b:ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCVhV+LmeIJwFQ+DSLB0wIKmCqf72xveMWGjmJlP9VFwqwUlo9qZAcmCC8GE4724zZxVv08LMy32c2hf1/pcwd0VidGpB/kY+gB/o1uf67nJL2TcJhCNMoUNCFyygf0Ero9XgGOOhv2pdSL3nH9hxMKiU/zDO3cUvIJMLyyIe0xUALNEVvuDEq2NmHHX2sJtUgPioLw8XJFi2QxlN7qtRsjwl4oiAITbwf643W13ruOC8/rnsgFVL26YQYlOuN3GrONOr2/FXnZGA4wKsuNvNOf9sxYl4wIl6pSJXGyu2xdcrnLUOB0TWsIMMsxVXsG2mULTwlh0rLgQ7d/I7Y2PGGF google-ssh {"userName":"maansi.b@smarter.codes","expireOn":"2026-06-12T03:44:02+0000"}""",
                                },
                                name="ttt-chat",
                                network_interfaces=[{
                                    "access_configs": [{
                                        "nat_ip": "8.231.114.203",
                                        "network_tier": "PREMIUM",
                                    }],
                                    "network": "https://www.googleapis.com/compute/v1/projects/talkingdb-40099/global/networks/default",
                                    "network_ip": "10.160.0.3",
                                    "stack_type": "IPV4_ONLY",
                                    "subnetwork": "https://www.googleapis.com/compute/v1/projects/talkingdb-40099/regions/asia-south1/subnetworks/default",
                                    "subnetwork_project": "talkingdb-40099",
                                }],
                                project="talkingdb-40099",
                                reservation_affinity={
                                    "type": "ANY_RESERVATION",
                                },
                                scheduling={
                                    "on_host_maintenance": "MIGRATE",
                                    "provisioning_model": "STANDARD",
                                },
                                service_account={
                                    "email": "743319630762-compute@developer.gserviceaccount.com",
                                    "scopes": [
                                        "https://www.googleapis.com/auth/devstorage.read_only",
                                        "https://www.googleapis.com/auth/logging.write",
                                        "https://www.googleapis.com/auth/monitoring.write",
                                        "https://www.googleapis.com/auth/service.management.readonly",
                                        "https://www.googleapis.com/auth/servicecontrol",
                                        "https://www.googleapis.com/auth/trace.append",
                                    ],
                                },
                                tags=[
                                    "http-server",
                                    "https-server",
                                ],
                                zone="asia-south1-c",
                                opts=pulumi.ResourceOptions(protect=True)
                                )


# Export useful values for other modules and for reference
pulumi.export("vm_name", ttt_chat.name)
pulumi.export("vm_external_ip",
              ttt_chat.network_interfaces[0].access_configs[0].nat_ip)
pulumi.export("vm_internal_ip", ttt_chat.network_interfaces[0].network_ip)
