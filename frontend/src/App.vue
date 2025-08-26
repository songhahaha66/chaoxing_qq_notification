<script setup lang="ts">
import { ElContainer,ElHeader,ElAside,ElMain, ElButton, ElScrollbar, ElMenu, ElMenuItem, ElPageHeader } from 'element-plus';
import { useRoute } from 'vue-router';
import router from './router';
const route = useRoute();
try{
  const access_token = localStorage.getItem('access_token');
  const refresh_token = localStorage.getItem('refresh_token');
  if (!access_token || !refresh_token) {
    router.push('/login');
  }
} catch (error) {
  router.push('/login');
}
</script>

<template>
 <div class="common-layout" v-if="route.path !== '/login'">
  <ElContainer>
   <ElHeader class="main_header">超星学习通作业查询系统</ElHeader>
    <ElContainer>
    <ElAside>
      <ElScrollbar> 
        <ElMenu :router="true" default-active="/">
          <ElMenuItem index="/">主页</ElMenuItem>
          <ElMenuItem index="about">关于</ElMenuItem>
        </ElMenu>
      </ElScrollbar>
    </ElAside>
    <ElMain>
      <RouterView />
    </ElMain>
  </ElContainer>
  </ElContainer>
 </div>
  <div class="login-layout" v-else>
  <RouterView />
 </div>
</template>

<style scoped>
.el-header {
  display: flex;
  align-items: center;   /* 垂直居中 */
  justify-content: flex-start; /* 内容靠左 */
  text-align: left;      /* 保持左对齐 */
  font-size: large;
  width: 100%;
  height: 100%;
  line-height: 100%;
}
.el-aside {
  width: 15%;
}
.common-layout {
  position: fixed;
  top: 0;
  left: 0;
  height: 100vh;
  width: 100vw;
}
.login-layout {
  position: fixed;
  top: 0;
  left: 0;
  height: 100vh;
  width: 100vw;
  display: flex;
  align-items: center;
  justify-content: center;
}
.main_header {
  border: 1px solid var(--el-border-color);
  height: 4rem;
}

</style>
