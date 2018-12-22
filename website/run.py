import json

from flask import render_template, Flask, redirect
from flask_admin import Admin, BaseView, expose
from google.protobuf.json_format import MessageToDict

from website.admin.models.pending_channel import PendingChannels, Channels
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
           return redirect('admin/home')

        self.admin = Admin(app=self)

        class HomeView(BaseView):
            @expose('/')
            def index(self):
                # noinspection PyBroadException
                try:
                    # Todo add timeout
                    info = MessageToDict(node_set.lnd_client.get_info())
                    with open('cache/info.json', 'w') as f:
                        json.dump(info, f)
                except Exception as e:
                    # Todo add logging
                    with open('cache/info.json', 'r') as f:
                        info = json.load(f)
                return render_template('index.html', info=info)

        self.admin.add_view(HomeView(name='Home', endpoint='home'))

        self.admin.add_view(PendingChannelsModelView(PendingChannels,
                                                     name='Pending Channels',
                                                     category='LND'))

        self.admin.add_view(OpenChannelsModelView(Channels,
                                                  name='Open Channels',
                                                  category='LND'))

        @self.route('/help')
        def help_route():
            return render_template('help.html')


if __name__ == '__main__':
    app = App()
    app.debug = True
    app.run()
