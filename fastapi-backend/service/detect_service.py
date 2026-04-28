import re
from db.db import get_db_connection

def load_sensitive_words():
    """加载敏感词"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, sensitive_word FROM sensitive_words')
    sensitive_rows = cursor.fetchall()
    
    conn.close()
    
    sensitive_list = [{'id': row['id'], 'word': row['sensitive_word']} for row in sensitive_rows]
    
    return sensitive_list

def generate_weak_variants(word):
    """生成英文弱变形（复数、时态、词根）"""
    variants = {word.lower()}
    lower_word = word.lower()
    
    # 名词复数变形
    if lower_word.endswith('s'):
        variants.add(lower_word[:-1])  # cats -> cat
    if lower_word.endswith('es'):
        variants.add(lower_word[:-2])  # boxes -> box
        variants.add(lower_word[:-1])  # 
    if lower_word.endswith('ies'):
        variants.add(lower_word[:-3] + 'y')  # cities -> city
    
    # 动词时态变形
    if lower_word.endswith('ing'):
        variants.add(lower_word[:-3])  # running -> run
        variants.add(lower_word[:-3] + 'e')  # making -> make
    if lower_word.endswith('ed'):
        variants.add(lower_word[:-2])  # walked -> walk
        variants.add(lower_word[:-1])  # 
    if lower_word.endswith('ied'):
        variants.add(lower_word[:-3] + 'y')  # carried -> carry
    
    # 形容词比较级/最高级
    if lower_word.endswith('er'):
        variants.add(lower_word[:-2])  # bigger -> big
    if lower_word.endswith('est'):
        variants.add(lower_word[:-3])  # biggest -> big
    
    return variants

def build_full_containment_pattern(word):
    """构建全包含检测正则（连续字母组合，至少3个字母）"""
    if len(word) <= 2:
        return re.escape(word.lower())
    
    # 生成所有可能的连续子串（长度>=3，避免过短匹配如"lo"）
    substrings = set()
    for i in range(len(word)):
        for j in range(i + 3, len(word) + 1):
            substrings.add(word[i:j].lower())
    
    # 按长度降序排序，优先匹配长的
    sorted_substrings = sorted(substrings, key=len, reverse=True)
    
    # 构建正则：匹配任意子串
    pattern = '|'.join(re.escape(s) for s in sorted_substrings)
    return pattern

def detect_sensitive_words(text):
    """
    敏感词检测主函数
    支持：
    1. 精准全词匹配（忽略大小写）
    2. 英文弱变形（复数/时态/词根）
    3. 全包含检测（连续字母组合）
    """
    if not text:
        return {
            'highlight_text': '',
            'original_matches': [],
            'variant_matches': [],
            'original_count': 0,
            'variant_count': 0,
            'total_count': 0
        }
    
    sensitive_list = load_sensitive_words()
    text_lower = text.lower()
    
    # ========== 1. 精准全词匹配（忽略大小写）==========
    original_matches = {}
    
    for item in sensitive_list:
        word = item['word']
        word_lower = word.lower()
        
        # 全词匹配正则：单词边界
        pattern = r'\b' + re.escape(word_lower) + r'\b'
        matches = list(re.finditer(pattern, text_lower))
        
        if matches:
            positions = [m.start() for m in matches]
            original_matches[word_lower] = {
                'word': word,
                'positions': positions,
                'type': 'exact'
            }
    
    # ========== 2. 英文弱变形检测 ==========
    for item in sensitive_list:
        word = item['word']
        word_lower = word.lower()
        
        # 如果是英文单词，检查弱变形
        if word.isalpha():
            weak_variants = generate_weak_variants(word)
            
            for variant in weak_variants:
                if variant == word_lower:
                    continue  # 跳过原词，已处理
                
                pattern = r'\b' + re.escape(variant) + r'\b'
                matches = list(re.finditer(pattern, text_lower))
                
                if matches:
                    positions = [m.start() for m in matches]
                    # 合并到原词的命中位置
                    if word_lower in original_matches:
                        existing_pos = set(original_matches[word_lower]['positions'])
                        for pos in positions:
                            if pos not in existing_pos:
                                original_matches[word_lower]['positions'].append(pos)
                    else:
                        original_matches[word_lower] = {
                            'word': word,
                            'positions': positions,
                            'type': 'weak_variant'
                        }
    
    # ========== 3. 全包含检测（连续字母组合）==========
    containment_matches = {}
    
    for item in sensitive_list:
        word = item['word']
        word_lower = word.lower()
        
        # 构建全包含正则
        containment_pattern = build_full_containment_pattern(word)
        
        # 查找所有匹配（不限制单词边界，任意位置）
        matches = list(re.finditer(containment_pattern, text_lower))
        
        for match in matches:
            matched_text = match.group()
            pos = match.start()
            
            # 检查这个位置是否已经被精准匹配覆盖
            already_covered = False
            if word_lower in original_matches:
                for existing_pos in original_matches[word_lower]['positions']:
                    if existing_pos <= pos < existing_pos + len(word):
                        already_covered = True
                        break
            
            if not already_covered:
                key = f"{word_lower}:{matched_text}"
                if key not in containment_matches:
                    containment_matches[key] = {
                        'word': word,
                        'matched_fragment': matched_text,
                        'positions': [],
                        'type': 'containment'
                    }
                containment_matches[key]['positions'].append(pos)
    
    # ========== 4. 整合结果 ==========
    
    # 合并全包含结果到原始匹配
    for key, data in containment_matches.items():
        word = data['word']
        word_lower = word.lower()
        
        if word_lower in original_matches:
            existing_pos = set(original_matches[word_lower]['positions'])
            for pos in data['positions']:
                if pos not in existing_pos:
                    original_matches[word_lower]['positions'].append(pos)
        else:
            original_matches[word_lower] = {
                'word': word,
                'positions': data['positions'],
                'type': 'containment'
            }
    
    # 构建高亮文本
    highlight_text = build_highlight_text(text, original_matches)
    
    # 格式化输出
    original_output = []
    for data in original_matches.values():
        original_output.append({
            'word': data['word'],
            'positions': sorted(data['positions']),
            'type': data.get('type', 'exact')
        })
    
    # 去重并按位置排序
    original_output = sorted(original_output, key=lambda x: x['positions'][0] if x['positions'] else 0)
    
    # 计算总命中次数（不去重）
    total_hits = sum(len(data['positions']) for data in original_matches.values())
    
    result = {
        'highlight_text': highlight_text,
        'original_matches': original_output,
        'variant_matches': [],
        'original_count': total_hits,
        'variant_count': 0,
        'total_count': total_hits
    }
    
    return result

def build_highlight_text(text, original_matches):
    """构建高亮文本"""
    # 收集所有命中位置
    hits = []
    
    for data in original_matches.values():
        word = data['word']
        for pos in data['positions']:
            hits.append({
                'start': pos,
                'end': pos + len(word),
                'word': word,
                'type': 'original'
            })
    
    # 按位置排序，处理重叠
    hits.sort(key=lambda x: (x['start'], -x['end']))
    
    # 去除重叠
    filtered_hits = []
    used_ranges = []
    
    for hit in hits:
        overlap = False
        for used in used_ranges:
            if not (hit['end'] <= used['start'] or hit['start'] >= used['end']):
                overlap = True
                break
        
        if not overlap:
            filtered_hits.append(hit)
            used_ranges.append({'start': hit['start'], 'end': hit['end']})
    
    # 按位置倒序插入高亮标签
    filtered_hits.sort(key=lambda x: x['start'], reverse=True)
    
    html = text
    for hit in filtered_hits:
        before = html[:hit['start']]
        word = html[hit['start']:hit['end']]
        after = html[hit['end']:]
        
        color = '#e74c3c'
        html = before + f'<span style="background-color: {color}; color: white; padding: 2px 4px; border-radius: 2px;">{word}</span>' + after
    
    return html
