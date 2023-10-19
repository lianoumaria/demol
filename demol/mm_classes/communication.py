class BrokerAuthPlain:
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
    def __init__(self, parent, host, port, vhost, auth):
        self.parent = parent
        self.host = host
        self.port = port
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
    def __init__(self, parent, host, port, db, auth):
        self.parent = parent
        self.host = host
        self.port = port
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
    def __init__(self, parent, host, port, auth):
        self.parent = parent
        self.host = host
        self.port = port
        self.auth = auth

    def to_dict(self):
        return {
            'host': self.host,
            'port': self.port,
            'auth': self.auth.to_dict(),
        }

