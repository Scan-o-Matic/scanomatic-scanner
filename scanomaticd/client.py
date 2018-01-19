class Client:

    def __init__(self, host, user, password):
        self._uuid = None
        self._host = host
        self._user = user
        self._password = password

    @property
    def uuid(self):
        return self._uuid

    @property
    def host(self):
        return self._host

    @property
    def user(self):
        return self._user

    def set_uuid(self, uuid):
        self._uuid = uuid

    def post_update(self, message=""):
        pass
