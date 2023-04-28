import json
from pymongo import MongoClient
from bson.json_util import dumps
from flask_socketio import SocketIO
from flask import Flask, render_template

app = Flask(__name__)
socketio = SocketIO(app)

# connect to MongoDB.
client = MongoClient("mongodb+srv://shuijing1996:Zshui1996!@dsci551.dgblqjz.mongodb.net/?retryWrites=true&w=majority")
db = client.dsci551
collection = db['2021Reservation']

@app.route('/')
def index():
    return render_template("index.html")

# modify the mongodb data here, so when pass it to html java script, it will be easier to parse.
def modify_data(data):
    data_new = []
    # again here I only grab those columns/attributes. If a new column is added, it won't show here.
    key_ls = ['_id',
              'historicalreservationid',
              'regioncode',
              'park',
              'inventorytype',
              'tax',
              'totalbeforetax',
              'discount',
              'totalpaid',
              'sitetype',
              'usetype']

    for data_ix in data:
        data_new_ix = data_ix
        data_new_ix['_id'] = str(data_ix['_id']) #chang _id type from ObjectID to str
        missing_key_ls = [k for k in key_ls if k not in data_new_ix.keys()]
        for missing_k in missing_key_ls:
            data_new_ix[missing_k] = '' #change missing value in MongoDB from NaN to '''
        data_new.append(data_new_ix)
    return data_new
#--modify_data

# listen for change in MongoDB data, if a change is detected, grab the newest collection and send to html
def watch_changes():
    with collection.watch() as stream:
        while stream.alive:
            change = stream.try_next()
            if change is not None:
                    data = list(collection.find())
                    data_new = modify_data(data)
                    socketio.emit("change_data", json.loads(dumps(data_new)))

@socketio.on("connect")
def on_connect():
    # print out initial data.
    # without this line, the data will show on html ONLY when a change is made to MongoDB
    data = list(collection.find())
    data_new = modify_data(data)
    socketio.emit("change_data", json.loads(dumps(data_new)))

    # run the watch_changes in the background
    if not hasattr(on_connect, "_watcher_started") or not on_connect._watcher_started:
        on_connect._watcher_started = True
        socketio.start_background_task(watch_changes)

if __name__ == '__main__':
    socketio.run(app, host='127.0.0.1', port=10102, debug=True) #define port 10102
