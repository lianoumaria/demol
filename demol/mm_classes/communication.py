class AuthPlain:
    def __init__(self, parent, username, password):
        self.parent = parent
        self.username = username
        self.password = password

    def to_dict(self):
        return {
            key: val for key, val in self.__dict__.items() \
            if not key.startswith('_') and key not in ('parent')
        }


class AMQPBroker:
    def __init__(self, parent, name, host, port, ssl, vhost, auth, *args, **kwargs):
        self.parent = parent
        self.name = name
        self.host = host
        self.port = port
        self.ssl = ssl
        self.vhost = vhost
        self.auth = auth

    def to_dict(self):
        return {
            'host': self.host,
            'port': self.port,
            'vhost': self.vhost,
            'auth': self.auth.to_dict(),
        }


class RedisBroker:
    def __init__(self, parent, name, host, port, ssl, db, auth,  *args, **kwargs):
        self.parent = parent
        self.name = name
        self.host = host
        self.port = port
        self.ssl = ssl
        self.db = db
        self.auth = auth

    def to_dict(self):
        return {
            'host': self.host,
            'port': self.port,
            'db': self.db,
            'auth': self.auth.to_dict(),
        }


class MQTTBroker:
    def __init__(self, parent, name, host, port, ssl, auth,  *args, **kwargs):
        self.parent = parent
        self.name = name
        self.host = host
        self.port = port
        self.ssl = ssl
        self.auth = auth

    def to_dict(self):
        return {
            'host': self.host,
            'port': self.port,
            'auth': self.auth.to_dict(),
        }

