from typing import Optional, Generic, TypeVar

T = TypeVar('T')

class ResponseModel(Generic[T]):
    code: int
    msg: str
    data: Optional[T]
    
    def __init__(self, code: int, msg: str, data: T = None):
        self.code = code
        self.msg = msg
        self.data = data
    
    def dict(self):
        return {
            "code": self.code,
            "msg": self.msg,
            "data": self.data
        }

def success(data: T = None, msg: str = "成功") -> dict:
    return ResponseModel(200, msg, data).dict()

def error(code: int = 400, msg: str = "失败") -> dict:
    return ResponseModel(code, msg, None).dict()