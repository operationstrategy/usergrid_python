class UserGridException(BaseException):
    """
    Exception class for UG
    """
    ERROR_PASSWORD_FAILED = 'password_update_failed'
    ERROR_EXPIRED_TOKEN = 'expired_token'
    ERROR_GENERAL = 'usergrid_failure'
    ERROR_LOGIN = 'login_failed'

    _title = None

    _detail = None

    def __init__(self, title, detail):
        self.title = title
        self.detail = detail

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, title):
        self._title = title

    @property
    def detail(self):
        return self._detail

    @detail.setter
    def detail(self, detail):
        self._detail = detail

    def __str__(self):
        return '%s: %s' % (self.title, self.detail)
