from datetime import datetime

from markupsafe import Markup


def format_timestamp(view, context, model, name):
    timestamp = getattr(model, name)
    timestamp = str(datetime.fromtimestamp(timestamp))
    return Markup(f"""
        <div style="white-space: nowrap; overflow: hidden;">
            {timestamp}
        </div>
    """)


def format_hash(view, context, model, name):
    hash = getattr(model, name)
    return hash[-20:]


def format_integer(amount):
    amount = int(amount)
    if amount:
        currency_string = "{0:,d}".format(amount)
        if currency_string.startswith('-'):
            currency_string = currency_string.replace('-', '(')
            currency_string += ')'
        return Markup(f'<div style="text-align: right;">{currency_string}</div>')
    else:
        return Markup(f'<div style="text-align: center;">-</div>')


def satoshi_formatter(view, context, model, name):
    amount = getattr(model, name)
    if amount is not None:
        return format_integer(amount)
    return None