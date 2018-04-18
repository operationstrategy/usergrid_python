"""
User Grid class
"""
import json
import logging
import warnings
import time
import requests
from usergrid.exceptions import UserGridException
from usergrid.decorators import catch_usergrid_not_found_exception

__version__ = '0.1.12'

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


# pylint: disable=too-many-public-methods
# pylint: disable=too-many-instance-attributes
class UserGrid(object):
    """
    Class wrapping UG calls easier
    """
    __slots__ = (
        '_client_id',
        '_client_secret',
        '_use_compression',
        '_auto_reconnect',
        '_app_endpoint',
        '_management_endpoint',
        '_access_token',
        '_token_expires',
        '_last_login_info',
        '_default_timeout',
        '_last_response',
        '_me'
    )

    def __init__(self, **kwargs):
        """
        :param str host:
        :param int port:
        :param str org:
        :param str app:
        :param str client_id:
        :param str client_secret:
        :param boolean debug:
        :param boolean autoreconnect:
        :param boolean use_compression:
        :param boolean use_ssl:
        :param int default_timeout:
        """
        host = kwargs.pop('host', None)
        app = kwargs.pop('app', None)
        org = kwargs.pop('org', None)
        assert host is not None
        assert org is not None
        assert app is not None

        self._client_id = kwargs.pop('client_id', None)
        self._client_secret = kwargs.pop('client_secret', None)
        self._use_compression = kwargs.pop('use_compression', None)
        self._auto_reconnect = kwargs.pop('autoreconnect', None)
        use_ssl = kwargs.pop('use_ssl', False)
        port = kwargs.pop('port', None)

        scheme = 'http://'
        if use_ssl:
            scheme = 'https://'

        self._app_endpoint = scheme + host
        self._management_endpoint = scheme + host

        if port is not None:
            self._app_endpoint += ':' + str(port)
            self._management_endpoint += ':' + str(port)

        self._app_endpoint += '/%s/%s' % (org, app)
        self._management_endpoint += "/management"
        self._access_token = None
        self._token_expires = None
        self._default_timeout = kwargs.pop('default_timeout', 20)
        self._me = None
        self._last_login_info = None

    @property
    def me(self):  # pylint: disable=invalid-name
        """

        :return:
        """
        return self._me

    @property
    def access_token(self):
        """
        Returns the access token

        :return:
        """
        return self._access_token

    @access_token.setter
    def access_token(self, token):
        """
        Token setter will reset options for properties

        :param token:
        :return:
        """
        self._auto_reconnect = False
        self._client_id = None
        self._client_secret = None
        self._access_token = token
        self._me = None
        self._last_login_info = {}
        self._token_expires = None

    def login(self, **kwargs):
        """
        Login to UG

        :param str superuser: name for the super admin
        :param str username: user name to autheticate with
        :param str password: password for super/user name
        :param str client_id: id for client_grant
        :param str client_secret: secret for client_grant
        :param int ttl: Time in seconds for the auth token to exist
        :return:
        """
        client_id = kwargs.pop('client_id', self._client_id)
        client_secret = kwargs.pop('client_secret', self._client_secret)
        user_name = kwargs.pop('username', None)
        super_user = kwargs.pop('superuser', None)
        password = kwargs.pop('password', None)
        ttl = kwargs.pop('ttl', None)

        self._client_id = client_id
        self._client_secret = client_secret

        endpoint = self._app_endpoint

        self._last_login_info = {
            'superuser': super_user,
            'ttl': ttl
        }

        if not user_name and not super_user:
            logger.info("Authenticating with client credentials")
            data = {
                "grant_type": "client_credentials",
                "client_id": self._client_id,
                "client_secret": self._client_secret
            }
        else:
            logger.info("Authenticating with username and password")
            self._auto_reconnect = False
            data = {
                "grant_type": "password",
                "username": user_name,
                "password": password
            }
            if super_user:
                logger.info("Authenticating as super user")
                endpoint = self._management_endpoint
                data['username'] = super_user

        if ttl is not None:
            if ttl < 1:
                raise RuntimeError('You cannot set a ttl less than one second')

            # request is made with milliseconds
            data['ttl'] = int(ttl) * 1000

        login_response = requests.request(
            method="POST",
            url=endpoint + "/token",
            data=data,
            timeout=20
        )

        try:
            login_json = login_response.json()
            if login_response.status_code == 200:
                self._token_expires = time.time() + int(login_json['expires_in'])
                self._access_token = login_json['access_token']
                if user_name:  # Only set if we are password grant
                    self._me = login_json['user']

            if 'error' in login_json and login_json['error'] == 'invalid_grant':
                raise UserGridException(
                    title=UserGridException.ERROR_LOGIN,
                    detail='Failed to login to usergrid'
                )
        except Exception as test:
            raise UserGridException(
                title=UserGridException.ERROR_GENERAL,
                detail='Failed to connect to usergrid'
            )

    @property
    def std_headers(self):
        """
        Standard headers sent with each request

        :return:
        """
        headers = {
            'user-agent': 'python usergrid client v.{0}'.format(__version__),
            'Accept': 'application/json',
        }

        if self._access_token is not None:
            headers['Authorization'] = "Bearer %s" % self._access_token

        if self._use_compression:
            headers['Accept-Encoding'] = "gzip, deflate"

        return headers

    def _get_full_endpoint(self, path):
        """
        Builds the endpoint for making a request

        :param str path:
        :rtype str:
        :return:
        """
        if '/' in path[0]:
            path = path[1:]

        return "{0}/{1}".format(self._app_endpoint, path)

    def collect_entities(self, endpoint, ql=None, limit=None):  # pylint: disable=invalid-name
        """
        A generator to return all entities

        Do no use this for end-user code

        :param str endpoint:
        :param str ql:
        :param int limit:
        :rtype dict:
        :return:
        """
        cursor = None

        if not limit or limit > 1000:
            limit = 1000

        while True:
            page_entities, cursor = self.get_entities(
                endpoint,
                ql=ql,
                limit=limit,
                cursor=cursor
            )

            for entity in page_entities:
                yield entity

            if cursor is None or len(page_entities) < limit:
                break


    def process_entities(self, endpoint, method, ql=None, limit=None):  # pylint: disable=invalid-name
        """
        Apply a function to each entity

        Do not use this for end-user code as it will apply to all entites
        in a collection

        :param str endpoint:
        :param callable method:
        :param str ql:
        :param int limit:
        :return:
        """
        assert callable(method)
        for entity in self.collect_entities(endpoint, ql, limit):
            method(entity)

    @catch_usergrid_not_found_exception(return_value_on_exception=([], None))
    def get_entities(self, endpoint, cursor=None, ql=None, limit=None):  # pylint: disable=invalid-name
        """
        Get entities from UG

        :param str endpoint:
        :param str cursor:
        :param str ql:
        :param int limit:
        :rtype (list, str):
        :return:
        """
        query_params = {}

        if limit:
            query_params['limit'] = int(limit)

        if ql:
            query_params['ql'] = ql

        if cursor:
            query_params['cursor'] = cursor

        entities = None
        cursor = None

        try:
            response = self._make_request(
                'GET',
                self._get_full_endpoint(endpoint),
                params=query_params
            )
            if 'entities' in response:
                entities = response['entities']

            # FIXME this seems impossible reach
            if 'list' in response:
                entities = response['list']

            if 'cursor' in response:
                cursor = response['cursor']

        except requests.HTTPError as request_exception:
            if 400 < request_exception.errno < 500:
                pass
            else:
                raise

        return [entities, cursor]

    @catch_usergrid_not_found_exception(return_value_on_exception=None)
    def get_entity(self, endpoint, ql=None):  # pylint: disable=invalid-name
        """
        Gets one entity from UG

        :param str endpoint:
        :param str ql:
        :rtype dict | None:
        :return:
        """
        entities, cursor = self.get_entities(endpoint, ql=ql, limit=1)  # pylint: disable=unused-variable
        entity = None
        if entities:
            entity = entities[0]

        return entity

    def get_entity_by_id(self, entity, entity_id):
        """
        Helper to get an entity by an entity_id

        :param entity:
        :param entity_id:
        :return:
        """
        return self.get_entity(entity + '/' + entity_id)

    def delete_entity(self, endpoint):
        """
        Calls DELETE on an endpoint

        :param endpoint:
        :return:
        """
        response = self._make_request(
            'DELETE',
            self._get_full_endpoint(endpoint)
        )

        return response

    def delete_entity_by_id(self, entity, entity_id):
        """
        Helper to delete entity by an id

        :param entity:
        :param entity_id:
        :return:
        """
        return self.delete_entity(entity + '/' + entity_id)

    def post_entity(self, endpoint, data):
        """
        Creates an entity

        :param str endpoint:
        :param dict data:
        :return:
        """
        response = self._make_request(
            'POST',
            self._get_full_endpoint(endpoint),
            data=json.dumps(data)
        )

        return response['entities'][0]

    def update_entity(self, endpoint, data):
        """
        Runs put on an endpoint

        :param str endpoint:
        :param dict data:
        :return:
        """
        response = self._make_request(
            'PUT',
            self._get_full_endpoint(endpoint),
            data=json.dumps(data)
        )

        return response['entities'][0]

    def update_entity_by_id(self, entity, entity_id, data):
        """
        Helper to update an entity by id

        :param entity:
        :param entity_id:
        :param data:
        :return:
        """
        return self.update_entity(entity + '/' + entity_id, data)

    def post_activity(self, endpoint, actor, verb, content, data=None):  # pylint: disable=too-many-arguments
        """
        Saves activity for an actor

        :param str endpoint:
        :param str actor:
        :param str verb:
        :param str content:
        :param dict data:
        :return:
        """
        post_data = {
            "actor": actor,
            "verb": verb,
            "content": content
        }

        if data:
            post_data.update(data)

        return self._make_request(
            'POST',
            self._get_full_endpoint(endpoint),
            data=json.dumps(post_data),
        )

    @staticmethod
    def get_connections(entity):
        """
        Helps pulls connections from an entity

        :param dict entity:
        :return:
        """
        if 'metadata' in entity and 'connections' in entity['metadata']:
            return entity['metadata']['connections']

        return None

    def post_relationship(self, endpoint):
        """
        Posts a relationship to an entity

        :param str endpoint:
        :return:
        """
        return self._make_request(
            'POST',
            self._get_full_endpoint(endpoint)
        )

    def delete_relationship(self, endpoint):
        """
        Deletes a relationship to an entity

        :param str endpoint:
        :return:
        """
        return self._make_request(
            'DELETE',
            self._get_full_endpoint(endpoint)
        )

    def post_file(self, endpoint, filepath):
        """
        Saves a file to UserGrid

        :param endpoint:
        :param filepath:
        :return:
        """
        file_handler = None
        try:
            file_handler = open(filepath, 'rb')

            files = {
                'file': file_handler,
                'name': filepath.split("/")[-1]
            }

            response = self._make_request(
                'POST',
                self._get_full_endpoint(endpoint),
                files=files,
                timeout=300  # 5min to upload
            )
        finally:
            if file_handler:
                file_handler.close()

        return response

    @staticmethod
    def get_actor_from_user(user):
        """
        Extracts the actor from a user entity

        :param dict user:
        :return:
        """
        name = ''
        picture = ''
        email = ''

        if 'username' in user:
            name = user['username']

        if 'name' in user:
            name = user['name']

        if 'picture' in user:
            picture = user['picture']

        if 'email' in user:
            email = user['email']

        return {
            "uuid": user['uuid'],
            "displayName": name,
            "username": user['username'],
            "email": email,
            "picture": picture
        }

    @staticmethod
    def print_user(user):
        """
        Deprecated call do not use

        :param user:
        :return:
        """
        warnings.warn(DeprecationWarning)
        logger.info(user)

    def _check_expired_token(self):
        """
        Called in _make_request to check if the token is expired
        :return:
        """
        # No expires set because the access_token was manually inputted
        if self._token_expires is None:
            return

        # Still have time on the token
        if self._token_expires > time.time():
            return

        if self._auto_reconnect:
            self.login()
            return

        raise UserGridException(
            title=UserGridException.ERROR_EXPIRED_TOKEN,
            detail='Access token has expired'
        )

    def _make_request(self, method, url, **kwargs):
        """
        Makes a call to user grid and forces a timeout

        :param method:
        :param url:
        :param kwargs:
        :rtype dict:
        :return:
        """
        try:
            self._check_expired_token()
            if 'timeout' not in kwargs:
                kwargs['timeout'] = self._default_timeout

            if 'headers' not in kwargs:
                kwargs['headers'] = {}

            kwargs['headers'].update(self.std_headers)

            response = requests.request(
                method,
                url,
                **kwargs
            )

            logger.debug('%s [%s] %s', method, response.status_code, url)
            self._last_response = response
            response_json = response.json()
            if 'exception' not in response_json:
                return response_json

            title = UserGridException.ERROR_GENERAL
            detail = 'Unknown user grid error'

            if 'error' in response_json:
                title = response_json['error']

            if 'error_description' in response_json:
                detail = response_json['error_description']

            raise UserGridException(
                title=title,
                detail=detail
            )

        except Exception as request_exception:
            logger.exception(request_exception)
            raise

    def archive_entity(self, entity_type, entity_id):
        """
        archives an entity to its corresponding archive table
        and returns archived entity given its type and id
        :param str entity_type:
        :param str entity_id:
        :return: dict
        """
        real_entity = self.get_entity_by_id(entity_type, entity_id)
        self._add_related_entities_to_entity(
            entity=real_entity,
            connection_type='connecting'
        )

        self._add_related_entities_to_entity(
            entity=real_entity,
            connection_type='connections'
        )

        archived_entity = self.post_entity(
            '/archived_%s' % entity_type,
            real_entity
        )

        self.delete_entity_by_id(entity_type, entity_id)
        return archived_entity

    def _add_related_entities_to_entity(self, entity, connection_type):
        """
        Finds all connecting entities and adds to the entity

        Mutates the entity

        :param entity:
        :param connection_type:
        :return:
        """
        if 'metadata' not in entity:
            return

        if connection_type not in entity['metadata']:
            return

        key_prefix = '__' + connection_type + '_'
        for key in entity['metadata'][connection_type]:
            self._add_related_entities(
                entity=entity,
                endpoint=entity['metadata'][connection_type][key],
                key=(key_prefix + key)
            )

    def update_password(self, user_id, old_password, new_password):
        """
        Updates a password for a usergrid user

        :param user_id:
        :param old_password:
        :param new_password:
        :return:
        """
        response = self._make_request(
            'PUT',
            self._get_full_endpoint('/users/' + user_id + '/password'),
            params={
                "client_id": self._client_id,
                "client_secret": self._client_secret
            },
            data=json.dumps({
                "oldpassword": old_password,
                "newpassword": new_password
            })
        )

        if 'error' in response:
            raise UserGridException(
                title=UserGridException.ERROR_PASSWORD_FAILED,
                detail='Updating password failed: ' + response['error']
            )

        return True

    def _add_related_entities(self, entity, endpoint, key):
        """
        Adds entities to the entity from matching endpoint

        Mutates the entity

        :param entity:
        :return:
        """
        if key not in entity:
            entity[key] = []

        for connecting_entity in self.collect_entities(endpoint):
            entity[key].append(connecting_entity)


__all__ = ['UserGrid', '__version__']
