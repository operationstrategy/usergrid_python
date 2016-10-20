from __future__ import absolute_import
from __future__ import print_function
#!/usr/bin/python

__version__='0.1.3'

import requests
import json
import datetime
import calendar
import time
import os
import sys
import traceback

# TODO: need to include entity not exists errors, etc. - raise them when
# problem occurs


class UserGrid:
    org = "SXM"
    app = "ORANGE"
    host = "backend.bigmirrorlabs.com"
    port = "80"

    client_id = "b3U6zqN2esf9EeSpD1E1ffgwnQ"
    client_secret = "b3U6AkxKbPNc81NfFzWvFYrDZ1IvJEY"

    app_endpoint = None

    access_token = None
    current_user = None

    autoreconnect = False
    last_login_info = {}

    me = None

    last_response = None

    # todo: pass in config, or call setters
    def __init__(
            self,
            host=None,
            port=None,
            org=None,
            app=None,
            client_id=None,
            client_secret=None,
            debug=False,
            autoreconnect=False,
            use_compression=True):
        if host:
            self.host = host
        if port:
            self.port = port
        if org:
            self.org = org
        if app:
            self.app = app
        if client_id:
            self.client_id = client_id
        if client_secret:
            self.client_secret = client_secret
        self.use_compression = use_compression
        self.autoreconnect = autoreconnect
        self.app_endpoint = "http://{0}:{1}/{2}/{3}".format(
            self.host, self.port, self.org, self.app)
        self.management_endpoint = "http://{0}:{1}/management".format(
            self.host, self.port)
        self.debug = debug

    def _debug(self, txt):
        if self.debug:
            print("UG_client:" + str(txt))

    def set_last_response(self, response):
        self.last_response = response

    def reconnect(self):
        self.login(**self.last_login_info)

    def login(
            self,
            superuser=None,
            username=None,
            password=None,
            client_id=None,
            client_secret=None,
            ttl=None):
        endpoint = self.app_endpoint
        if client_id:
            self.client_id = client_id
            self.last_login_info['client_id'] = client_id
        if client_secret:
            self.client_secret = client_secret
            self.last_login_info['client_secret'] = client_secret
        if username:
            self.username = username
            self.last_login_info['username'] = username
        if superuser:
            self.superuser = superuser
            endpoint = self.management_endpoint
            self.last_login_info['superuser'] = superuser
        if password:
            self.password = password
            self.last_login_info['password'] = password
        # login as super user
        data = {}
        if not username and not superuser:
            self.grant_type = "client_credentials"
            data = {"grant_type": "client_credentials",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret}
        else:
            self.grant_type = "password"
            data = {"grant_type": "password",
                    "password": self.password}

            if username:
                data['username'] = self.username
            if superuser:
                print("logging in as super user")
                data['username'] = self.superuser
        if ttl:
            data['ttl'] = ttl
            self.last_login_info['ttl'] = ttl

        self._debug("login: grant_type: " + self.grant_type)
        self._debug("login: data: " + str(data))

        r = requests.post(endpoint + "/token", data=data)
        self.set_last_response(r)
        r.raise_for_status()

        json = r.json()

        self.access_token = json['access_token']
        self.token_response = json
        if username:
            #self.me = json['entities'][0]
            self.me = json['user']

    def std_headers(self):
        headers = {}
        headers['user-agent'] = 'python usergrid client v.{0}'.format(__version__)
        headers['Accept'] = 'application/json'
        headers['Authorization'] = "Bearer {0}".format(self.access_token)
        if self.use_compression:
            headers['Accept-Encoding'] = "gzip, deflate"
        return headers

    def get_full_endpoint(self, path):
        if '/' in path[0]:
            path = path[1:]
        full = "{0}/{1}".format(self.app_endpoint, path)
        return full

    def collect_entities(self, endpoint, ql=None, limit=None):
        entities = []
        page_entities, cursor = self.get_entities(endpoint, ql=ql, limit=limit)
        entities.extend(page_entities)
        count = len(page_entities)

        while cursor and (len(page_entities) > 0):
            page_entities, cursor = self.get_entities(
                endpoint, ql=ql, cursor=cursor, limit=limit)
            entities.extend(page_entities)
            count = count + len(page_entities)

        return entities

    def process_entities(self, endpoint, method, ql=None, limit=None):
        page_entities, cursor = self.get_entities(endpoint, ql=ql, limit=limit)
        # process these entities
        for entity in page_entities:
            method(entity)

        while cursor:
            page_entities, cursor = self.get_entities(
                endpoint, ql=ql, cursor=cursor, limit=limit)
            for entity in page_entities:
                method(entity)

    def get_entities(self, endpoint, cursor=None, ql=None, limit=None):
        try:
            # assumes end point delivers page(s) of entities
            if cursor or ql or limit:
                endpoint = endpoint + "?"
            if limit:
                endpoint = endpoint + "limit=" + str(limit) + "&"
            if ql:
                endpoint = endpoint + "ql=" + ql + "&"
            if cursor:
                endpoint = endpoint + "cursor=" + cursor + "&"
            # print endpoint
            r = requests.get(
                self.get_full_endpoint(endpoint),
                headers=self.std_headers())
            self.set_last_response(r)
            # print r.text.encode('utf-8')
            r.raise_for_status
            response = r.json()
            self._debug(response)
            if 'exception' in response:
                # check for expired_token and autoreconnect
                if ('expired_token' in response['error'] or 'auth_invalid' in response['error']) and self.autoreconnect:
                    self.reconnect()
                    r = requests.get(
                            self.get_full_endpoint(endpoint),
                            headers=self.std_headers())
                    self.set_last_response(r)
                    r.raise_for_status
                    response = r.json()
                else:
                    print(response['error_description'])
                    return [[], None] # TODO: RAISE EXCEPTION
            if 'entities' in response or 'list' in response:
                if 'entities' in response:
                    entities = response['entities']
                else:
                    entities = response['list']
                if 'cursor' in response:
                    cursor = response['cursor']
                else:
                    cursor = None
                return [entities, cursor]
            else:
                return [[], None]
        except:
            print("Exception")
            traceback.print_exc(file=sys.stdout)
            if r:
                print("Response text: {0}".format(r.text))
                print("Response status: {0}".format(r.status_code))
            else:
                print(r)

            print("endpoint: {0}".format(endpoint))
            print("cursor: {0}".format(cursor))
            print("ql: {0}".format(ql))
            print("limit: {0}".format(limit))
            return [[], None]

    def get_entity(self, endpoint, ql=None):
        entities, cursor = self.get_entities(endpoint, ql=ql)
        if entities:
            entity = entities[0]
            return entity
        return None

    def delete_entity(self, endpoint):
        r = requests.delete(
            self.get_full_endpoint(endpoint),
            headers=self.std_headers())
        self.set_last_response(r)
        r.raise_for_status
        response = r.json()
        if 'exception' in response:
            # check for expired_token and autoreconnect
            if ('expired_token' in response['error'] or 'auth_invalid' in response['error']) and self.autoreconnect:
                self.reconnect()
                r = requests.delete(
                        self.get_full_endpoint(endpoint),
                        headers=self.std_headers())
                self.set_last_response(r)
                r.raise_for_status
                response = r.json()
            else:
                print(response['error_description'])
                return None # TODO : raise exception
        return response

    def post_entity(self, endpoint, data):
        r = requests.post(
            self.get_full_endpoint(endpoint),
            headers=self.std_headers(),
            data=json.dumps(data))
        self.set_last_response(r)
        r.raise_for_status
        response = r.json()
        if 'exception' in response:
            if ('expired_token' in response['error'] or 'auth_invalid' in response['error']) and self.autoreconnect:
                self.reconnect()
                r = requests.post(
                        self.get_full_endpoint(endpoint),
                        headers=self.std_headers(),
                        data=json.dumps(data))
                self.set_last_response(r)
                r.raise_for_status
                response = r.json()
            else:
                print(response['error_description'])
                return None
        return response['entities'][0]

    # maybe should pass in uuid, as a failsafe, rather than rely on endpoint
    def update_entity(self, endpoint, data):
        r = requests.put(
            self.get_full_endpoint(endpoint),
            headers=self.std_headers(),
            data=json.dumps(data))
        self.set_last_response(r)
        r.raise_for_status
        response = r.json()
        if 'exception' in response:
            if ('expired_token' in response['error'] or 'auth_invalid' in response['error']) and self.autoreconnect:
                self.reconnect()
                r = requests.put(
                        self.get_full_endpoint(endpoint),
                        headers=self.std_headers(),
                        data=json.dumps(data))
                self.set_last_response(r)
                r.raise_for_status
                response = r.json()
            else:
                print(response['error_description'])
                return None
        return response['entities'][0]

    # ? Should this autocreate /users/me/activities
    def post_activity(self, endpoint, actor, verb, content, data=None):
        post_data = {"actor": actor, "verb": verb, "content": content}
        if data:
            post_data.update(data)
        r = requests.post(
            self.get_full_endpoint(endpoint),
            data=json.dumps(post_data),
            headers=self.std_headers())
        self.set_last_response(r)
        r.raise_for_status
        response = r.json()
        if 'exception' in response:
            if ('expired_token' in response['error'] or 'auth_invalid' in response['error']) and self.autoreconnect:
                self.reconnect()
                r = requests.post(
                        self.get_full_endpoint(endpoint),
                        data=json.dumps(post_data),
                        headers=self.std_headers())
                self.set_last_response(r)
                r.raise_for_status
                response = r.json()
            else:
                print(response['error_description'])
                return None
        return response

    def get_connections(self, entity):
        if 'metadata' in list(entity.keys()) and 'connections' in list(entity[
                'metadata'].keys()):
            return entity['metadata']['connections']
        return None

    # seperate method since we don't need data...
    def post_relationship(self, endpoint):
        r = requests.post(
            self.get_full_endpoint(endpoint),
            headers=self.std_headers())
        self.set_last_response(r)
        r.raise_for_status
        response = r.json()
        if 'exception' in response:
            if ('expired_token' in response['error'] or 'auth_invalid' in response['error']) and self.autoreconnect:
                self.reconnect()
                r = requests.post(
                        self.get_full_endpoint(endpoint),
                        headers=self.std_headers())
                self.set_last_response(r)
                r.raise_for_status
                response = r.json()
            else:
                print(response['error_description'])
                return None
        return response

    def post_file(self, endpoint, filepath):
        filename = filepath.split("/")[-1]

        headers = self.std_headers()
