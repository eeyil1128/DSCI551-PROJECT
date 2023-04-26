# DSCI551-PROJECT: Emulating Firebase

The repo develops a prototype system that emulates the interface of Firebase. The data this repo used is 2021 US Camground reservation data stored in MongoDB. This repo will allow user to use curl command to access the MongoDB data and see the real-time data stream change in the web app.

## Get Started
### 1. Run the restful server in the background

```python3 restful_server.py```


### 2. Run the real-time web app in the background. The web app runs at http://127.0.0.1:10102/

```python3 realtime_mongodb_app.py```


### 3. Run the data change log web app in the background. The web app runs at http://127.0.0.1:10101/

```python3 change_log_mongodb_app.py```


### 4. Run curl command
#### GET
curl -X GET "http://localhost:5000/myPath?orderBy=regioncode&equalTo="AK""

curl -X GET "http://localhost:5000/myPath?orderBy=discount&startAt=0&endAt=5&limitToFirst=3"


#### PUT
curl -X PUT 'http://localhost:5000/myPath' -H 'Content-Type: application/json' -d '{"regioncode": "CA", "park" : "dsci551"}'

curl -X PUT 'http://localhost:5000/myPath/930b4213-90dd-49ce-a89d-b778813924d9' -H 'Content-Type: application/json' -d '{"regioncode": "NY"}'


#### POST
curl -X POST 'http://127.0.0.1:5000/2021Reservation' -d '{"historicalreservationid":"bca72357-5824-4484-9eac-a824f5d00600", "regioncode":"CA"}' -H 'Content-Type: application/json'

curl -X POST 'http://127.0.0.1:5000/2021Reservation' -d '{"tax":1,"regioncode":"CA"}' -H 'Content-Type: application/json'


#### PATCH
curl -X PATCH 'http://127.0.0.1:5000/2021Reservation/bca72357-5824-4484-9eac-a824f5d00600' -d '{"inventorytype":"ACTIVITYPASS","park":"post_park"}' -H 'Content-Type: application/json'


#### DELETE
curl -X DELETE 'http://127.0.0.1:5000/2021Reservation/32b0cad7-8443-51e7-a1ea-d50fbb4a0050'

curl -X DELETE 'http://127.0.0.1:5000/2021Reservation/bca72357-5824-4484-9eac-a824f5d00600/regioncode'

