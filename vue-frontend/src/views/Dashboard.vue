<template>
  <div class="dashboard">
    <header class="header">
      <h1>敏感词检测系统</h1>
      <button @click="handleLogout" class="logout-btn">退出登录</button>
    </header>
    
    <div class="tab-container">
      <div class="tabs">
        <button 
          v-for="tab in tabs" 
          :key="tab.key"
          @click="activeTab = tab.key"
          :class="['tab-btn', { active: activeTab === tab.key }]"
        >
          {{ tab.label }}
        </button>
      </div>
      
      <div class="tab-content">
        <keep-alive>
          <DetectPanel v-show="activeTab === 'detect'" />
        </keep-alive>
        <SensitiveWordPanel v-if="activeTab === 'sensitive'" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import DetectPanel from '../components/DetectPanel.vue'
import SensitiveWordPanel from '../components/SensitiveWordPanel.vue'

const router = useRouter()
const activeTab = ref('detect')
const tabs = [
  { key: 'detect', label: '敏感词检测' },
  { key: 'sensitive', label: '敏感词管理' }
]

const handleLogout = () => {
  localStorage.removeItem('token')
  router.push('/login')
}
</script>

<style scoped>
.dashboard {
  min-height: 100vh;
  background: #f5f7fa;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 32px;
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.header h1 {
  font-size: 20px;
  color: #333;
  margin: 0;
}

.logout-btn {
  padding: 8px 20px;
  background: #e74c3c;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.3s;
}

.logout-btn:hover {
  background: #c0392b;
}

.tab-container {
  max-width: 1200px;
  margin: 24px auto;
  padding: 0 24px;
}

.tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
  background: white;
  padding: 8px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.tab-btn {
  padding: 12px 24px;
  border: none;
  background: transparent;
  color: #666;
  font-size: 14px;
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.3s;
}

.tab-btn:hover {
  background: #f5f7fa;
}

.tab-btn.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.tab-content {
  background: white;
  padding: 24px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  min-height: 500px;
}
</style>
