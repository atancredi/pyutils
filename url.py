from enum import Enum
from typing import List, Optional

# url VERSION: v1.0.0
# 1.0.0: first version

class WebProtocol(Enum):
    HTTP = "http://"
    HTTPS = "https://"

class Url:
    scheme: WebProtocol
    host: str
    port: Optional[int]
    path: List[str]
    query: str

    def __init__(self, host: str, scheme: WebProtocol = WebProtocol.HTTPS, port: Optional[int] = None) -> None:
        self.host = host
        self.scheme = scheme
        self.port = port
        self.path = []
        self.query = ""

    def join_path(self, path: str):
        self.path.append(path)
        return self

    def join_query_parameter(self, key: str, value: str):
        self.query += f"{key}={value}&"
        
    def get(self) -> str:
        base_url = self.scheme.value + self.host
        if self.port:
            base_url += ":" + str(self.port)

        args = (base_url,*self.path)
        trailing_slash = '/' if args[-1].endswith('/') else ''
        
        ret = "/".join(map(lambda x: str(x).strip('/'), args)) + trailing_slash
        if self.query:
            ret += "?" + self.query[:-1]
        return ret
 
if __name__ == "__main__":
    u = Url("www.google.com")
    u.join_path("path/to/file.css")
    u.join_query_parameter("key", "value")
    u.join_query_parameter("key2", "value")
    u.join_path("path/2/")
    print(u.get())
