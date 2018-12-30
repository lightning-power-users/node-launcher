from flask import Flask, redirect, render_template, url_for
from flask_admin import Admin
from flask_qrcode import QRcode

from website.extensions import cache
from website.views.home_view import HomeView
from website.models import Channels, PendingChannels
from website.views.pending_channels_model_view import PendingChannelsModelView
from website.views.open_channels_model_view import OpenChannelsModelView
from website.constants import FLASK_SECRET_KEY
from website.views.tip_view import TipView


class App(Flask):
    def __init__(self):
        super().__init__(__name__)
        cache.init_app(self)
        QRcode(self)
        self.debug = False
        self.config['SECRET_KEY'] = FLASK_SECRET_KEY

        @self.route('/')
        @cache.memoize(timeout=600)
        def index():
            return redirect(url_for('home.index'))

        @self.errorhandler(404)
        @cache.memoize(timeout=600)
        def page_not_found(e):
            return redirect(url_for('home.index'))

        self.admin = Admin(app=self,
                           url='/')
        self.admin.add_view(HomeView(name='Home', endpoint='home'))
        self.admin.add_view(TipView(name='Send a Tip', endpoint='tip'))
        self.admin.add_view(PendingChannelsModelView(PendingChannels,
                                                     endpoint='pending-channels',
                                                     name='Pending Channels',
                                                     category='LND'))
        self.admin.add_view(OpenChannelsModelView(Channels,
                                                  endpoint='channels',
                                                  name='Open Channels',
                                                  category='LND'))


if __name__ == '__main__':
    app = App()
    app.debug = True
    app.run()
