"""
firewall.py — Firewall rules for TalkingDB.

All 4 rules already existed in GCP on the default VPC and have been
imported into Pulumi state (updates #2, #3, #4, #5).

How each rule applies to ttt-chat:
  - default-allow-ssh      → all instances (no tag filter) → covers ttt-chat
  - default-allow-http     → targets http-server tag       → ttt-chat has this tag
  - default-allow-https    → targets https-server tag      → ttt-chat has this tag
  - default-allow-internal → all instances, internal range → covers ttt-chat

DO NOT modify these unless you intend to change the actual GCP rules.
All are marked protect=True — Pulumi will refuse to delete them.
"""

import pulumi
import pulumi_gcp as gcp


default_allow_ssh = gcp.compute.Firewall("default-allow-ssh",
                                         allows=[{
                                             "ports": ["22"],
                                             "protocol": "tcp",
                                         }],
                                         description="Allow SSH from anywhere",
                                         direction="INGRESS",
                                         name="default-allow-ssh",
                                         network="https://www.googleapis.com/compute/v1/projects/talkingdb-40099/global/networks/default",
                                         priority=65534,
                                         project="talkingdb-40099",
                                         source_ranges=["0.0.0.0/0"],
                                         opts=pulumi.ResourceOptions(
                                             protect=True),
                                         )

default_allow_http = gcp.compute.Firewall("default-allow-http",
                                          allows=[{
                                              "ports": ["80"],
                                              "protocol": "tcp",
                                          }],
                                          direction="INGRESS",
                                          name="default-allow-http",
                                          network="https://www.googleapis.com/compute/v1/projects/talkingdb-40099/global/networks/default",
                                          project="talkingdb-40099",
                                          source_ranges=["0.0.0.0/0"],
                                          target_tags=["http-server"],
                                          opts=pulumi.ResourceOptions(
                                              protect=True),
                                          )

default_allow_https = gcp.compute.Firewall("default-allow-https",
                                           allows=[{
                                               "ports": ["443"],
                                               "protocol": "tcp",
                                           }],
                                           direction="INGRESS",
                                           name="default-allow-https",
                                           network="https://www.googleapis.com/compute/v1/projects/talkingdb-40099/global/networks/default",
                                           project="talkingdb-40099",
                                           source_ranges=["0.0.0.0/0"],
                                           target_tags=["https-server"],
                                           opts=pulumi.ResourceOptions(
                                               protect=True),
                                           )

default_allow_internal = gcp.compute.Firewall("default-allow-internal",
                                              allows=[
                                                  {
                                                      "ports": ["0-65535"],
                                                      "protocol": "tcp",
                                                  },
                                                  {
                                                      "ports": ["0-65535"],
                                                      "protocol": "udp",
                                                  },
                                                  {
                                                      "protocol": "icmp",
                                                  },
                                              ],
                                              description="Allow internal traffic on the default network",
                                              direction="INGRESS",
                                              name="default-allow-internal",
                                              network="https://www.googleapis.com/compute/v1/projects/talkingdb-40099/global/networks/default",
                                              priority=65534,
                                              project="talkingdb-40099",
                                              source_ranges=["10.128.0.0/9"],
                                              opts=pulumi.ResourceOptions(
                                                  protect=True),
                                              )
