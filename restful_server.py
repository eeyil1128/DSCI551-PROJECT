

from flask import Flask, jsonify, request
import pymongo
from bson import ObjectId
import uuid
import urllib.parse
import json

app=Flask(__name__)
app.config['JSONIFY_MIMETYPE'] = 'application/json'
#app.before_request(lambda: request.headers.setdefault('Content-Type', 'application/json'))

client=pymongo.MongoClient('mongodb+srv://shuijing1996:Zshui1996!@dsci551.dgblqjz.mongodb.net/',
                           serverSelectionTimeoutMS=600000)
db = client.dsci551
collection=db["2021Reservation"]

@app.route('/', defaults={'myPath': ''})


########### GET
@app.route('/<path:myPath>', methods=['GET'])

def get_reservations(myPath):
    
    query={}
    if 'orderBy' in request.args:
        field=request.args.get('orderBy')
        if field=="$key":
            field="historicalreservationid"
        elif field=='$value':
            raise ValueError ('Please specify an attribute.')

        #create proper index to support orderby
        collection.create_index([(field, pymongo.ASCENDING)])
        
        equal_to = request.args.get('equalTo')
        start_at = request.args.get('startAt')
        end_at = request.args.get('endAt')

        if field in ['totalbeforetax', 'discount', 'totalpaid']:
            if equal_to is not None:
                equal_to = float(equal_to)
            if start_at is not None:
                start_at = float(start_at)
            if end_at is not None:
                end_at = float(end_at)

        if equal_to is not None:
            query[field]=equal_to
        elif start_at is not None and end_at is not None:
            query[field]={"$gte":start_at, "$lte":end_at}
        elif start_at is not None:
            query[field]={"$gte":start_at}
        elif end_at is not None:
            query[field]={"$lte":end_at}
        
        print(query)
        if 'limitToFirst' in request.args:
            limit_first = request.args.get('limitToFirst')
            results = collection.find(query).sort([(field,pymongo.ASCENDING)]).limit(int(limit_first))
        elif 'limitToLast' in request.args:
            limit_last = request.args.get('limitToLast')
            results = collection.find(query).sort([(field,pymongo.DESCENDING)]).limit(int(limit_last))
        else:
            results = collection.find(query)

    else:
        key, value = next(request.args.items())
        if key=='limitToFirst':
            results = collection.find({}).limit(int(value))
        else:
            results = collection.find({}).sort([(_id,pymongo.DESCENDING)]).limit(int(value))


    result_list=[]
    for result in results:
        result['_id'] = str(result['_id'])
        result_list.append(result)      
    print(result_list)

    return jsonify(result_list)



########### PUT
@app.route('/<path:myPath>', methods=['PUT'])
def put_reservations(myPath):
    
    path=request.path
    values=request.get_json()

    #add a new reservation
    if path.endswith('myPath'):
        unique_id=str(uuid.uuid4())#randomly generated a unique historicalreservationid
        result=collection.insert_one({'historicalreservationid': unique_id, **values})
        
    #update an existing reservation
    else:
       unique_id=path.split("/")[-1]
       values['historicalreservationid']=unique_id
       result=collection.replace_one({"historicalreservationid": unique_id}, values)#overwrite

    #check if update/upload is successful
    if result.acknowledged:
        results=collection.find({'historicalreservationid':unique_id})
        result_list=[]
        for result in results:
            result['_id'] = str(result['_id'])
            result_list.append(result)
        return jsonify(result_list)
    else:
        print("Upload failed")
        return jsonify({'error': 'Upload failed'})


########### POST
# 1.Create a new document(must provide new historicalreservationid)
@app.route('/<string:collection_name>', methods=['POST'])
def post_new_order(collection_name):
    # Decode the URL-encoded collection_name parameter
    collection_name = urllib.parse.unquote(collection_name, encoding='utf-8')
    # Get the collection object
    collection = getattr(db, collection_name)
    # Get data
    content_type = request.headers.get('Content-Type')
    if content_type == 'application/json':
        data = request.get_json()
    else:
        data = request.form.to_dict()       
    if not data or "historicalreservationid" not in data:
        return jsonify({"message":"Missing id in request body"})
    reservation_id = data['historicalreservationid']
    if collection.count_documents({"historicalreservationid":reservation_id}) > 0:
        return jsonify({"message":f"id {reservation_id} already exists"})
    result = collection.insert_one(data)
    if result.acknowledged:
        new_reservation = collection.find_one(data)
        new_reservation['_id'] = str(new_reservation['_id'])
        return jsonify(new_reservation)
# 2.Create a new attribute for one reservation
@app.route('/<string:collection_name>/<string:reservation_id>', methods=['POST'])
def post_new_attribute(collection_name, reservation_id):
    # Decode the URL-encoded collection_name and reservation_id parameter
    collection_name = urllib.parse.unquote(collection_name, encoding='utf-8')
    reservation_id = urllib.parse.unquote(reservation_id, encoding='utf-8')
    # Get the collection object
    collection = getattr(db, collection_name)
    # Get data
    content_type = request.headers.get('Content-Type')
    if content_type == 'application/json':
        data = request.get_json()
    else:
        data = request.form.to_dict()   
    if not data:
        return jsonify({"message":"Please provide valid json data"})
    else:
        result = collection.update_one({"historicalreservationid":reservation_id},{"$set":data}) 
        if result.modified_count == 0:
            return jsonify({"message":f"{reservation_id} not found"})
        else:
            updated_reservation = collection.find_one({"historicalreservationid":reservation_id})
            updated_reservation['_id'] = str(updated_reservation['_id'])
            return jsonify(updated_reservation)
