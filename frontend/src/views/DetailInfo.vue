<script setup lang="ts">
import axios from 'axios'
import { ElButton } from 'element-plus'
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const homeworkId = route.params.id as string

const homeworkData = ref<any>(null)
const jumpXxt = (url: string) => {
  window.location.href = url;
}
onMounted(async () => {
  try {
    const res = await axios.get(
      `${import.meta.env.VITE_API_BASE_URL}/get/homework/${homeworkId}`,
      {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      }
    )
    homeworkData.value = res.data.data
  } catch (err) {
    console.error('Error fetching homework details:', err)
  }
})
</script>

<template>
  <div class="detail-info-container">
    <div v-if="homeworkData" class="content-wrapper">
      <h2>{{ homeworkData.subject }}</h2>
      <p><strong>作业名称:</strong> {{ homeworkData.homework_name }}</p>
      <p><strong>截止时间:</strong> {{ homeworkData.due_date }}</p>
      <p><strong>状态:</strong> {{ homeworkData.status }}</p>
      <p><strong>详情内容:</strong></p>
      <div v-for="(detail, index) in homeworkData.detail_info" :key="index" class="detail-item">
        <p class="question-title">问题 {{ index + 1 }}: {{ detail.question }}</p>
        <p class="question-description">{{ detail.description }}</p>
      </div>
      <br>
      <ElButton @click="jumpXxt(homeworkData.detail_url)" type="primary" style="margin-top: 10px;">在学习通中查看</ElButton>
    </div>
    <div v-else class="loading-wrapper">
      <p>正在加载作业详情...</p>
    </div>
  </div>
</template>

<style scoped>
.detail-info-container {
  padding: 20px;
  height: 100%; /* Assumes parent provides a constrained height. */
  overflow-y: auto;
  /* If the component is meant to be the main scrollable area of a page: */
  /* max-height: 100vh; /* Ensures it doesn't exceed viewport height, allowing scroll */
  box-sizing: border-box;
}

.content-wrapper h2 {
  margin-top: 0;
  margin-bottom: 16px;
  font-size: 1.5em;
  color: #333;
}

.content-wrapper p {
  margin-bottom: 8px;
  line-height: 1.6;
}

.detail-item {
  background-color: #f9f9f9;
  border: 1px solid #eee;
  padding: 10px;
  margin-bottom: 10px;
  border-radius: 4px;
}

.detail-item .question-title {
  font-weight: bold;
  margin-bottom: 5px;
}

.detail-item .question-description {
  color: #555;
}

.loading-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px; /* Or 100% if container has height */
}
</style>

