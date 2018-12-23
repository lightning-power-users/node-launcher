from flask import Flask, redirect, render_template
from flask_admin import Admin

from website.views.home_view import HomeView
from website.models import Channels, PendingChannels
from website.views.pending_channels_model_view import PendingChannelsModelView
from website.views.open_channels_model_view import OpenChannelsModelView
from website.constants import FLASK_SECRET_KEY


class App(Flask):
    def __init__(self):
        super().__init__(__name__)
        self.debug = False
        self.config['SECRET_KEY'] = FLASK_SECRET_KEY

        @self.route('/')
        def index():
            return redirect('admin/home')

        @self.errorhandler(404)
        def page_not_found(e):
            return redirect('admin/home')

        self.admin = Admin(app=self)
        self.admin.add_view(HomeView(name='Home', endpoint='home'))
        self.admin.add_view(PendingChannelsModelView(PendingChannels,
                                                     endpoint='pending-channels',
                                                     name='Pending Channels',
                                                     category='LND'))
        self.admin.add_view(OpenChannelsModelView(Channels,
                                                  endpoint='channels',
                                                  name='Open Channels',
                                                  category='LND'))

        @self.route('/help')
        def help_route():
            return render_template('help.html')


if __name__ == '__main__':
    app = App()
    app.debug = True
    app.run()
