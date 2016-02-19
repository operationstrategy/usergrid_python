# UserGrid1.x Python Library

This library lets you communicate with a UserGrid1.x server and do the following:

 * Authenticate as a user, admin or client application
 * CRUD operations on entities
 * Push binary file content to entities
 * Automatically collect all entities matching a query without needing to paginate yourself


For the Orange project, we needed a decent Python library for UserGrid. They didn't have an official one, so this was written. Here are some examples of what can be done:

```python
from usergrid import UserGrid

ug = UserGrid(host='ughost.somewhere.com',port='80',org='someorg',app='someapp')
ug.login(client_id='someid',client_secret='somesecret')
```

Once logged in, you can perform basic CRUD operations easily:

```python
eldorado_entity = ug.post_entity("/cars", data={'name':'El Dorado','color':'blue','wheels': ['one','two','three','four']})

ug.update_entity("/cars/{0}".format(eldorado_entity.uuid), data={'color':'purple','status'='freshly repainted'})

eldorado_entity = ug.get_entity("/cars/{0}".format(eldorado_entity.uuid))

page_of_cars = ug.get_entities("/cars")

page_of_blue_cars = ug.get_entities("/cars", ql="select * where color='blue')

all_cars = ug.collect_entities("/cars")

ug.delete_entity("/cars/{0}".format(eldorado_entity.uuid))
```


## Installation

To install, I would recommend creating a virtualenv for any project that uses this. Then clone this project and run this in the virtualenv:

```bash
python setup.py install
```

## Documentation

pass1 - document here until a formal document is created

##### UserGrid(host=None,port=None,org=None,app=None,client_id=None,client_secret=None,
##### &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;debug=False,autoreconnect=True)

 * host: usergrid host to connect to
 * port: port usergrid is listening on
 * app: app to connect to on UserGrid
 * org: org to connect to on UserGrid
 * client_id, client_secret: supply these to use the client application authentication
 * debug: print debug information
 * autoreconnect: whether to reauthenticate automatically if session expires

Creates an unauthenticated UserGrid object and returns it.

##### login(superuser=None,username=None,password=None,client_id=None,client_secret=None,
##### &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ttl=None)

 * superuser: if supplied, attempt to authenticate as this superuser
 * username: if supplied, attempt to authenticate as this user
 * password: needs to be supplied with either superuser or username
 * client_id, client_secret:  authenticate as this client application
 * ttl: session timeout in seconds. defaults to 7 days if not supplied.

Authenticates against the UserGrid host/port/app/org in the UserGrid object with the given credentials.

##### get_entity(endpoint,ql=None)

 * endpoint: the endpoint to fetch
 * ql: a ql query parameter to pass to usergrid
 
Retrieves a single entity from UserGrid. Returns a Python object representing the entity.


#### get_entities(endpoint, ql=None, cursor=None, limit=None)

 * endpoint: endpoint for entities to fetch
 * ql: ql query parameter to pass to UserGrid
 * cursor: pass the cursor on subsequent calls to page through results
 * limit: limit to number of results to return

Retrieves a set of entities from UserGrid matching the endpoint and ql. Returns a two-element array - the first is an array of entities as in get_entity above, the second is a cursor string to use on subsequent calls to page through the results.

#### collect_entities(endpoint, ql=None, limit=None)

 * endpoint: endpoint for entities to fetch
 * ql: ql query parameter to pass to UserGrid
 * limit: limit to number of results to return

Iteratively performs get_entities() calls, automatically using the cursors to collect and gather all the results from all the pages. Returns an array of the entity objects described in get_entity().

#### delete_entity(endpoint)

 * endpoint: entity to delete

Deletes an entity from UserGrid - can be used for entities or relationships, just pass the right endpoint in.

#### post_entity(endpoint, data)

 * endpoint: endpoint for collection to post entity in
 * data: object with data to post into entity

Posts a new entity into UserGrid.

#### update_entity(endpoint, data)

 * endpoint: endpoint of entity to update
 * data: data to update with

Updates the given entity with any fields in data. These need to be top-level - that is, if you need to change only a subfield's value, you'll need to fetch the entire field, change the subfield value, and then update using the entire field again. Example:

```python
# we want to fix the engine size for a car
> car = ug.get_entity("/cars/mycar")
> print movie

{
 'doors': 4,
 'name': 'mycard',
 'model': 'EL Dorado',
 'engine': {
    'size_litres': 5.7,
    'engine_type': 'v8'
 }
}

# but that size is wrong, it should be 5.4. To change that, we'll have to give the entire 'engine' block:
> ug.update_entity("/cars/mycar", data={'engine': {'size_litres': 5.4, 'engine_type': 'v8'}})
```

#### post_activity(endpoint, actor, verb, content, data=None)

 * endpoint: endpoint to post activity to. Should always be '/activities'
 * actor: actor block
 * verb: activity string verb
 * content: additional string content
 * data: optional additional data

Posts an activity. This adheres to a basic implementation of Activity Streams (http://activitystrea.ms/specs/json/1.0/). The actor should include these elements, based on the user performing the activity:

```
{
  "uuid": [uuid],
  "displayName": String,
  "username": String,
  "email": [email],
  "picture": [url]
}
```

The verb is a simple string, and the content is a simple string. Data is optional but can include additional information.


#### post_relationship(endpoint)

 * endpoint: the endpoint for the relationship you wish to create

Creates a relationship between two entities. Example:

```python
ug.post_relationship("/user/bob/owns/cars/eldorado")
```

This creates a relationship between user bob and the car eldorado, such that this will return the eldorado object:

```python
bobscar = ug.get_entity("/user/bob/owns/cars")
```

and this will return bob's entity:

```python
owner = ug.get_entity("/cars/eldorado/connecting/owns/users")
```

#### post_file(endpoint, filepath)

 * endpoint: the entity to attach the file to
 * filepath: path on disk for the file to upload

This uploads a file to UserGrid and associates it with the given entity. UG will determine the content-type automatically. If there is a file attached to an entity, UserGrid will add this block to the entity:

```python
file-metadata: {
   content-length: Integer,
   content-type: String,
   last-modified: timestamp
}
```

This indicates that there is a file attached to this entity. To retrieve this file, you GET the entity, but add an Accept: header indicating the content-type listed in the file-metadata block. The UserGrid library here doesn't include a convenience method to do this, yet, but with requests it would look like this:

```python
ug.post_file('/cars/eldorado', '/tmp/sweeteldorado_picture.jpg')

# now eldorado entity has a file-metadata block like this:
# file-metadata: {
#    content-length: 123456,
#    content-type: image/jpeg,
#    last-modified: 1455904899
# }
# So, we can fetch by using Accept: image/jpeg

url = "http://usergridhost.com/myorg/myapp/cars/eldorado"
r = requests.get(url, headers={'Accept': 'image/jpeg'}, stream=True)

if r.status_code == 200:
    with open('/tmp/picfile.jpg', 'wb') as f:
        for chunk in r.iter_content():
            f.write(chunk)
# contents of sweeteldorado_picture.jpg are now in /tmp/picfile.jpg
```


#### get_actor(user_id=None)

 * user_id: optional user_id to create actor block for. If none provided, uses currently authenticated user

Convenience method to get an actor block from a User entity.



