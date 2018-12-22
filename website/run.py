from flask import Flask, redirect, render_template
from flask_admin import Admin

from website.admin.home_view import HomeView
from website.admin.models.pending_channel import Channels, PendingChannels
from website.admin.open_channels_model_view import OpenChannelsModelView
from website.admin.pending_channels_model_view import PendingChannelsModelView
from website.constants import FLASK_SECRET_KEY


class App(Flask):
    def __init__(self):
        super().__init__(__name__)
        self.debug = False
        self.config['SECRET_KEY'] = FLASK_SECRET_KEY

        @self.route('/')
        def index():
            return redirect('admin/home')

        self.admin = Admin(app=self)
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
