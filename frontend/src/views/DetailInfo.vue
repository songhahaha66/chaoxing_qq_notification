<script setup lang="ts">
import axios from 'axios'
import { ElButton } from 'element-plus'
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const homeworkId = route.params.id as string  // 修正：直接从 route.params 取 id

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
  <div v-if="homeworkData">
    <h2>{{ homeworkData.subject }}</h2>
    <p>{{ homeworkData.homework_name }}</p>
    <p>截止：{{ homeworkData.due_date }}</p>
    <p>状态：{{ homeworkData.status }}</p>
    <p>详情：</p>
    <p v-for ="(detail, index) in homeworkData.detail_info" :key="index">
      {{ detail.question }}
      <br>
      {{ detail.description }}
      <br>
    </p>
    <br>
    <ElButton @click="jumpXxt(homeworkData.detail_url)" type="primary">查看</ElButton>
    <!-- 根据实际字段渲染其余详情 -->
  </div>
  <div v-else>
    <p>正在加载...</p>
  </div>
</template>