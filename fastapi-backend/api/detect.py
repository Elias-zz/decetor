from fastapi import APIRouter
from core.response import success, error
from db.models import DetectRequest
from service.detect_service import detect_sensitive_words

router = APIRouter()

@router.post("/detect")
def detect(request: DetectRequest):
    if not request.text or not request.text.strip():
        return error(400, "文本不能为空")
    
    result = detect_sensitive_words(request.text)
    
    return success(result, "检测完成")