## segmind-task
This repo contains assignment for segmind.
A python flask application for creating and maintaining gcp instances in real time.

## Application setup

### Google Cloud
1. Make a google cloud account.
2. Create a project. (Current Name : segmind-base)
3. Create a service account, and give appropriate permissions.
4. Download the auth json provided by google.

### Running Application
* Create environment(Inside the project folder)
``` 
   python3 -m venv env
   source /env/activate
```

* Install Dependencies
``` 
    pip3 install -r requirements.txt
```

* Start server
```
    python3 runserver.py
```
### Curls
* Create a new instance
```bash
curl --location --request POST 'localhost:7000/gcp/create-instance' \
--header 'Content-Type: application/json' \
--data-raw '{
    "instanceName":"test-vm-22"
}'
```
* Delete the existing instance and create a image of that instance.
```bash
    curl --location --request PUT 'localhost:7000/gcp/delete-instance' \
--header 'Content-Type: application/json' \
--data-raw '{
    "instanceName":"test-vm-22",
    "imageName" : "image-224",
    "familyName" : "segmind-fam"
}'
```
* Restart the instance from image.
```bash
curl --location --request PUT 'localhost:7000/gcp/restart-instance' \
--header 'Content-Type: application/json' \
--data-raw '{
    "instanceName":"test-vm-22"
}'
```

### How it works?
* When creating a instance, flask application uses google-api-python-client to connect to gcp. 
And then it call a function for creating instance which by default `uses us-central1-a` as zone 
and create a `ubuntu-minimal-1804-bionic-v20201014` image and start a python server for which the 
startup script is present in `startup-script.py`, then it waits for the operation to get completed,
and logs list of instance in console.

* In delete call, first flask app stops the instance and then create the image and waits for 20 seconds
for creation of image as google is unable to identify the operation running for creating image, the it updates the database
for image and also updates the mapping table. There are two flows :
    1. If the instance is closed for the first time, it will simply create a row in image table and update mapping with the image id.
    2. If the instance is closed after restarting, it will create a entry in image table and map the new id with vm id in mapping table
    and also it will mark the earlier image as `is_dirty_resource`
    
* In restart call, the application first checks if the vm existed earlier, and if it existed it will get the vm id and
search for the image that was mapped last to that vm and create a vm with the respective image and start a python server.


### Future Scopes
* Use a schedular for closing all the dirty resources.
* As currently a single api call take time to keeping the request in a persistant queue,
such as rabbitmq.  


