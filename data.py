from datetime import datetime

# data VERSION: v1.0.0
# 1.0.0: old version

#REGION class helpers
class Serializable:
    def as_dict(self, obj = None):
        ret = {}
        if obj != None:
            read = obj.__dict__
        else:
            read = self.__dict__

        for key in read:
            value = read[key]
            if "data." in str(type(value)):
                ret[key] = self.as_dict(obj=value)
            else:
                ret[key] = value
        return ret

class Settable:
    def __setitem__(self,k,v):
        setattr(self,k,v)

    def __getitem__(self,k):
        return getattr(self, k)

    def set(self,obj: dict):
        if obj == None:
            return

        for key in obj:
            self[key] = obj[key]
#ENDREGION

#REGION date and time
# timestamp
def get_timestamp() -> str:
    return datetime.now().isoformat()
#ENDREGION
