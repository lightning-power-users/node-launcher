from flask import request, render_template
from flask_admin import BaseView, expose

from node_launcher.node_set import NodeSet
from website.constants import network
from website.forms.payment_request_form import PaymentRequestForm


class TipView(BaseView):

    @expose('/')
    def index(self):
        form = PaymentRequestForm()
        node_set = NodeSet(network)
        address = node_set.lnd_client.get_new_address()
        return render_template('tip.html',
                               form=form,
                               address=address)

    @expose('/payreq', methods=['POST'])
    def tip(self):
        node_set = NodeSet(network)
        payment_request = node_set.lnd_client.create_invoice(
            value=int(request.form['value']),
            memo=request.form['memo']
        ).payment_request
        uri = ':'.join(['lightning', payment_request])

        return render_template('payment_request.html',
                               payment_request=payment_request,
                               uri=uri)
