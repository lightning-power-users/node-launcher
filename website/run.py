from flask import render_template, Flask
from flask_frozen import Freezer

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


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
