from flask import render_template, Flask
from flask_frozen import Freezer

app = Flask(__name__)


@app.route('/')
def index(name=None):
    return render_template('index.html', name=name)


freezer = Freezer(app)


if __name__ == '__main__':
    app.debug = True
    app.run()
    # freezer.freeze()
