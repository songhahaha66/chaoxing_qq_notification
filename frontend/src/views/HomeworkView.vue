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
      page_size: 10
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

import { ElButton, ElCard, ElInput, ElRow, ElSpace, ElText } from 'element-plus';
import { onMounted, ref } from 'vue';
</script>

<template>
  <main>
    <div v-if="homeworkData">
        <ElText size="large">作业列表</ElText>
        <ElRow :gutter="20">
      <div v-for="(homework, index) in homeworkData" :key="index" style="width: 300px; height: 200px; margin: 0 20px;">
        <ElCard>
          <template #header>
        <ElSpace>
          <ElText>{{ homework.homework_name }}</ElText>
          <ElButton @click="req(i)" type="primary">查看</ElButton>
        </ElSpace>
          </template>
          <div>
        <div>{{ homework.subject }}</div>
        <div>{{ homework.due_date }}</div>
        <div>{{ homework.status }}</div>
          </div>
        </ElCard>
      </div>
    </ElRow>
      <div v-if="all_pages > 1 && i < all_pages">
        <ElButton @click="req(i++)" type="primary">下一页</ElButton>
      </div>
      <div v-if="all_pages > 1 && i > 1">
        <ElButton @click="req(--i)" type="primary">上一页</ElButton>
      </div>
    </div>
    <div v-else>
      <ElText>No homework data available.</ElText>
    </div>
  
  </main>
</template>
