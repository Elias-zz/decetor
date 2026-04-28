from pydantic import BaseModel, Field
from typing import Optional, List

class SensitiveWord(BaseModel):
    id: Optional[int] = None
    sensitive_word: str = Field(..., description="敏感词")

class VariantWord(BaseModel):
    id: Optional[int] = None
    variant_word: str = Field(..., description="变形词")
    sensitive_id: int = Field(..., description="关联的原始敏感词ID")

class DetectRequest(BaseModel):
    text: str = Field(..., description="待检测文本")

class DetectResult(BaseModel):
    highlight_text: str = ""
    original_matches: List[dict] = []
    variant_matches: List[dict] = []
    original_count: int = 0
    variant_count: int = 0
    total_count: int = 0

class LoginRequest(BaseModel):
    username: str
    password: str

class PageResponse(BaseModel):
    list: List[dict] = []
    total: int = 0