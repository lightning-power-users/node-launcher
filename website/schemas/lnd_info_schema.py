"""
identity_pubkey
03fd5d4b4eb03c531749a1abf197d8f09e48b54e2540fa6d8e115d4b9b0f285b9f
alias
03fd5d4b4eb03c531749
num_active_channels
1
num_peers
4
block_height
556126
block_hash
0000000000000000001f5a0cb63b184372c1330c2b87d56e925c3a9302651061
synced_to_chain
True
chains
bitcoin
best_header_timestamp
1546125426
version
0.5.1-beta commit=
"""
from marshmallow import Schema, fields


class LndInfoSchema(Schema):
    identity_pubkey = fields.Str()