# 3.Create a new value for an attribute(cover)(update)
@app.route('/<string:collection_name>/<string:reservation_id>/<string:sub_key>', methods=['POST'])
def post_new_value(collection_name, reservation_id, sub_key):
    # Decode the URL-encoded collection_name, reservation_id and sub_key parameter
    collection_name = urllib.parse.unquote(collection_name, encoding='utf-8')
    reservation_id = urllib.parse.unquote(reservation_id, encoding='utf-8') 
    sub_key = urllib.parse.unquote(sub_key, encoding='utf-8')   
    # Get the collection object
    collection = getattr(db, collection_name)
    # Get data
    content_type = request.headers.get('Content-Type')
    if content_type == 'application/json':
        data = request.get_json()
    else:
        data = [k for k in request.form.to_dict().keys()][0]
        #data = request.form.to_dict()
    if not data:
        return jsonify({"message":"Please provide valid json data"})
    else:
        result = collection.update_one({"historicalreservationid":reservation_id},{"$set":{sub_key:data}})
        if result.modified_count == 0:
            return jsonify({"message":f"{reservation_id} not found"})
        else:
            updated_reservation = collection.find_one({"historicalreservationid":reservation_id})
            updated_reservation['_id'] = str(updated_reservation['_id'])
            return jsonify(updated_reservation)


########### Patch
# Update one or more key-value pairs (attributes)
@app.route('/<string:collection_name>/<string:reservation_id>', methods=['PATCH']) 
def patch_order_info(collection_name, reservation_id):
    # Decode the URL-encoded collection_name and order_id parameter
    collection_name = urllib.parse.unquote(collection_name, encoding='utf-8')
    reservation_id = urllib.parse.unquote(reservation_id, encoding='utf-8')
    # Get the collection object
    collection = getattr(db, collection_name)
    # Get data
    content_type = request.headers.get('Content-Type')
    if content_type == 'application/json':
        data = request.get_json()
    else:  # if we don't specify the content type explicitly, curl will use the default content type of 'application/x-www-form-urlencoded'
        data = request.form.to_dict() # -d 'column1=hi&newcolumn2=hello' will be sent as form data
    if not data:
        return jsonify({"message":"Please provide valid data"})
    else:
        result = collection.update_one({"historicalreservationid":reservation_id},{"$set":data}) #update if exists, otherwise insert
        if result.modified_count == 0:
            return jsonify({"message":f"{reservation_id} not found"})
        else:
            updated_reservation = collection.find_one({"historicalreservationid":reservation_id})
            updated_reservation['_id'] = str(updated_reservation['_id'])
            return jsonify(updated_reservation)


########### Delete
# 1.Delete an entire reservation by reservation_id
@app.route('/<string:collection_name>/<string:reservation_id>', methods=['DELETE'])
def delete_order(collection_name, reservation_id): # collection_name may has spaces(using %20 in curl commands)
    # Decode the URL-encoded collection_name and order_id parameter
    collection_name = urllib.parse.unquote(collection_name, encoding='utf-8')
    reservation_id = urllib.parse.unquote(reservation_id, encoding='utf-8')
    # Get the collection object
    collection = getattr(db, collection_name)
    result = collection.delete_one({"historicalreservationid":reservation_id})
    if result.deleted_count == 1:
        return jsonify({"message":f"{reservation_id} deleted"})
    else:
        return jsonify({"message":f"{reservation_id} not found"})
# 2.Delete a key-value pair (attribute) of an reservation
@app.route('/<string:collection_name>/<string:reservation_id>/<string:sub_key>', methods=['DELETE']) #sub_key: not real sub_key
def delete_subkey(collection_name, reservation_id, sub_key):
    # Decode the URL-encoded collection_name, order_id and sub_key parameter
    collection_name = urllib.parse.unquote(collection_name, encoding='utf-8')
    reservation_id = urllib.parse.unquote(reservation_id, encoding='utf-8') 
    sub_key = urllib.parse.unquote(sub_key, encoding='utf-8')   
    # Get the collection object
    collection = getattr(db, collection_name)
    found_doc = collection.find_one({"historicalreservationid":reservation_id})
    if not found_doc:
        return jsonify({"message":f"{reservation_id} not found"})
    else:
        if sub_key not in [key for key in found_doc.keys()]:
            return jsonify({"message":f"{sub_key} not valid"})
        else:
            result = collection.update_one({"historicalreservationid":reservation_id},{"$unset":{sub_key:None}})
            if result.modified_count == 1:
                return jsonify({"message":f"{sub_key} of {reservation_id} deleted"})
            else:
                return jsonify({"message":"Error"})




if __name__ == '__main__':
    app.run(debug=True)


#shuijing1996:Zshui1996!
#@dsci551.dgblqjz.mongodb.net



#curl -X PUT 'http://localhost:5000/myPath' -H 'Content-Type: application/json' -d '{"regioncode": "CA", "regiondescription":"California", "parentlocationid":99999}'
#curl -X PUT 'http://localhost:5000/myPath/d739c6a4-8884-4ad0-950e-85cba89e57e0' -H 'Content-Type: application/json' -d '{"regioncode": "NY"}'

#curl -X GET "http://localhost:5000/myPath?orderBy=regioncode&equalTo="AK""
#curl -X GET "http://localhost:5000/myPath?orderBy="historicalreservationid"&equalTo=bca72357-5824-4484-9eac-a824f5c00622"
#curl -X GET "http://localhost:5000/myPath?orderBy=\$key&equalTo="ca72357-5824-4484-9eac-a824f5c00622""





