python setup.py install

The UserGrid python library consists of a single class that can be used to authenticate against a UserGrid 1.x instance and perform any operations the authenticated user is authorized to do.

Installation

python setup.py install

It is recommended that you create a virtualenv for any project that needs this library and install in the virtualenv rather than system-wide


Usage

Here's an example of logging in with the client_id credentials - that is, trusted access to the entirety of the application:

~~~
from usergrid import UserGrid

ug = UserGrid(host="usergridhost.anywhere.com", port="80", app="yourapp", org="yourorg")
ug.login(client_id="client_id", client_secret="client_secret")
~~~

From here you can use the get_entity, get_entities, collect_entities and post_entity to manipulate data.

~~~
eldorado_entity = ug.post_entity("/cars", data={'name':'El Dorado','color':'blue','wheels': ['one','two','three','four']})
ug.update_entity("/cars/{0}".format(eldorado_entity.uuid), data={'color':'purple','status'='freshly repainted'})

eldorado_entity = ug.get_entity("/cars/{0}".format(eldorado_entity.uuid))

page_of_cars = ug.get_entities("/cars")

page_of_blue_cars = ug.get_entities("/cars", ql="select * where color='blue')

all_cars = ug.collect_entities("/cars")

ug.delete_entity("/cars/{0}".format(eldorado_entity.uuid))
~~~

