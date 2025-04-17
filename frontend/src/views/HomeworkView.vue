<script setup lang="ts">
import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL
});

api.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config;
    // 判断是否返回 401 且没有重试过，防止死循环
    if (error.response && error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const refresh_token = localStorage.getItem('refresh_token');
      try {
        // 调用刷新 token 的接口（假设接口为 /refresh，传递 refresh_token）
        const response = await axios.post(
          `${import.meta.env.VITE_API_BASE_URL}/refresh-token`,
          { refresh_token },
          { headers: { 'Content-Type': 'application/json' } }
        );
        const newAccessToken = response.data.access_token;
        localStorage.setItem('access_token', newAccessToken);
        // 更新请求头中的 Authorization 并重试原请求
        originalRequest.headers['Authorization'] = `Bearer ${newAccessToken}`;
        return axios(originalRequest);
      } catch (refreshError) {
        // 刷新失败时清除 token 并跳转登录页
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

const homeworkData = ref<any[]>([]);
const all_pages = ref(0);
const i = ref(1);
const req = (i: number) => api.get('/get/homework',
  {
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('access_token')}`
    },
    params: {
      page: i,
      page_size: 20
    }
  },
).then(response => {
  const data = response.data;
  console.log(data);
  homeworkData.value = data['data'];
  all_pages.value = data['total_pages'];
}).catch(error => {
  console.error('Error fetching homework data:', error);
});
onMounted(() => {
  req(i.value);
});

const jumpXxt = (url: string) => {
  window.location.href = url;
}

const remainingTime = (dueDate: string) => {
  const now = new Date();
  const due = new Date(dueDate);
  const diff = due.getTime() - now.getTime();
  return Math.floor(diff / (1000 * 60 * 60)); // 返回剩余小时数
}

const refresh = () => api.get('/update/homework',
  {
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('access_token')}`
    }
  }
).then(response => {
  const update_homework_msg = response.data;
  console.log(update_homework_msg);
}).catch(error => {
  console.error('Error fetching homework data:', error);
});

import { ElButton, ElCard, ElInput, ElRow, ElScrollbar, ElSpace, ElText } from 'element-plus';
import { onMounted, ref } from 'vue';
</script>

<template>
  <main>
    <div v-if="homeworkData" class="homework_data">
      <ElRow class="title_header">
        <ElText size="large" class="homework_header">作业列表</ElText>
        <div class="refresh"><ElButton @click="refresh" type="primary">刷新</ElButton></div>
      </ElRow>
        <ElRow :gutter="20">
      <div v-for="(homework, index) in homeworkData" :key="index" style="width: 300px; height: 210px; margin: 0 20px;">
        <ElCard>
          <template #header>
        <ElSpace>
          <ElText>{{ homework.homework_name }}</ElText>
          <ElText v-if="homework.status === '未提交'" type="danger">还有{{ remainingTime(homework.due_date) }}小时截止</ElText>
          <ElButton @click="jumpXxt(homework.url)" type="primary">查看</ElButton>
        </ElSpace>
          </template>
          <div>
        <div>{{ homework.subject }}</div>
        <div v-if="homework.status==='未提交'">{{ homework.due_date }}</div>
        <div>{{ homework.status }}</div>
          </div>
        </ElCard>
      </div>
    </ElRow>
    <ElRow>
      <ElSpace>
        <ElButton @click="req(--i)" :disabled="i <= 1" type="primary">上一页</ElButton>
        <ElButton @click="req(++i)" :disabled="i >= all_pages" type="primary">下一页</ElButton>
      </ElSpace>
    </ElRow>
    </div>
    <div v-else>
      <ElText>No homework data available.</ElText>
    </div>
  
  </main>
</template>
<style scoped>
.homework_header {
  display: flex;
  align-items: center;
  justify-content: left;
  font-size: large;
  height: 30px;
}
.homework_data{
  height: 100vh;
  overflow-y: auto;
}
.title_header {
  display: flex;
}
.refresh {
  margin:0 20px;
}
</style>