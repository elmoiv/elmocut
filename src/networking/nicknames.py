from tools.utils_gui import get_settings, set_settings

class Nicknames:
    def __init__(self):
        self.__db = get_settings('nicknames')
    
    def get_name(self, mac):
        return self.__db.get(mac, '-')
    
    def set_name(self, mac, name):
        self.__db[mac] = name
        set_settings('nicknames', self.__db)
    
    def reset_name(self, mac):
        if mac in self.__db:
            del self.__db[mac]
        set_settings('nicknames', self.__db)
    
    @property
    def nicknames_database(self):
        return self.__db