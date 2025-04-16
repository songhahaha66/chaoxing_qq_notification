<script setup lang="ts">
import router from '@/router';
import axios from 'axios';
import { ElButton, ElInput, ElSpace, ElText } from 'element-plus';
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
import { ref } from 'vue';
const username = ref('');
const password = ref('');
const errorMessage = ref('');

const login = async () => {
  const username = (document.getElementById('username') as HTMLInputElement).value;
  const password = (document.getElementById('password') as HTMLInputElement).value;
  try {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);

    const response = await api.post('/token', formData, {
      headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
      }
    });
    const access_token = response.data.access_token;
    localStorage.setItem('access_token', access_token);
    const refresh_token = response.data.refresh_token;
    localStorage.setItem('refresh_token', refresh_token);
    router.push('/');
  } catch (error) {
    if (axios.isAxiosError(error)) {
      if (error.response) {
        errorMessage.value = '用户名或密码错误';
      } else {
        // The request was made but no response was received
        errorMessage.value = '网络错误，请稍后再试';
      }
    }
  }
};
try{
  const access_token = localStorage.getItem('access_token');
  const refresh_token = localStorage.getItem('refresh_token');
  if (access_token && refresh_token) {
    router.push('/');
  }
} catch (error) {
  console.error('Error retrieving tokens:', error);
}
</script>

<template>
  <main>
  <ElSpace 
  direction="vertical" 
  style="border-radius: var(--el-border-radius-round); border: 1px solid #ccc; padding: 20px;">
  <ElText type="primary" size="large">超星学习通作业查询系统</ElText>
  <ElInput id="username" v-model="username" placeholder="账户"></ElInput>
  <ElInput id="password" v-model="password" type="password" placeholder="密码"></ElInput>
  <ElButton id="loginButton" type="primary" @click="login">登陆</ElButton>
  <ElText type="danger" size="small" v-if="errorMessage">{{ errorMessage }}</ElText>
  </ElSpace>
  </main>
</template>
<style scoped>
main {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%; /* Full viewport height for centering */
}

.username,
.password,
.loginButton {
  align-items: center;
  justify-content: center;
  width: 100%;
  display: flex; /* Added display flex for proper alignment */
}

</style>

