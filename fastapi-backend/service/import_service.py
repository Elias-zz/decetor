from db.db import get_db_connection
from utils.excel_handler import read_excel, generate_single_column_template, generate_double_column_template

def import_sensitive_words(file_stream):
    data = read_excel(file_stream)
    
    if len(data) == 0 or (len(data) == 1 and data[0][0] is None):
        return {'success': 0, 'duplicate': [], 'invalid': []}
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    success_count = 0
    duplicate_rows = []
    invalid_rows = []
    
    for idx, row in enumerate(data):
        row_num = idx + 1
        
        if len(row) == 0 or (len(row) == 1 and row[0] is None):
            continue
        
        if len(row) == 0 or row[0] is None:
            invalid_rows.append(row_num)
            continue
        
        word = str(row[0]).strip()
        
        if not word:
            invalid_rows.append(row_num)
            continue
        
        cursor.execute('SELECT id FROM sensitive_words WHERE sensitive_word = ?', (word,))
        if cursor.fetchone():
            duplicate_rows.append(row_num)
            continue
        
        try:
            cursor.execute('INSERT INTO sensitive_words (sensitive_word) VALUES (?)', (word,))
            success_count += 1
        except Exception as e:
            invalid_rows.append(row_num)
    
    conn.commit()
    conn.close()
    
    return {
        'success': success_count,
        'duplicate': duplicate_rows,
        'invalid': invalid_rows
    }

def import_variant_words(file_stream):
    data = read_excel(file_stream)
    
    if len(data) == 0 or (len(data) == 1 and data[0][0] is None):
        return {'success': 0, 'duplicate': [], 'invalid': [], 'no_match': []}
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT sensitive_word, id FROM sensitive_words')
    sensitive_map = {row['sensitive_word']: row['id'] for row in cursor.fetchall()}
    
    success_count = 0
    duplicate_rows = []
    invalid_rows = []
    no_match_rows = []
    
    for idx, row in enumerate(data):
        row_num = idx + 1
        
        if len(row) < 2 or row[0] is None or row[1] is None:
            invalid_rows.append(row_num)
            continue
        
        variant_word = str(row[0]).strip()
        original_word = str(row[1]).strip()
        
        if not variant_word or not original_word:
            invalid_rows.append(row_num)
            continue
        
        if original_word not in sensitive_map:
            no_match_rows.append(row_num)
            continue
        
        sensitive_id = sensitive_map[original_word]
        
        cursor.execute('SELECT id FROM variant_words WHERE variant_word = ?', (variant_word,))
        if cursor.fetchone():
            duplicate_rows.append(row_num)
            continue
        
        try:
            cursor.execute('INSERT INTO variant_words (variant_word, sensitive_id) VALUES (?, ?)', 
                        (variant_word, sensitive_id))
            success_count += 1
        except Exception as e:
            invalid_rows.append(row_num)
    
    conn.commit()
    conn.close()
    
    return {
        'success': success_count,
        'duplicate': duplicate_rows,
        'invalid': invalid_rows,
        'no_match': no_match_rows
    }

def generate_sensitive_template():
    return generate_single_column_template('敏感词')

def generate_variant_template():
    return generate_double_column_template('变形词', '对应敏感词')