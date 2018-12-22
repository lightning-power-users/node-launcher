from flask import render_template, Flask
from flask_admin import Admin
from flask_frozen import Freezer
from google.protobuf.json_format import MessageToDict

from node_launcher.node_set.lnd_client.rpc_pb2 import Channel
from website.admin.models.pending_channel import PendingChannel
from website.admin.pending_channels_model_view import PendingChannelsModelView

from website.admin.open_channels_model_view import OpenChannelsModelView
from website.constants import FLASK_SECRET_KEY, node_set


class App(Flask):
    def __init__(self):
        super().__init__(__name__)
        self.debug = False
        self.config['SECRET_KEY'] = FLASK_SECRET_KEY

        @self.route('/')
        def index():
            # noinspection PyBroadException
            try:
                info = MessageToDict(node_set.lnd_client.get_info())
            except Exception as e:
                info = None
            return render_template('index.html', info=info)

        self.admin = Admin(app=self,
                           name='Bitcoin/LN',
                           template_mode='bootstrap3',
                           )

        self.admin.add_view(PendingChannelsModelView(PendingChannel,
                                                     name='Pending Channels',
                                                     category='LND'))

        self.admin.add_view(OpenChannelsModelView(Channel,
                                                  name='Open Channels',
                                                  category='LND'))

        @self.route('/help')
        def help_route():
            return render_template('help.html')


if __name__ == '__main__':
    app = App()
    app.debug = True
    app.run()
