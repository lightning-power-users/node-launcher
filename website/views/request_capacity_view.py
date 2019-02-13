from collections import OrderedDict

from flask import request, render_template
from flask_admin import BaseView, expose

from node_launcher.node_set import NodeSet
from website.forms.request_capacity_form import RequestCapacityForm
from website.utilities.cache_directory import get_latest


class RequestCapacityView(BaseView):

    @expose('/')
    def index(self):
        form = RequestCapacityForm()
        price = get_latest('usd_price')
        last_price = price['last']
        fee_estimates = get_latest('fee_estimate')

        fee_estimate_choices = []
        for fee_estimate in fee_estimates:
            estimated_fee_per_byte = fee_estimate['conservative']['feerate']
            estimated_fee = estimated_fee_per_byte * 200

            select_label = fee_estimate['label'].replace('_', ' ').capitalize()
            select_label = f'{select_label} ({estimated_fee_per_byte} sats per byte)'
            select_value = estimated_fee_per_byte
            fee_estimate_choices.append((select_value, select_label))
        form.fee_rate.choices = fee_estimate_choices
        form.fee_rate.default = fee_estimate_choices[3][0]
        node_set = NodeSet()
        address = node_set.lnd_client.get_new_address()
        return render_template('request_capacity.html',
                               form=form,
                               address=address)

    @expose('/buy_capacity', methods=['GET', 'POST'])
    def buy_channel(self):
        if request.method == 'POST':
            value = int(request.form['value'])
            memo = request.form['memo']
        else:
            value = 50000
            memo = 'Tip'
        node_set = NodeSet()
        payment_request = node_set.lnd_client.create_invoice(
            value=value,
            memo=memo
        ).payment_request
        uri = ':'.join(['lightning', payment_request])

        return render_template('payment_request.html',
                               payment_request=payment_request,
                               uri=uri)
