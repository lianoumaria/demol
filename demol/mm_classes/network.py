class Network:
    def __init__(self, parent, ssid, passwd, address, channel):
        self.parent = parent
        self.ssid = ssid
        self.passwd = passwd
        self.address = address
        self.channel = channel

    def to_dict(self):
        return {
            'ssid': self.ssid,
            'passwd': self.passwd,
            'address': self.address,
            'channel': self.channel,
        }

