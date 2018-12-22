from flask import url_for
from markupsafe import Markup


def format_pub_key(long_pub_key: str):
    if long_pub_key:
        short_pub_key = long_pub_key[0:20]
        name = ''
        return Markup(
            '<div style="white-space: nowrap; overflow: hidden;">{0} {1}</div>'.format(
                short_pub_key, name))
    else:
        return ''


def pub_key_formatter(view, context, model, name):
    long_pub_key = getattr(model, name)
    return format_pub_key(long_pub_key)


def path_formatter(view, context, model, name):
    pub_keys = getattr(model, name)
    formatted = '<br>'.join([format_pub_key(p) for p in pub_keys])
    return Markup(formatted)


def get_txid_link(txid: str):
    # url = url_for('bitcoin-transaction.index', txid=txid)
    # txid = txid[-20:]
    # link = f'''<a href="{url}">{txid}</a>'''
    # return Markup(link)
    return txid[-20:]


def tx_hash_formatter(view, context, model, name):
    tx_hash = getattr(model, name)
    if tx_hash is None:
        return None
    link = get_txid_link(tx_hash)
    return Markup(link)


def channel_point_formatter(view, context, model, name):
    channel_point = getattr(model, name)
    txid, output_index = channel_point.split(':')
    link = get_txid_link(txid)
    link += ':' + str(output_index)
    return link
