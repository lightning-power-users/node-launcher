from jinja2.runtime import Context

from app.bitcoind_client.models.blocks import Blocks


def format_block_txids(view, context: Context,
                       model: Blocks, name: str):
    return len(getattr(model, name))
