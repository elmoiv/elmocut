class NetFace:
    def __init__(self, iface):
        self.name = iface['name']
        self.guid = iface['guid']
        self.mac = iface['mac']
        self.ip = iface['ips'][-1]
    
    def __repr__(self):
        return f'<NAME={self.name}, GUID={self.guid}, MAC={self.mac}, IP={self.ip}>'