#	headers['Content-Type'] = 'application/x-www-form-urlencoded'
#	headers['Content-Type'] = 'multipart/form-data'

        files = {'file': open(filepath, 'rb'), 'name': filename}

        r = requests.post(
            self.get_full_endpoint(endpoint),
            headers=headers,
            files=files)
        self.set_last_response(r)
        r.raise_for_status
        response = r.json()
        if 'exception' in response:
            if ('expired_token' in response['error'] or 'auth_invalid' in response['error']) and self.autoreconnect:
                self.reconnect()
                r = requests.post(
                        self.get_full_endpoint(endpoint),
                        headers=headers,
                        files=files)
                self.set_last_response(r)
                r.raise_for_status
                response = r.json()
            else:
                print(response['error_description'])
                return None
        return response

# These are some collection-aware utility functions
    def get_actor(self, user_id=None):
        if not user_id:
            user = self.get_entity("/users/me")
        else:
            user = self.get_entity("/users/{0}".format(user_id))
        if not user:
            users, cursor = self.get_entities(self.get_full_endpoint(
                "/users"), ql="select * where uuid='{0}*' or username='{0}*' or name='{0}*'")
            if users and len(users) > 0:
                user = users[0]
        if user:
            actor = self.get_actor_from_user(user)
        return None

    def get_actor_from_user(self, user):
        if 'name' not in list(user.keys()):
            name = user['username']
        else:
            name = user['name']
        if 'picture' not in list(user.keys()):
            picture = ''
        else:
            picture = user['picture']
        if 'email' not in list(user.keys()):
            email = ''
        else:
            email = user['email']
        actor = {
            "uuid": user['uuid'],
            "displayName": name,
            "username": user['username'],
            "email": email,
            "picture": picture}
        return actor

    def print_user(self, user):
        print("{0}\t{1}".format(user['username'], user['uuid']))
