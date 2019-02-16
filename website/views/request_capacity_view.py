import uuid
from decimal import Decimal

import structlog
from bitcoin.core import COIN
from flask import request, render_template, redirect, url_for, flash, session
from flask_admin import BaseView, expose
from google.protobuf.json_format import MessageToDict
# noinspection PyProtectedMember
from grpc._channel import _Rendezvous

from node_launcher.node_set import NodeSet
from website.constants import EXPECTED_BYTES, CAPACITY_CHOICES, \
    CAPACITY_FEE_RATES
from website.forms.request_capacity_form import RequestCapacityForm
from website.lnd_queries.channels import Channels
from website.utilities.cache.cache import get_latest
from website.utilities.dump_json import dump_json
from website.utilities.websocket_client import send_websocket_message


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
        select_label_time_estimate = fee_estimate['label'].replace('_',
                                                                   ' ').capitalize()
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
        logger = structlog.get_logger()
        log = logger.new(request_id=str(uuid.uuid4()))
        price = get_latest('usd_price')
        last_price = price['last']
        price_per_sat = last_price / COIN
        form = get_request_capacity_form()
        if session.get('tracker', None) is None:
            session['tracker'] = uuid.uuid4().hex
        log.debug('RequestCapacityView.index', tracker=session['tracker'])
        return render_template('request_capacity.html',
                               form=form,
                               price_per_sat=price_per_sat,
                               EXPECTED_BYTES=EXPECTED_BYTES)

    @expose('/pay-req', methods=['GET', 'POST'])
    def process_request(self):
        logger = structlog.get_logger()
        log = logger.new(request_id=str(uuid.uuid4()))
        if request.method != 'POST':
            log.warn(
                'RequestCapacityView.process_request invalid request method',
                request_method=request.method
            )
            return redirect(url_for('request-capacity.index'))

        form_data = request.form
        log.info(
            'request-capacity.process_request POST request',
            form_data=form_data
        )

        # PubKey processing
        pub_key_data = form_data.get('pub_key', '').strip()
        if not pub_key_data:
            log.debug(
                'request-capacity.process_request no pubkey provided',
                pub_key_data=pub_key_data
            )
            flash('Error: please enter your PubKey', category='danger')
            return redirect(url_for('request-capacity.index'))

        if '@' in pub_key_data:
            try:
                pub_key, ip_address = pub_key_data.split('@')
                log.debug('Parsed host', ip_address=ip_address)
            except ValueError:
                log.debug(
                    'request-capacity.process_request invalid pubkey format',
                    pub_key_data=pub_key_data
                )
                flash('Error: invalid PubKey format', category='danger')
                return redirect(url_for('request-capacity.index'))
        else:
            pub_key = pub_key_data
            ip_address = None

        if len(pub_key) != 66:
            flash('Error: invalid PubKey length, expected 66 characters',
                  category='danger')
            return redirect(url_for('request-capacity.index'))

        # Connect to peer
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
                              data=form_data, details=details)
                    return redirect(url_for('request-capacity.index'))
        else:
            peers = node_set.lnd_client.list_peers()
            try:
                peer = [p for p in peers if p.pub_key == pub_key][0]
            except IndexError:
                flash('Error: unknown PubKey, please provide pubkey@host:port',
                      category='danger')
                return redirect(url_for('request-capacity.index'))

        # Check channels
        channels = Channels(pubkey=pub_key)
        if len(channels.pending_channels) > 0:
            if len(channels.pending_channels) > 1:
                flash(f'Error: you already have {len(channels.pending_channels)} channels pending with our node, please wait for them to confirm',
                      category='danger')
                return redirect(url_for('request-capacity.index'))
            else:
                flash(f'Error: you already have a channel pending with our node, please wait for it to confirm',
                      category='danger')
                return redirect(url_for('request-capacity.index'))

        if len(channels) >= 2:
            flash(f'Error: you already have {len(channels)} open or pending channels',
                  category='danger')
            return redirect(url_for('request-capacity.index'))

        # Validate inputs
        requested_capacity = int(form_data['capacity'])
        if requested_capacity != 0 and requested_capacity not in CAPACITY_CHOICES:
            flash('Error: invalid capacity request', category='danger')
            return redirect(url_for('request-capacity.index'))

        reciprocation_capacity = None
        if requested_capacity == 0:
            if len(channels) != 1:
                flash(f'Error: you do not currently have an open channel with our node for us to reciprocate',
                      category='danger')
                return redirect(url_for('request-capacity.index'))

            if channels.net_remote_balance < 100000:
                flash(f'Error: your remote balance minus our local balance '
                      f'is {channels.net_remote_balance:,d}, 100,000 is the minimum for reciprocation',
                      category='danger')
                return redirect(url_for('request-capacity.index'))

            reciprocation_capacity = max(channels.net_remote_balance, 200000)

        requested_capacity_fee_rate = Decimal(
            form_data.get('capacity_fee_rate', '0'))
        if requested_capacity_fee_rate not in dict(CAPACITY_FEE_RATES):
            flash('Error: invalid capacity fee rate request', category='danger')
            return redirect(url_for('request-capacity.index'))

        capacity_fee = int(requested_capacity * requested_capacity_fee_rate)

        transaction_fee_rate = int(form_data['transaction_fee_rate'])
        if not transaction_fee_rate >= 1:
            flash('Error: invalid transaction fee rate request',
                  category='danger')
            return redirect(url_for('request-capacity.index'))

        transaction_fee = transaction_fee_rate * EXPECTED_BYTES
        total_fee = capacity_fee + transaction_fee

        memo = 'Lightning Power Users capacity request: '
        if requested_capacity == 0:
            memo += 'reciprocate'
        else:
            memo += f'{requested_capacity} @ {requested_capacity_fee_rate}'

        invoice = node_set.lnd_client.create_invoice(
            value=int(total_fee),
            memo=memo
        )
        invoice = MessageToDict(invoice)
        payment_request = invoice['payment_request']
        uri = ':'.join(['lightning', payment_request])

        if not session.get('tracker', None):
            session['tracker'] = uuid.uuid4().hex

        if requested_capacity == 0:
            requested_capacity_copy = f'Reciprocate {reciprocation_capacity:,d}'
            capacity_fee_rate_copy = '0%'
            capacity_fee_copy = '-'
        else:
            requested_capacity_copy = f'{requested_capacity:,d}'
            capacity_fee_rate_copy = f'{requested_capacity_fee_rate:.0%}'
            capacity_fee_copy = f'{capacity_fee:,d}'

        bill = [
            ('Requested capacity', requested_capacity_copy),
            ('Capacity fee rate', capacity_fee_rate_copy),
            ('Capacity fee', capacity_fee_copy),
            ('Transaction fee rate', f'{transaction_fee_rate:,d}'),
            ('Expected bytes', f'{EXPECTED_BYTES:,d}'),
            ('Transaction fee', f'{transaction_fee:,d}'),
            ('Total fee', f'{total_fee:,d}')
        ]

        data = {
            'type': 'inbound_capacity_request',
            'bill': bill,
            'reciprocation_capacity': reciprocation_capacity,
            'form_data': form_data,
            'tracker': session['tracker'],
            'invoice': invoice,
            'EXPECTED_BYTES': EXPECTED_BYTES,
            'parsed_pubkey': pub_key,
            'parsed_host': ip_address
        }

        log.debug('request-capacity.process_request', data=data)

        dump_json(data=data, name='capacity_request', label=session['tracker'])

        log.debug(
            'request-capacity.process_request sending websocket data'
        )
        send_websocket_message(data=data)

        return render_template(
            'payment_request.html',
            bill=bill,
            payment_request=payment_request,
            uri=uri
        )
