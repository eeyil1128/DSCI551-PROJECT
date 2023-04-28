# DSCI551-PROJECT: Emulating Firebase

The repo develops a prototype system(database server) that emulates Firebase using Flask, WebSockets and MongoDB. The data this repo used is 2021 US Campground reservation data stored in MongoDB. This repo will allow users to use curl command to access the MongoDB data and see the real-time data stream change in the web app.

## Get Started
### 1. Start the poetry virtual environment
```poetry shell```


### 2. Run the RESTful server in the background

```python3 restful_server.py```


### 3. Run the real-time web app in the background. The web app runs at http://127.0.0.1:10102/

```python3 realtime_mongodb_app.py```


### 4. Run the data change log web app in the background. The web app runs at http://127.0.0.1:10101/

```python3 change_log_mongodb_app.py```


### 5. Run curl command
#### GET
```curl -X GET "http://localhost:5000/myPath?orderBy=regioncode&equalTo="AK""```

```curl -X GET "http://localhost:5000/myPath?orderBy=discount&startAt=0&endAt=5&limitToFirst=3"```


#### PUT (You can see the PUT command in http://127.0.0.1:10101/)
```curl -X PUT 'http://localhost:5000/myPath' -H 'Content-Type: application/json' -d '{"regioncode": "CA", "park" : "dsci551"}'```

```curl -X PUT 'http://localhost:5000/myPath/66be58c0-6d1f-4923-8735-879efcbb0c03' -H 'Content-Type: application/json' -d '{"regioncode": "NY"}'```

```curl -X POST 'http://127.0.0.1:5000/2021Reservation/bca72357-5824-4484-9eac-a824f5d00600/discount' -d '"10"' -H 'Content-Type: application/json'```     


#### POST (You can see the POST command in http://127.0.0.1:10101/)
```curl -X POST 'http://127.0.0.1:5000/2021Reservation' -d '{"historicalreservationid":"bca72357-5824-4484-9eac-a824f5d00600", "regioncode":"CA"}' -H 'Content-Type: application/json'```

```curl -X POST 'http://127.0.0.1:5000/2021Reservation/bca72357-5824-4484-9eac-a824f5d00600' -d '{"discount":0,"inventorytype":"CAMPING"}' -H 'Content-Type: application/json'```


#### PATCH (You can see the PATCH command in http://127.0.0.1:10101/)
```curl -X PATCH 'http://127.0.0.1:5000/2021Reservation/bca72357-5824-4484-9eac-a824f5d00600' -d '{"inventorytype":"ACTIVITYPASS","park":"post_park"}' -H 'Content-Type: application/json'```


#### DELETE (You can see the DELETE command in http://127.0.0.1:10101/)
```curl -X DELETE 'http://127.0.0.1:5000/2021Reservation/32b0cad7-8443-51e7-a1ea-d50fbb4a0050'```

```curl -X DELETE 'http://127.0.0.1:5000/2021Reservation/bca72357-5824-4484-9eac-a824f5d00600/regioncode'```

