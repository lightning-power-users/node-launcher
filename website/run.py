from flask import render_template, Flask
from flask_frozen import Freezer
from google.protobuf.json_format import MessageToDict

from node_launcher.node_set import NodeSet

app = Flask(__name__)

node_set = NodeSet('mainnet')


@app.route('/')
def index():
    # noinspection PyBroadException
    try:
        info = MessageToDict(node_set.lnd_client.get_info())
    except Exception as e:
        info = None
    return render_template('index.html', info=info)


@app.route('/channels')
def channels():
    channel_data = []

    return render_template('channels.html', channels=channel_data)


@app.route('/help')
def help_route():
    return render_template('help.html')


freezer = Freezer(app)

if __name__ == '__main__':
    app.debug = True
    app.run()
    # freezer.freeze()
