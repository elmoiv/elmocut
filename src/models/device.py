class Device:
    def __init__(self, **kwargs):
        self.ip = kwargs['ip']
        self.mac = kwargs['mac']
        self.vendor = kwargs['vendor']
        self.type = kwargs['dtype']
        self.name = kwargs['name']
        self.admin = kwargs['admin']
    
    def to_dict(self):
        return self.__dict__.copy()