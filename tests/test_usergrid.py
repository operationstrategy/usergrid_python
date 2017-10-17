from unittest import TestCase
import requests
import requests_mock
from tests import read_json_file
from usergrid.usergrid import UserGrid

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
            client_id='manchuck',
            client_secret='manbearpig'
        )

    def test_it_should_get_entities(self, mock):
        """

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
        Tests get_entities calls with query parameter

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
        Ensures one entity is returned

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

        entities, actual_cursor = self.user_grid.get_entities('users')

        self.assertEqual(
            None,
            actual_cursor,
            'UserGrid get_entities did not return correct cursor when not found'
        )

        self.assertEqual(
            [],
            entities,
            'UserGrid get_entities did not return empty list when not found'
        )

    def test_it_should_delete_entity(self, mock):
        """
        Ensures creating entities works as expected

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
        Ensures usergrid will post_activity correctly
        :param mock:
        :return:
        """
        # /users/me/activities
        def request_match(request):
            return (
                request.body ==
                '{"actor": "manchuck", "verb": "put", "content":'
                ' "updated", "foo": "bar"}')

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
        Ensures usergid posts a relationship correctly
        :param mock:
        :return:
        """
        post_relation_response = read_json_file('post_relationship_response.json')
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
            '../tests/test_data/Headshot_300_300.jpg'
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
            return (
                request.body ==
                'grant_type=client_credentials&client_id=foo&client_secret=bar')

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
            return (
                request.body ==
                'grant_type=password&password=bar&username=foo')

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
            "http://usergrid.com:80/man/chuck/token",
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
            "http://usergrid.com:80/man/chuck/token",
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
            test = request.body
            return (
                request.body ==
                'grant_type=client_credentials&client_id=foo&client_secret=bar')

        post_response = read_json_file('grant_auth_response.json')
        mock.register_uri(
            "POST",
            "http://usergrid.com:80/man/chuck/token",
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
