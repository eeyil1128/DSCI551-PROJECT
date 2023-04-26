import json
from bson.json_util import dumps
from flask import Flask, render_template
from flask_socketio import SocketIO
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

app = Flask(__name__)
socketio = SocketIO(app)

# Configure MongoDB client
client = MongoClient("mongodb+srv://shuijing1996:Zshui1996!@dsci551.dgblqjz.mongodb.net/?retryWrites=true&w=majority")
db = client.dsci551
collection = db['2021Reservation']

@app.route('/')
def index():
    return render_template("index_sync.html")

def modify_change(change):
    # extract _id
    change['id'] = str(change['documentKey']['_id'])

    # extract time
    change['timestamp'] = str(change['wallTime'])

    # make operationType more granular
    if change['operationType'] == 'update':
        if change['updateDescription']['updatedFields'] == {}:
            change['operationType'] = 'delete_field'
        else:
            change['operationType'] = 'update_field'

    elif change['operationType'] == 'delete':
        change['operationType'] = 'delete_row'

    elif change['operationType'] == 'insert':
        change['operationType'] = 'insert_row'
        fulldoc = change['fullDocument']
        fulldoc.pop('_id')
        change['fullDocument'] = fulldoc
    else:
        pass

    return change


def watch_changes():
    try:
        with collection.watch() as stream:
            while stream.alive:
                change = stream.try_next()
                if change is not None:
                    change = modify_change(change)
                    socketio.emit("change_data", json.loads(dumps(change)))
    except ServerSelectionTimeoutError:
        print("MongoDB connection timeout. Check the connection settings.")
        return

@socketio.on("connect")
def on_connect():
    if not hasattr(on_connect, "_watcher_started") or not on_connect._watcher_started:
        on_connect._watcher_started = True
        socketio.start_background_task(watch_changes)


if __name__ == '__main__':
    socketio.run(app, host='127.0.0.1', port=10101, debug=True)
