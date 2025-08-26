<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { ElButton, ElInput, ElSpace, ElText, ElMessage } from 'element-plus';
import { useAuthStore } from '@/stores/auth';
import apiClient from '@/services/api';

const router = useRouter();
const authStore = useAuthStore();

const username = ref('');
const password = ref('');
const isLoading = ref(false);

// Redirect if already logged in
onMounted(() => {
  if (authStore.isAuthenticated) {
    router.push('/');
  }
});

const login = async () => {
  if (!username.value || !password.value) {
    ElMessage.error('请输入账户和密码');
    return;
  }
  isLoading.value = true;
  try {
    const formData = new FormData();
    formData.append('username', username.value);
    formData.append('password', password.value);

    const response = await apiClient.post('/token', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    });

    const accessToken = response.data.access_token;
    const refreshToken = response.data.refresh_token;
    authStore.setTokens(accessToken, refreshToken);
    ElMessage.success('登录成功');
    router.push('/');
  } catch (error: any) {
    if (error.response && error.response.data && error.response.data.detail) {
      ElMessage.error(error.response.data.detail);
    } else if (error.message && error.message.includes('Network Error')) {
       ElMessage.error('网络错误，请检查您的网络连接。');
    } else {
      ElMessage.error('登录失败，请检查您的账户或密码。');
    }
    console.error('Login error:', error);
  } finally {
    isLoading.value = false;
  }
};
</script>

<template>
  <main class="login-container">
    <div class="login-box">
      <ElText type="primary" size="large" class="login-title">超星学习通作业查询系统</ElText>
      <ElInput v-model="username" placeholder="账户" size="large" clearable class="login-input"/>
      <ElInput v-model="password" type="password" placeholder="密码" size="large" show-password @keyup.enter="login" class="login-input"/>
      <ElButton type="primary" @click="login" :loading="isLoading" class="login-button" size="large">登录</ElButton>
    </div>
  </main>
</template>

<style scoped>
.login-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 1rem;
}

.login-box {
  background-color: #ffffff;
  padding: 2rem;
  border-radius: 0.5rem;
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 24rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.login-title {
  text-align: center;
  display: block;
  font-size: 1.5rem;
  color: #333;
}

.login-input {
  font-size: 1rem;
}

.login-button {
  width: 100%;
  font-size: 1rem;
}

@media (min-width: 768px) {
  .login-box {
    padding: 2.5rem;
  }
  .login-title {
    font-size: 1.75rem;
  }
}
</style>

