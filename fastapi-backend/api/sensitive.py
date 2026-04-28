from fastapi import APIRouter, Query, UploadFile, File
from core.response import success, error
from db.db import get_db_connection
from db.models import SensitiveWord
from service.import_service import import_sensitive_words, generate_sensitive_template
from io import BytesIO

router = APIRouter()

@router.get("/sensitive")
def get_sensitive_words(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=1000),
    keyword: str = Query("")
):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = 'SELECT * FROM sensitive_words'
    params = []
    
    if keyword and keyword.strip():
        query += ' WHERE sensitive_word LIKE ?'
        params.append(f'%{keyword}%')
    
    query += ' ORDER BY id DESC LIMIT ? OFFSET ?'
    params.extend([size, (page - 1) * size])
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    cursor.execute('SELECT COUNT(*) FROM sensitive_words' + (' WHERE sensitive_word LIKE ?' if keyword and keyword.strip() else ''), 
                params[:-2] if keyword and keyword.strip() else [])
    total = cursor.fetchone()[0]
    
    conn.close()
    
    result = {
        "list": [dict(row) for row in rows],
        "total": total
    }
    
    return success(result)

@router.post("/sensitive")
def create_sensitive_word(word: SensitiveWord):
    if not word.sensitive_word.strip():
        return error(400, "敏感词不能为空")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('INSERT INTO sensitive_words (sensitive_word) VALUES (?)', 
                    (word.sensitive_word.strip(),))
        conn.commit()
        word.id = cursor.lastrowid
        conn.close()
        return success(dict(word), "添加成功")
    except Exception as e:
        conn.close()
        if "UNIQUE constraint failed" in str(e):
            return error(400, "敏感词已存在")
        return error(400, str(e))

@router.put("/sensitive/{id}")
def update_sensitive_word(id: int, word: SensitiveWord):
    if not word.sensitive_word.strip():
        return error(400, "敏感词不能为空")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM sensitive_words WHERE id = ?', (id,))
    if cursor.fetchone() is None:
        conn.close()
        return error(404, "敏感词不存在")
    
    try:
        cursor.execute('UPDATE sensitive_words SET sensitive_word = ? WHERE id = ?', 
                    (word.sensitive_word.strip(), id))
        conn.commit()
        conn.close()
        return success(None, "修改成功")
    except Exception as e:
        conn.close()
        if "UNIQUE constraint failed" in str(e):
            return error(400, "敏感词已存在")
        return error(400, str(e))

@router.delete("/sensitive/{id}")
def delete_sensitive_word(id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM sensitive_words WHERE id = ?', (id,))
    if cursor.fetchone() is None:
        conn.close()
        return error(404, "敏感词不存在")
    
    cursor.execute('DELETE FROM variant_words WHERE sensitive_id = ?', (id,))
    cursor.execute('DELETE FROM sensitive_words WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    
    return success(None, "删除成功")

@router.post("/sensitive/import")
async def import_sensitive(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        result = import_sensitive_words(BytesIO(contents))
        return success(result, "导入完成")
    except Exception as e:
        return error(400, str(e))

@router.get("/sensitive/template")
def download_template():
    from fastapi.responses import StreamingResponse
    output = generate_sensitive_template()
    return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            headers={"Content-Disposition": "attachment; filename=sensitive_word_template.xlsx"})