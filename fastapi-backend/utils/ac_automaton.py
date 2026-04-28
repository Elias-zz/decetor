class ACNode:
    def __init__(self):
        self.children = {}
        self.fail = None
        self.is_end = False
        self.word = None
        self.sensitive_id = None

class ACAutomaton:
    def __init__(self):
        self.root = ACNode()
    
    def insert(self, word, sensitive_id=None):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = ACNode()
            node = node.children[char]
        node.is_end = True
        node.word = word
        node.sensitive_id = sensitive_id
    
    def build(self):
        from collections import deque
        queue = deque()
        
        for child in self.root.children.values():
            child.fail = self.root
            queue.append(child)
        
        while queue:
            current_node = queue.popleft()
            
            for char, child in current_node.children.items():
                fail_node = current_node.fail
                while fail_node is not None and char not in fail_node.children:
                    fail_node = fail_node.fail
                
                child.fail = fail_node.children[char] if fail_node else self.root
                queue.append(child)
    
    def search(self, text):
        results = []
        node = self.root
        n = len(text)
        
        for i in range(n):
            char = text[i]
            
            while node is not None and char not in node.children:
                node = node.fail
            
            if node is None:
                node = self.root
                continue
            
            node = node.children[char]
            
            temp_node = node
            while temp_node is not self.root:
                if temp_node.is_end:
                    word_len = len(temp_node.word)
                    start = i - word_len + 1
                    results.append({
                        'word': temp_node.word,
                        'start': start,
                        'end': i + 1,
                        'sensitive_id': temp_node.sensitive_id
                    })
                temp_node = temp_node.fail
        
        return results