<script setup lang="ts">
import { ElContainer,ElHeader,ElAside,ElMain, ElButton, ElScrollbar, ElMenu, ElMenuItem, ElPageHeader } from 'element-plus';
import { useRoute } from 'vue-router';
import { ref } from 'vue';
import router from './router';

const route = useRoute();
const isCollapsed = ref(true); // 默认折叠

const toggleSidebar = () => {
  isCollapsed.value = !isCollapsed.value;
};

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
   <ElHeader class="main_header">
     <ElButton 
       type="text" 
       @click="toggleSidebar" 
       class="collapse-btn"
       size="large"
     >
       {{ isCollapsed ? '☰' : '✕' }}
     </ElButton>
     <span class="header-title">超星学习通作业查询系统</span>
   </ElHeader>
    <ElContainer>
    <ElAside :width="isCollapsed ? '0px' : '15%'" :style="{ overflow: 'hidden' }">
      <ElScrollbar v-if="!isCollapsed"> 
        <ElMenu 
          :router="true" 
          default-active="/" 
          :collapse="false"
          :collapse-transition="false"
        >
          <ElMenuItem index="/">
            <template #title>主页</template>
          </ElMenuItem>
          <ElMenuItem index="about">
            <template #title>关于</template>
          </ElMenuItem>
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
  align-items: center;
  font-size: large;
  width: 100%;
  height: 100%;
}

.collapse-btn {
  margin-right: 12px;
  color: #409eff;
}

.collapse-btn:hover {
  background-color: #ecf5ff;
}

.header-title {
  font-size: large;
  font-weight: 600;
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
