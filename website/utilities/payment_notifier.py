import socketio

# standard Python
sio = socketio.Client()


@sio.on('connect')
def on_connect():
    print('Im connected!')


@sio.on('message')
def on_message(data):
    print('I received a message!')


@sio.on('my message')
def on_message(data):
    print('I received a custom message!')


@sio.on('disconnect')
def on_disconnect():
    print('Im disconnected!')


sio.connect('http://localhost:5003')
