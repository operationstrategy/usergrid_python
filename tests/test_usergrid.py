"""
UserGrid tests
"""
from unittest import TestCase
import requests
import requests_mock
from tests import read_json_file
from usergrid.usergrid import *
import logging
from unittest.mock import Mock
from unittest.mock import call
import os
import json

SESSION = requests.Session()
ADAPTER = requests_mock.Adapter()
SESSION.mount('mock', adapter=ADAPTER)

requests_mock.Mocker.TEST_PREFIX = 'test'


@requests_mock.mock()
class TestUserGrid(TestCase):
    """
    Ensures user grid calls behave as excepted
    """

    def setUp(self):
        """

        :return:
        """
        self.user_grid = UserGrid(
            host='usergrid.com',
            org='man',
            app='chuck',
            port=80,
            client_id='manchuck',
            client_secret='manbearpig',
            use_compression=True
        )
        logging.getLogger(UserGrid.__name__).disabled = True

    def test_it_should_get_entities(self, mock):
        """
        Ensures UG fetches all entities

        :param mock:
        :return:
        """
        entities_response = read_json_file('get_entities_response.json')
        mock.register_uri(
            "GET",
            "http://usergrid.com:80/man/chuck/users",
            json=entities_response
        )

        entities, actual_cursor = self.user_grid.get_entities('users')

        self.assertEqual(
            'LTU2ODc0MzQzOkhGOWVtalNoRWVhdmdvLTNqcmpZVWc',
            actual_cursor,
            'UserGrid get_entities did not return correct cursor'
        )

        expected_user_ids = [
            '5dc2e4ba-2f33-11e6-9880-47e38a0eed23',
            '69361b5a-2f33-11e6-9d6f-c7a4ebfb263a',
            '75ad7b8a-2f33-11e6-8d91-25e5758e7b14',
            '5dc2e4ba-2f33-11e6-9880-47e38a0eed23',
            '69361b5a-2f33-11e6-9d6f-c7a4ebfb263a',
            '5dc2e4ba-2f33-66e6-9880-47e38a0eed23',
            '69361b5a-7f33-11e6-9d6f-c7a4ebfb763a',
            '75ad7b8a-2f88-11e6-8d91-25e5758e7b14',
            '5dc2e9ba-2f33-11e6-9880-97e38a0eed23',
            '6936110a-2f33-11e6-9d6f-c7a4ebfb263a'
        ]

        actual_user_ids = []
        for user in entities:
            actual_user_ids.append(user['uuid'])

        self.assertEqual(
            expected_user_ids,
            actual_user_ids,
            'UserGrid get_entities did not return correct entities'
        )

    def test_it_should_get_entities_with_query_limit_and_cursor(self, mock):
        """
        Ensures get_entities works with cursor and query

        :param mock:
        :return:
        """
        entities_response = read_json_file('get_entities_response.json')
        mock.register_uri(
            "GET",
            "http://usergrid.com:80/man/chuck/users?ql=select * where name"
            " contains 'demo'&limit=10&cursor=foobar",
            json=entities_response
        )

        entities, actual_cursor = self.user_grid.get_entities(
            '/users',
            ql="select * where name contains 'demo'",
            limit=10,
            cursor="foobar"
        )

        self.assertEqual(
            'LTU2ODc0MzQzOkhGOWVtalNoRWVhdmdvLTNqcmpZVWc',
            actual_cursor,
            'UserGrid get_entities did not return correct cursor'
        )

        expected_user_ids = [
            '5dc2e4ba-2f33-11e6-9880-47e38a0eed23',
            '69361b5a-2f33-11e6-9d6f-c7a4ebfb263a',
            '75ad7b8a-2f33-11e6-8d91-25e5758e7b14',
            '5dc2e4ba-2f33-11e6-9880-47e38a0eed23',
            '69361b5a-2f33-11e6-9d6f-c7a4ebfb263a',
            '5dc2e4ba-2f33-66e6-9880-47e38a0eed23',
            '69361b5a-7f33-11e6-9d6f-c7a4ebfb763a',
            '75ad7b8a-2f88-11e6-8d91-25e5758e7b14',
            '5dc2e9ba-2f33-11e6-9880-97e38a0eed23',
            '6936110a-2f33-11e6-9d6f-c7a4ebfb263a'
        ]

        actual_user_ids = []
        for user in entities:
            actual_user_ids.append(user['uuid'])

        self.assertEqual(
            expected_user_ids,
            actual_user_ids,
            'UserGrid get_entities did not return correct entities'
        )

    def test_it_should_fetch_one_entity(self, mock):
        """
        Ensures one entity is returned

        :param mock:
        :return:
        """
        entities_response = read_json_file('get_entity_response.json')
        mock.register_uri(
            "GET",
            "http://usergrid.com:80/man/chuck/users/foo",
            json=entities_response
        )

        entity = self.user_grid.get_entity('/users/foo')

        self.assertEqual(
            '5dc2e4ba-2f33-11e6-9880-47e38a0eed23',
            entity['uuid'],
            'UserGrid get_entities did not return correct entities'
        )

        self.assertEqual(
            entities_response['entities'][0]['metadata']['connections'],
            self.user_grid.get_connections(entity),
            'UserGrid get_entities did not return connections for an entity'
        )

    def test_it_should_not_fetch_entities(self, mock):
        """
        Ensures an exception is thrown with a bad status code

        :param mock:
        :return:
        """
        entities_response = read_json_file('get_entity_not_found_response.json')
        mock.register_uri(
            "GET",
            "http://usergrid.com:80/man/chuck/users",
            json=entities_response,
            status_code=404
        )

        with self.assertRaises(UserGridException) as failed:
            self.user_grid.get_entities('users')

    def test_it_should_delete_entity(self, mock):
        """
        Ensures deleting entities works as expected

        :param mock:
        :return:
        """
        delete_response = read_json_file('delete_response.json')
        mock.register_uri(
            "DELETE",
            "http://usergrid.com:80/man/chuck/users/foo-bar",
            json=delete_response
        )

        deleted = self.user_grid.delete_entity('/users/foo-bar')

        self.assertEqual(
            delete_response,
            deleted,
            'UserGrid get_entities did not delete entity'
        )

    def test_it_should_post_entity(self, mock):
        """
        Ensures UserGrid posts an entity correctly

        :return:
        """
        def request_match(request):
            return (
                request.body ==
                '{"foo": "bar"}')

        post_response = read_json_file('post_response.json')
        mock.register_uri(
            "POST",
            "http://usergrid.com:80/man/chuck/users",
            json=post_response,
            additional_matcher=request_match
        )

        created = self.user_grid.post_entity('/users', {"foo": "bar"})

        self.assertEqual(
            post_response['entities'][0],
            created,
            'UserGrid get_entities did not create entity'
        )

    def test_it_should_put_entity(self, mock):
        """
        Ensures UG can update an entity

        :return:
        """
        def request_match(request):
            return (
                request.body ==
                '{"foo": "bar"}')

        put_response = read_json_file('put_response.json')
        mock.register_uri(
            "PUT",
            "http://usergrid.com:80/man/chuck/users",
            json=put_response,
            additional_matcher=request_match
        )

        created = self.user_grid.update_entity('/users', {"foo": "bar"})

        self.assertEqual(
            put_response['entities'][0],
            created,
            'UserGrid get_entities did not create entity'
        )

    def test_it_should_post_activity(self, mock):
        """
        Ensures that activity is posted correctly

        :param mock:
        :return:
        """
        # /users/me/activities
        def request_match(request):
            expected = {
                "actor": "manchuck",
                "verb": "put",
                "content": "updated",
                "foo": "bar"
            }

            actual = json.loads(request.body)
            return expected == actual

        post_response = read_json_file('post_response.json')
        mock.register_uri(
            "POST",
            "http://usergrid.com:80/man/chuck/users/me/activities",
            json=post_response,
            additional_matcher=request_match
        )

        created = self.user_grid.post_activity(
            '/users/me/activities',
            "manchuck",
            "put",
            "updated",
            {"foo": "bar"}
        )

        self.assertEqual(
            post_response,
            created,
            'UserGrid get_entities did not create entity'
        )

    def test_it_should_post_relationship(self, mock):
        """
        Ensures UG posts a relationship correctly

        :param mock:
        :return:
        """
        post_relation_response = read_json_file(
            'post_relationship_response.json'
        )

        mock.register_uri(
            "POST",
            "http://usergrid.com:80/man/chuck/users/has/story/foo",
            json=post_relation_response
        )

        created = self.user_grid.post_relationship('/users/has/story/foo')

        self.assertEqual(
            post_relation_response,
            created,
            'UserGrid get_entities did not create entity'
        )

    def test_it_should_post_file(self, mock):
        """
        Ensures UserGrid posts a file correctly

        :param mock:
        :return:
        """
        def request_match(request):
            return request.body is not None

        post_response = read_json_file('post_file_response.json')
        mock.register_uri(
            "POST",
            "http://usergrid.com:80/man/chuck/users",
            json=post_response,
            additional_matcher=request_match
        )

        created = self.user_grid.post_file(
            '/users',
            os.path.dirname(os.path.realpath(__file__)) + '/test_data/Headshot_300_300.jpg'
        )

        self.assertEqual(
            post_response,
            created,
            'UserGrid get_entities did not create entity'
        )

    def test_it_should_login_with_client_credentials(self, mock):
        """
        Ensures UserGrid will login correctly with client credentials

        :param mock:
        :return:
        """
        def request_match(request):
            if 'client_secret=bar' not in request.body:
                return False

            if 'client_id=foo' not in request.body:
                return False

            if 'grant_type=client_credentials' not in request.body:
                return False

            return True

        post_response = read_json_file('grant_auth_response.json')
        mock.register_uri(
            "POST",
            "http://usergrid.com:80/man/chuck/token",
            json=post_response,
            additional_matcher=request_match
        )

        self.user_grid.login(
            client_id='foo',
            client_secret='bar',
        )

    def test_it_should_login_with_password(self, mock):
        """
        Ensures UserGrid will login correctly with password grant

        :param mock:
        :return:
        """
        def request_match(request):
            if 'grant_type=password' not in request.body:
                return False

            if 'username=foo' not in request.body:
                return False

            if 'password=bar' not in request.body:
                return False

            return True

        post_response = read_json_file('password_auth_response.json')
        mock.register_uri(
            "POST",
            "http://usergrid.com:80/man/chuck/token",
            json=post_response,
            additional_matcher=request_match
        )

        self.user_grid.login(
            username='foo',
            password='bar'
        )

    def test_it_should_fail_login_with_bad_credentials(self, mock):
        """
        Ensures UserGrid will fail to login with bad password grant

        :param mock:
        :return:
        """
        def request_match(request):
            return (
                request.body ==
                'grant_type=password&password=bar&username=foo&ttl=1500')

        post_response = read_json_file('password_auth_failed_response.json')
        mock.register_uri(
            "POST",
            "http://usergrid.com/man/chuck/token",
            json=post_response,
            additional_matcher=request_match,
            status_code=400
        )

        with self.assertRaises(Exception) as failed:
            self.user_grid.login(
                username='foo',
                password='bar'
            )

    def test_it_should_fail_login_with_bad_password(self, mock):
        """
        Ensures UserGrid will fail to login with bad password grant

        :param mock:
        :return:
        """
        def request_match(request):
            return (
                request.body ==
                'grant_type=password&password=bar&username=foo&ttl=1500')

        post_response = read_json_file('password_auth_failed_response.json')
        mock.register_uri(
            "POST",
            "http://usergrid.com/man/chuck/token",
            json=post_response,
            additional_matcher=request_match,
            status_code=400
        )

        with self.assertRaises(Exception) as failed:
            self.user_grid.login(
                username='foo',
                password='bar',
                ttl=1500
            )

    def test_it_should_user_client_grant_as_default_login(self, mock):
        """
        Ensures UserGrid uses client credentials by default

        :param mock:
        :return:
        """
        def request_match(request):
            if 'grant_type=client_credentials' not in request.body:
                return False

            if 'client_id=foo' not in request.body:
                return False

            if 'client_secret=bar' not in request.body:
                return False

            return True

        post_response = read_json_file('grant_auth_response.json')
        mock.register_uri(
            "POST",
            "http://usergrid.com/man/chuck/token",
            json=post_response,
            additional_matcher=request_match
        )

        user_grid = UserGrid(
            host='usergrid.com',
            org='man',
            app='chuck',
            client_id='foo',
            client_secret='bar'
        )

        user_grid.login()

    def test_it_should_reconnect_when_token_expires(self, mock):
        """
        Ensures a reconnect happens when the token is expired

        :param mock:
        :return:
        """
        post_response = read_json_file('grant_auth_response.json')
        called = False

        def multiple_response(request, context):
            context.response_code = 200
            if not called:
                post_response['expires_in'] = -100000

            return post_response

        login_request = mock.register_uri(
            "POST",
            "http://usergrid.com/man/chuck/token",
            json=multiple_response
        )

        entities_response = read_json_file('get_entity_response.json')
        mock.register_uri(
            "GET",
            "http://usergrid.com/man/chuck/users/foo?limit=1",
            json=entities_response
        )

        user_grid = UserGrid(
            host='usergrid.com',
            org='man',
            app='chuck',
            client_id='foo',
            client_secret='bar',
            autoreconnect=True
        )

        user_grid.login()

        entity = user_grid.get_entity('/users/foo')

        self.assertEqual(
            '5dc2e4ba-2f33-11e6-9880-47e38a0eed23',
            entity['uuid'],
            'UserGrid get_entities did not return correct entities'
        )

        self.assertEqual(
            2,
            login_request.call_count
        )

    def test_it_should_not_reconnect_when_token_expires(self, mock):
        """
        Ensures a reconnect will not happen when turned off

        :param mock:
        :return:
        """
        post_response = read_json_file('grant_auth_response.json')
        called = False

        def multiple_response(request, context):
            context.response_code = 200
            if not called:
                post_response['expires_in'] = -100000

            return post_response

        login_request = mock.register_uri(
            "POST",
            "http://usergrid.com/man/chuck/token",
            json=multiple_response
        )

        entities_response = read_json_file('get_entity_response.json')
        mock.register_uri(
            "GET",
            "http://usergrid.com/man/chuck/users/foo?limit=1",
            json=entities_response
        )

        user_grid = UserGrid(
            host='usergrid.com',
            org='man',
            app='chuck',
            client_id='foo',
            client_secret='bar',
            autoreconnect=False
        )

        user_grid.login()
        with self.assertRaises(UserGridException) as expired:
            user_grid.get_entity('/users/foo')

        self.assertEqual(
            1,
            login_request.call_count
        )

        self.assertEqual(
            str(expired.exception),
            'Access token has expired'
        )

    def test_it_should_not_reconnect_when_token_set(self, mock):
        """
        Ensures that UG will not reconnect when setting a user token

        :param mock:
        :return:
        """
        post_response = read_json_file('grant_auth_response.json')
        called = False

        def multiple_response(request, context):
            context.response_code = 200
            if not called:
                post_response['expires_in'] = -100000

            return post_response

        login_request = mock.register_uri(
            "POST",
            "http://usergrid.com/man/chuck/token",
            json=multiple_response
        )

        entities_response = read_json_file('expired_token.json')
        mock.register_uri(
            "GET",
            "http://usergrid.com/man/chuck/users/foo?limit=1",
            json=entities_response,
            status_code=401
        )

        user_grid = UserGrid(
            host='usergrid.com',
            org='man',
            app='chuck',
            client_id='foo',
            client_secret='bar',
            autoreconnect=True
        )

        # connect to get a token
        user_grid.login()

        user_grid.access_token = 'FOO-BAR-BAZ-BAT'

        with self.assertRaises(UserGridException) as expired:
            user_grid.get_entity('/users/foo')

        self.assertEqual(
            1,
            login_request.call_count
        )

        self.assertEqual(
            str(expired.exception),
            'Unable to authenticate due to expired access token'
        )

    def test_it_should_generate_over_all_entities(self, mock):
        """
        Ensures that collection entities acts as a generator
        :param mock:
        :return:
        """
        page_one_response = read_json_file(
            'get_entities_response.json'
        )

        page_two_response = read_json_file(
            'get_entities_response_page_two.json'
        )

        mock.register_uri(
            "GET",
            "http://usergrid.com:80/man/chuck/users",
            json=page_one_response
        )

        mock.register_uri(
            "GET",
            "http://usergrid.com:80/man/chuck/users"
            "?cursor=LTU2ODc0MzQzOkhGOWVtalNoRWVhdmdvLTNqcmpZVWc",
            json=page_two_response
        )

        expected_user_ids = [
            '5dc2e4ba-2f33-11e6-9880-47e38a0eed23',
            '69361b5a-2f33-11e6-9d6f-c7a4ebfb263a',
            '75ad7b8a-2f33-11e6-8d91-25e5758e7b14',
            '5dc2e4ba-2f33-11e6-9880-47e38a0eed23',
            '69361b5a-2f33-11e6-9d6f-c7a4ebfb263a',
            '5dc2e4ba-2f33-66e6-9880-47e38a0eed23',
            '69361b5a-7f33-11e6-9d6f-c7a4ebfb763a',
            '75ad7b8a-2f88-11e6-8d91-25e5758e7b14',
            '5dc2e9ba-2f33-11e6-9880-97e38a0eed23',
            '6936110a-2f33-11e6-9d6f-c7a4ebfb263a',
            "6936111a-2f33-11e6-9d6f-c7a4ebfb263a"
        ]

        actual_user_ids = []
        for user in self.user_grid.collect_entities('/users'):
            actual_user_ids.append(user['uuid'])

        self.assertEqual(
            expected_user_ids,
            actual_user_ids,
            'UserGrid get_entities did not generate entities'
        )

    def test_it_should_process_entities(self, mock):
        """

        :param mock:
        :return:
        """

        page_one_response = read_json_file(
            'get_entities_response.json'
        )

        page_two_response = read_json_file(
            'get_entities_response_page_two.json'
        )

        mock.register_uri(
            "GET",
            "http://usergrid.com:80/man/chuck/users",
            json=page_one_response
        )

        mock.register_uri(
            "GET",
            "http://usergrid.com:80/man/chuck/users"
            "?cursor=LTU2ODc0MzQzOkhGOWVtalNoRWVhdmdvLTNqcmpZVWc",
            json=page_two_response
        )

        expected_calls = []
        for entity in page_one_response['entities']:
            expected_calls.append(call(entity))

        for entity in page_two_response['entities']:
            expected_calls.append(call(entity))

        mock = Mock(name='process_test')
        self.user_grid.process_entities('/users', method=mock)
        self.assertEqual(
            expected_calls,
            mock.mock_calls,
            'UserGrid get_entities did not process entities'
        )

    def test_archive_one_entity(self, mock):
        """
        tests archiving an entity
        :param mock:
        :return:
        """

        entities_response = read_json_file('get_presegmented.json')
        mock.register_uri(
            "GET",
            "http://usergrid.com:80/man/chuck/presegmentedaudios/foo",
            json=entities_response
        )
        presegmented_has_response = read_json_file(
            'get_presegmented_has.json'
        )

        presegmented_connecting_has_response = read_json_file(
            'get_presegmented_connecting_has.json'
        )

        mock.register_uri(
            "GET",
            "http://usergrid.com:80/man/chuck/presegmentedaudios/foo/has",
            json=presegmented_has_response
        )

        mock.register_uri(
            "GET",
            "http://usergrid.com:80/man/chuck/"
            "presegmentedaudios/foo/connecting/has",
            json=presegmented_connecting_has_response
        )

        archived_presegmented_post_response = read_json_file(
            'archived_presegmented_post.json'
        )
        mock.register_uri(
            "POST",
            "http://usergrid.com:80/man/chuck/archived_presegmentedaudios",
            json=archived_presegmented_post_response
        )
        page_one_response = read_json_file(
            'presegmented_connecting_owns_users_1.json'
        )

        page_two_response = read_json_file(
            'presegmented_connecting_owns_users_2.json'
        )

        mock.register_uri(
            "GET",
            "http://usergrid.com:80/man/chuck/"
            "presegmentedaudios/foo/connecting/owns",
            json=page_one_response
        )

        mock.register_uri(
            "GET",
            "http://usergrid.com:80/man/chuck/"
            "presegmentedaudios/foo/connecting/owns"
            "?cursor=LTU2ODc0MzQzOmhHU2hDakk5RWVhWXRkV3Q1QUNKc2c",
            json=page_two_response
        )

        delete_response = read_json_file('delete_presegmented.json')
        mock.register_uri(
            "DELETE",
            "http://usergrid.com:80/man/chuck/presegmentedaudios/foo",
            json=delete_response
        )
        archived_entity = self.user_grid.archive_entity(
            "presegmentedaudios",
            "foo"
        )

        self.assertEqual(
            archived_presegmented_post_response['entities'][0],
            archived_entity, "Usergrid didn't archive entity"
        )

    def test_it_should_archive_entity_without_connections(self, mock):
        """
        test to make sure it archives entity if it has no connections
        :param mock:
        :return:
        """
        entities_response = read_json_file('get_presegmented.json')
        delete_response = read_json_file('delete_presegmented.json')
        archived_presegmented_post_response = read_json_file(
            'archived_presegmented_post.json'
        )
        for key in ['connections', 'connecting']:
            entities_response['entities'][0]['metadata'].pop(key, None)
            delete_response['entities'][0]['metadata'].pop(key, None)
            archived_presegmented_post_response['entities'][0]['metadata'].pop(
                key, None
            )

        mock.register_uri(
            "GET",
            "http://usergrid.com:80/man/chuck/presegmentedaudios/foo",
            json=entities_response
        )
        mock.register_uri(
            "DELETE",
            "http://usergrid.com:80/man/chuck/presegmentedaudios/foo",
            json=delete_response
        )
        mock.register_uri(
            "POST",
            "http://usergrid.com:80/man/chuck/archived_presegmentedaudios",
            json=archived_presegmented_post_response
        )
        archived_entity = self.user_grid.archive_entity(
            "presegmentedaudios",
            "foo"
        )
        self.assertEqual(
            archived_presegmented_post_response['entities'][0],
            archived_entity, "Usergrid didn't archive entity"
        )

    def test_it_should_not_archive_entity_when_conneting_entity_not_found(
            self,
            mock
    ):
        """
        test to check if it raises exception and not archive entity when
        connections are not found
        :param mock:
        :return:
        """
        entities_response = read_json_file('get_presegmented.json')
        entities_response['entities'][0]['metadata'].pop("connecting", None)
        mock.register_uri(
            "GET",
            "http://usergrid.com:80/man/chuck/presegmentedaudios/foo",
            json=entities_response
        )
        presegmented_has_response_not_found = read_json_file(
            'get_entity_not_found_response.json'
        )

        mock.register_uri(
            "GET",
            "http://usergrid.com:80/man/chuck/presegmentedaudios/foo/has",
            json=presegmented_has_response_not_found,
            status_code=404
        )
        with self.assertRaises(UserGridException) as failed:
            self.user_grid.archive_entity("presegmentedaudios", "foo")

    def test_it_should_return_version(self, mock):
        """
        Ensures that the version number can be imported correctly

        :return:
        """

        self.assertEqual(
            '0.1.8',
            __version__
        )