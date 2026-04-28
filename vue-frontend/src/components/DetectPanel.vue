<template>
  <div class="detect-panel">
    <div class="input-section">
      <label>待检测文本</label>
      <textarea
        v-model="text"
        placeholder="请输入需要检测的文本..."
        rows="8"
        class="text-input"
      ></textarea>
      <div class="btn-group">
        <button
          @click="handleDetect"
          :disabled="loading || !text.trim()"
          class="detect-btn"
        >
          {{ loading ? '检测中...' : '开始检测' }}
        </button>
        <button
          @click="handleClear"
          :disabled="loading"
          class="clear-btn"
        >
          清空
        </button>
      </div>
    </div>

    <div v-if="result" class="result-section">
      <div class="result-header">
        <div class="stats">
          <span class="stat-item">
            <span class="stat-label">敏感词命中</span>
            <span class="stat-value red">{{ result.total_count }}</span>
          </span>
        </div>
      </div>

      <div class="result-content">
        <div class="highlight-box">
          <h4>高亮结果</h4>
          <div v-html="highlightText" class="highlight-text"></div>
        </div>

        <div class="matches-box">
          <div class="match-section">
            <h4>敏感词命中列表</h4>
            <div v-if="result.original_matches.length > 0">
              <div
                v-for="(match, index) in result.original_matches"
                :key="index"
                class="match-item red"
              >
                <span class="match-word">{{ match.word }}</span>
                <span class="match-position">位置: {{ match.positions.join(', ') }}</span>
              </div>
            </div>
            <p v-else class="empty-text">无命中</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { detectText } from '../api/sensitive'

const text = ref('')
const loading = ref(false)
const result = ref(null)
const highlightText = ref('')

const handleDetect = async () => {
  if (!text.value.trim()) {
    alert('请输入检测文本')
    return
  }
  loading.value = true
  try {
    const res = await detectText({ text: text.value })
    result.value = res
    renderHighlight(res)
  } catch (err) {
    alert(err.message || '检测失败')
  } finally {
    loading.value = false
  }
}

const handleClear = () => {
  text.value = ''
  result.value = null
  highlightText.value = ''
}

const renderHighlight = (res) => {
  let html = escapeHtml(text.value)
  const hits = []

  res.original_matches.forEach(match => {
    match.positions.forEach(pos => {
      hits.push({
        start: pos,
        end: pos + match.word.length,
        type: 'original',
        word: match.word
      })
    })
  })

  hits.sort((a, b) => b.start - a.start)

  hits.forEach(hit => {
    const before = html.substring(0, hit.start)
    const word = html.substring(hit.start, hit.end)
    const after = html.substring(hit.end)
    const color = '#e74c3c'
    html = before + `<span style="background-color: ${color}; color: white; padding: 2px 4px; border-radius: 2px;">${word}</span>` + after
  })

  highlightText.value = html
}

const escapeHtml = (text) => {
  const div = document.createElement('div')
  div.textContent = text
  return div.innerHTML.replace(/\n/g, '<br>')
}
</script>

<style scoped>
.detect-panel {
  max-width: 1200px;
  margin: 0 auto;
}

.input-section {
  margin-bottom: 32px;
}

.input-section label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
}

.text-input {
  width: 100%;
  padding: 16px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  resize: vertical;
  box-sizing: border-box;
  font-family: inherit;
}

.text-input:focus {
  outline: none;
  border-color: #667eea;
}

.btn-group {
  display: flex;
  gap: 12px;
  margin-top: 12px;
}

.detect-btn {
  padding: 12px 32px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  transition: opacity 0.3s;
}

.detect-btn:hover:not(:disabled) {
  opacity: 0.9;
}

.detect-btn:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

.clear-btn {
  padding: 12px 32px;
  background: #95a5a6;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  transition: background 0.3s;
}

.clear-btn:hover:not(:disabled) {
  background: #7f8c8d;
}

.clear-btn:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

.result-section {
  margin-top: 24px;
}

.result-header {
  margin-bottom: 24px;
}

.stats {
  display: flex;
  gap: 32px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.stat-label {
  color: #666;
  font-size: 14px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #333;
}

.stat-value.red {
  color: #e74c3c;
}

.result-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.highlight-box,
.matches-box {
  background: #fafafa;
  border-radius: 8px;
  padding: 20px;
}

.highlight-box h4,
.matches-box h4 {
  margin: 0 0 16px 0;
  color: #333;
  font-size: 16px;
}

.highlight-text {
  font-size: 14px;
  line-height: 1.8;
  color: #333;
  word-break: break-all;
}

.match-section {
  margin-bottom: 20px;
}

.match-section:last-child {
  margin-bottom: 0;
}

.match-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 6px;
  margin-bottom: 8px;
  font-size: 14px;
}

.match-item.red {
  background: #ffebee;
}

.match-word {
  font-weight: bold;
}

.match-item.red .match-word {
  color: #c62828;
}

.match-position {
  margin-left: auto;
  color: #666;
  font-size: 12px;
}

.empty-text {
  color: #999;
  font-size: 14px;
  text-align: center;
  padding: 20px;
}

@media (max-width: 768px) {
  .result-content {
    grid-template-columns: 1fr;
  }
}
</style>
