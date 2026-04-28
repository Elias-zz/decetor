<template>
  <div class="sensitive-panel">
    <div class="panel-header">
      <div class="search-box">
        <input
          v-model="searchText"
          placeholder="搜索敏感词..."
          @input="handleSearch"
          class="search-input"
        />
      </div>
      <div class="action-btns">
        <button @click="downloadTemplate" class="action-btn">
          下载模板
        </button>
        <label class="upload-btn">
          <input
            type="file"
            accept=".xlsx,.xls"
            @change="handleImport"
            class="file-input"
          />
          导入Excel
        </label>
        <button @click="showAddModal = true" class="action-btn primary">
          添加敏感词
        </button>
      </div>
    </div>

    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>敏感词</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in list" :key="item.id">
            <td>{{ item.id }}</td>
            <td>{{ item.sensitive_word }}</td>
            <td>
              <button @click="handleEdit(item)" class="edit-btn">编辑</button>
              <button @click="handleDelete(item.id)" class="delete-btn">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="list.length === 0" class="empty-state">
        <p>暂无数据</p>
      </div>
    </div>

    <div class="pagination" v-if="total > pageSize">
      <button
        @click="prevPage"
        :disabled="currentPage === 1"
        class="page-btn"
      >
        上一页
      </button>
      <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
      <button
        @click="nextPage"
        :disabled="currentPage === totalPages"
        class="page-btn"
      >
        下一页
      </button>
    </div>

    <div v-if="showAddModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal">
        <h3>{{ editItem ? '编辑敏感词' : '添加敏感词' }}</h3>
        <div class="form-group">
          <label>敏感词</label>
          <input
            v-model="form.sensitive_word"
            type="text"
            placeholder="请输入敏感词"
            class="modal-input"
          />
        </div>
        <div class="modal-actions">
          <button @click="closeModal" class="modal-btn cancel">取消</button>
          <button @click="handleSave" class="modal-btn confirm">确定</button>
        </div>
      </div>
    </div>

    <div v-if="showImportModal" class="modal-overlay" @click.self="showImportModal = false">
      <div class="modal">
        <h3>导入结果</h3>
        <div class="import-result">
          <p>成功导入: {{ importResult.success }} 条</p>
          <p v-if="importResult.duplicate.length > 0">
            重复跳过: {{ importResult.duplicate.length }} 条 (行: {{ importResult.duplicate.join(', ') }})
          </p>
          <p v-if="importResult.invalid.length > 0">
            无效数据: {{ importResult.invalid.length }} 条 (行: {{ importResult.invalid.join(', ') }})
          </p>
        </div>
        <div class="modal-actions">
          <button @click="showImportModal = false" class="modal-btn confirm">确定</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import {
  getSensitiveWords,
  createSensitiveWord,
  updateSensitiveWord,
  deleteSensitiveWord,
  importSensitiveWords,
  downloadSensitiveTemplate
} from '../api/sensitive'

const list = ref([])
const searchText = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const showAddModal = ref(false)
const showImportModal = ref(false)
const editItem = ref(null)
const form = ref({ sensitive_word: '' })
const importResult = ref({ success: 0, duplicate: [], invalid: [] })

const totalPages = computed(() => Math.ceil(total.value / pageSize.value))

const loadList = async () => {
  try {
    const params = {
      page: currentPage.value,
      size: pageSize.value,
      keyword: searchText.value
    }
    const res = await getSensitiveWords(params)
    list.value = res.list
    total.value = res.total
  } catch (err) {
    alert(err.message)
  }
}

const handleSearch = () => {
  currentPage.value = 1
  loadList()
}

const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
    loadList()
  }
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
    loadList()
  }
}

const handleEdit = (item) => {
  editItem.value = item
  form.value = { sensitive_word: item.sensitive_word }
  showAddModal.value = true
}

const closeModal = () => {
  showAddModal.value = false
  editItem.value = null
  form.value = { sensitive_word: '' }
}

const handleSave = async () => {
  if (!form.value.sensitive_word.trim()) {
    alert('请输入敏感词')
    return
  }
  try {
    if (editItem.value) {
      await updateSensitiveWord(editItem.value.id, form.value)
      alert('修改成功')
    } else {
      await createSensitiveWord(form.value)
      alert('添加成功')
    }
    closeModal()
    loadList()
  } catch (err) {
    alert(err.message)
  }
}

const handleDelete = async (id) => {
  if (!confirm('确定要删除吗？')) return
  try {
    await deleteSensitiveWord(id)
    alert('删除成功')
    loadList()
  } catch (err) {
    alert(err.message)
  }
}

const downloadTemplate = async () => {
  try {
    await downloadSensitiveTemplate()
    alert('模板下载成功')
  } catch (err) {
    alert(err.message)
  }
}

const handleImport = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  const formData = new FormData()
  formData.append('file', file)

  try {
    const res = await importSensitiveWords(formData)
    importResult.value = res
    showImportModal.value = true
    loadList()
  } catch (err) {
    alert(err.message)
  } finally {
    event.target.value = ''
  }
}

onMounted(() => {
  loadList()
})
</script>

<style scoped>
.sensitive-panel {
  max-width: 1200px;
  margin: 0 auto;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.search-box {
  flex: 1;
  max-width: 300px;
}

.search-input {
  width: 100%;
  padding: 10px 16px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
}

.search-input:focus {
  outline: none;
  border-color: #667eea;
}

.action-btns {
  display: flex;
  gap: 12px;
}

.action-btn {
  padding: 10px 20px;
  background: #f5f7fa;
  border: 1px solid #ddd;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.action-btn:hover {
  background: #e8eaed;
}

.action-btn.primary {
  background: #667eea;
  color: white;
  border-color: #667eea;
}

.action-btn.primary:hover {
  background: #5a6fd6;
}

.upload-btn {
  padding: 10px 20px;
  background: #f5f7fa;
  border: 1px solid #ddd;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  display: inline-flex;
  align-items: center;
}

.upload-btn:hover {
  background: #e8eaed;
}

.file-input {
  display: none;
}

.table-container {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.data-table th,
.data-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.data-table th {
  background: #f5f7fa;
  font-weight: 600;
  color: #333;
}

.data-table tr:hover {
  background: #fafafa;
}

.edit-btn,
.delete-btn {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  margin-right: 8px;
}

.edit-btn {
  background: #3498db;
  color: white;
}

.edit-btn:hover {
  background: #2980b9;
}

.delete-btn {
  background: #e74c3c;
  color: white;
}

.delete-btn:hover {
  background: #c0392b;
}

.empty-state {
  text-align: center;
  padding: 60px;
  color: #999;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 24px;
}

.page-btn {
  padding: 8px 16px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 4px;
  cursor: pointer;
}

.page-btn:hover:not(:disabled) {
  background: #f5f7fa;
}

.page-btn:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

.page-info {
  font-size: 14px;
  color: #666;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal {
  background: white;
  border-radius: 8px;
  padding: 24px;
  width: 400px;
}

.modal h3 {
  margin: 0 0 20px 0;
  color: #333;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
}

.modal-input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  box-sizing: border-box;
}

.modal-input:focus {
  outline: none;
  border-color: #667eea;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}

.modal-btn {
  padding: 10px 24px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.modal-btn.cancel {
  background: #f5f7fa;
  color: #666;
}

.modal-btn.confirm {
  background: #667eea;
  color: white;
}

.import-result {
  font-size: 14px;
  line-height: 2;
}
</style>