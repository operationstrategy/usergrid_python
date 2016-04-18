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
    responses = {}
    # Mapping of query to respones
    # eg { '/channels/123456': { <channel data> },
    #      '/stories/9999/has_intro/audioclips' : [{ <audioclip data> }]

    # note in testing you need to be aware of what you expect to get back from UG so you put the right thing in

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

    def add_response_by_key(self, key, data):
        print("Adding: {0} -> {1}".format(key,data))
        if not isinstance(data, list):
            self.responses[key] = [data]
        else:
            self.responses[key] = data

    def add_response(self, endpoint, ql=None, cursor=None, limit=None, data=None):
        key = "{0}?ql={1}&limit={2}&cursor={3}".format(endpoint, ql, limit, cursor)
        self.add_response_by_key(key, data)

    def get_response_by_key(self, key):
        if key in self.responses:
            return self.responses[key]
        else:
            return None

    def get_response(self, endpoint, ql=None, cursor=None, limit=None, data=None):
        key = "{0}?ql={1}&limit={2}&cursor={3}".format(endpoint, ql, limit, cursor)
        return self.get_response_by_key(key)

    def std_headers(self):
        return None

    def process_entities(self, endpoint, method, ql=None, limit=None):
        all_entities = self.collect_entities(endpoint, ql=ql, limit=limit)
        if limit and limit < len(all_entities):
            all_entities = all_entities[0:limit]
        # process these entities
        for entity in all_entities:
            method(entity)

    def collect_entities(self, endpoint, ql=None, limit=None):
        entities = self.get_response(endpoint, ql=ql, limit=limit)
        if limit and limit < len(entities):
            entities = entities[0:limit]

    def get_entities(self, endpoint, cursor=None, ql=None, limit=None):
        if not limit:
            limit = 10
        response = self.get_response(endpoint, ql=ql, limit=limit, cursor=cursor)
        return (response[0:limit],"newcursor")

    def get_entity(self, endpoint, ql=None):
        response = self.get_response(endpoint, ql=ql)
        return response[0]

    def delete_entity(self, endpoint):
        print("Not yet implemented")
        return None

    def post_entity(self, endpoint, data):
        print("Not yet implemented")
        return None

    # maybe should pass in uuid, as a failsafe, rather than rely on endpoint
    def update_entity(self, endpoint, data):
        print("Not yet implemented")

    # ? Should this autocreate /users/me/activities
    def post_activity(self, endpoint, actor, verb, content, data=None):
        print("Not yet implemented")

    def get_connections(self, entity):
        print("Not yet implemented in mock")
        pass


    # seperate method since we don't need data...
    def post_relationship(self, endpoint):
        return self.get_entity(endpoint)

    def post_file(self, endpoint, filepath):
        print("Not yet implemented in mock")

# These are some collection-aware utility functions
    def get_actor(self, user_id=None):
        return self.get_mock_user()

    def get_actor_from_user(self, user):
        return self.get_mock_user()

    def print_user(self, user):
        print("username\tuuid")
