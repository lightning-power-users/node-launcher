import uuid
from decimal import Decimal

from bitcoin.core import COIN
from flask import request, render_template, redirect, url_for, flash
from flask_admin import BaseView, expose
from google.protobuf.json_format import MessageToDict
from grpc._channel import _Rendezvous

from node_launcher.logging import log
from node_launcher.node_set import NodeSet
from website.constants import EXPECTED_BYTES, CAPACITY_CHOICES, \
    CAPACITY_FEE_RATES
from website.forms.request_capacity_form import RequestCapacityForm
from website.utilities.cache.cache import get_latest
from website.utilities.dump_json import dump_json


def get_request_capacity_form() -> RequestCapacityForm:
    form = RequestCapacityForm()
    fee_estimates = get_latest('fee_estimate')

    fee_estimate_choices = []
    previous_estimate = 0
    for fee_estimate in fee_estimates:
        estimated_fee_per_byte = fee_estimate['conservative']['feerate']
        if estimated_fee_per_byte == previous_estimate:
            continue
        previous_estimate = estimated_fee_per_byte
        select_label_time_estimate = fee_estimate['label'].replace('_', ' ').capitalize()
        if estimated_fee_per_byte > 1:
            select_label = f'{select_label_time_estimate} ({estimated_fee_per_byte} sats per byte)'
        else:
            select_label = f'{select_label_time_estimate} (1 sat per byte)'
        select_value = estimated_fee_per_byte
        fee_estimate_choices.append((select_value, select_label))

    form.transaction_fee_rate.choices = fee_estimate_choices
    form.capacity.choices = []
    form.capacity.choices.append((0, 'Reciprocate'))
    for capacity_choice in CAPACITY_CHOICES:
        form.capacity.choices.append((capacity_choice, f'{capacity_choice:,}'))

    form.capacity_fee_rate.choices = CAPACITY_FEE_RATES
    return form


class RequestCapacityView(BaseView):

    @expose('/')
    def index(self):
        price = get_latest('usd_price')
        last_price = price['last']
        price_per_sat = last_price/COIN
        form = get_request_capacity_form()
        node_set = NodeSet()
        address = node_set.lnd_client.get_new_address()
        return render_template('request_capacity.html',
                               form=form,
                               address=address,
                               price_per_sat=price_per_sat,
                               EXPECTED_BYTES=EXPECTED_BYTES)

    @expose('/process_request', methods=['GET', 'POST'])
    def process_request(self):
        if request.method != 'POST':
            return redirect(url_for('request-capacity.index'))

        data = request.form
        pub_key_data = data['pub_key'].strip()
        if not pub_key_data:
            flash('Error: please enter your PubKey', category='danger')
            return redirect(url_for('request-capacity.index'))

        if '@' in pub_key_data:
            try:
                pub_key, ip_address = pub_key_data.split('@')
            except ValueError:
                flash('Error: invalid PubKey format', category='danger')
                return redirect(url_for('request-capacity.index'))
        else:
            pub_key = pub_key_data
            ip_address = None

        if len(pub_key) != 66:
            flash('Error: invalid PubKey length, expected 66 characters', category='danger')
            return redirect(url_for('request-capacity.index'))

        node_set = NodeSet()

        if ip_address is not None:
            try:
                node_set.lnd_client.connect_peer(pub_key, ip_address)
            except _Rendezvous as e:
                details = e.details()
                if 'already connected to peer' in details:
                    pass
                else:
                    flash(f'Error: {details}', category='danger')
                    log.error('request-capacity.process_request POST',
                              data=data, details=details)
                    return redirect(url_for('request-capacity.index'))
        else:
            peers = node_set.lnd_client.list_peers()
            try:
                peer = [p for p in peers if p.pub_key == pub_key][0]
            except IndexError:
                flash('Error: unknown PubKey, please provide pubkey@host:port', category='danger')
                return redirect(url_for('request-capacity.index'))

        requested_capacity = int(data['capacity'])
        if requested_capacity != 0 and requested_capacity not in CAPACITY_CHOICES:
            flash('Error: invalid capacity request', category='danger')
            return redirect(url_for('request-capacity.index'))

        requested_capacity_fee_rate = Decimal(data.get('capacity_fee_rate', '0'))
        if requested_capacity_fee_rate not in dict(CAPACITY_FEE_RATES):
            flash('Error: invalid capacity fee rate request', category='danger')
            return redirect(url_for('request-capacity.index'))

        capacity_fee = requested_capacity * requested_capacity_fee_rate

        transaction_fee_rate = int(data['transaction_fee_rate'])
        if not transaction_fee_rate >= 1:
            flash('Error: invalid transaction fee rate request', category='danger')
            return redirect(url_for('request-capacity.index'))

        transaction_fee = transaction_fee_rate * EXPECTED_BYTES
        total_fee = capacity_fee + transaction_fee

        tracker = uuid.uuid4().hex
        dump_json(data=data, name='capacity_request', label=tracker)
        log.info('request-capacity.process_request POST', data=data)

        memo = 'Lightning Power Users capacity request: '
        if requested_capacity == 0:
            memo += 'reciprocate'
        else:
            memo += f'{requested_capacity} @ {requested_capacity_fee_rate}'

        invoice = node_set.lnd_client.create_invoice(
            value=int(total_fee),
            memo=f'Capacity request: '
        )
        invoice = MessageToDict(invoice)
        payment_request = invoice['payment_request']
        uri = ':'.join(['lightning', payment_request])

        return render_template('payment_request.html',
                               payment_request=payment_request,
                               uri=uri)
