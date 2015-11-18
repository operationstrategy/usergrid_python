from __future__ import absolute_import
from __future__ import print_function
#!/usr/bin/python

__version__='0.1.1'

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


class MockUserGrid:
    expected_responses = {}

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
            debug=False):
        self.debug = debug
        self.host = host
        self.port = port
        self.org = org
        self.app = app
        self.client_id = client_id
        self.client_secret = client_secret

    def _debug(self, txt):
        if self.debug:
            print("UG_client:" + str(txt))

    def set_last_response(self, response):
        self.last_response = response

    def login(
            self,
            superuser=None,
            username=None,
            password=None,
            client_id=None,
            client_secret=None):
        self.access_token = "1234567890"

        if username:
            self.me = self.get_mock_user()

    def get_mock_user(self):
        return {
            "uuid": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
            "type": "users",
            "name": "mock.user",
            "created": 1442347521177,
            "modified": 1446535640630,
            "username": "mock.user",
            "email": "mock.user@bigmirrorlabs.com",
            "activated": true,
            "picture": "http://www.gravatar.com/avatar/eced2b67a2ec3d29c561d1db58ef1d4e",
            "metadata": {
                "path": "/users/aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                "sets": {
                    "rolenames": "/users/aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa/roles",
                    "permissions": "/users/aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa/permissions"
                },
                "connections": {
                    "my": "/users/aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa/my",
                    "owns": "/users/aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa/owns"
                },
                "collections": {
                    "activities": "/users/aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa/activities",
                    "devices": "/users/aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa/devices",
                    "feed": "/users/aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa/feed",
                    "groups": "/users/aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa/groups",
                    "roles": "/users/aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa/roles",
                    "following": "/users/aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa/following",
                    "followers": "/users/aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa/followers"
                }
            },
            "ourpicks_channel": "sxm_default_ourpicks"
        }

    def collect_entities(self, endpoint, ql=None, limit=None):
        return expected_responses["{0}?ql={1}&limit={2}".format(endpoint, ql, limit)]

    def std_headers(self):
        headers = {}
        headers['user-agent'] = 'python usergrid client v.{0}'.format(__version__)
        headers['Accept'] = 'application/json'
        headers['Authorization'] = "Bearer {0}".format(self.access_token)
        return headers

    def process_entities(self, endpoint, method, ql=None, limit=None):
        page_entities, cursor = self.collect_entities(endpoint, ql=ql, limit=limit)
        # process these entities
        for entity in page_entities:
            method(entity)
        # changed get_entities to collect_entities so mock doesn't have to deal with cursors

    def get_entities(self, endpoint, cursor=None, ql=None, limit=None):
        return [expected_responses["{0}?ql={1}&limit={2}&cursor={3}".format(endpoint, ql, limit, cursor)], cursor + 1]
        # here we are assuming cursor is mocked as just an integer

    def get_entity(self, endpoint, ql=None):
        entities, cursor = self.get_entities(endpoint, ql=ql)
        if entities:
            entity = entities[0]
            return entity
        return None

    def delete_entity(self, endpoint):
        print("not yet implemented in mock")
        pass

    def post_entity(self, endpoint, data):
        data['uuid'] = uuid.uuid1
        expected_responses[endpoint] = data
        return data

    # maybe should pass in uuid, as a failsafe, rather than rely on endpoint
    def update_entity(self, endpoint, data):
        old_data = expected_responses[endpoint]
        for key in list(data.keys()):
            old_data[key] = data[key]
        expected_responses[endpoint] = old_data

    # ? Should this autocreate /users/me/activities
    def post_activity(self, endpoint, actor, verb, content, data=None):
        post_data = {"actor": actor, "verb": verb, "content": content}
        if data:
            post_data.update(data)
        post_data['uuid'] = uuid.uuid1
        expected_responses[endpoint] = post_data

    def get_connections(self, entity):
        print("Not yet implemented in mock")
        pass


    # seperate method since we don't need data...
    def post_relationship(self, endpoint):
        print("Not yet implemented in mock")
        # would need to pull appart endpoint to look up things?!?!!

    def post_file(self, endpoint, filepath):
        print("Not yet implemented in mock")

# These are some collection-aware utility functions
    def get_actor(self, user_id=None):
        return self.get_mock_user()

    def get_actor_from_user(self, user):
        return self.get_mock_user()

    def print_user(self, user):
        print("username\tuuid")
