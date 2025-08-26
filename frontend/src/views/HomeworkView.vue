<script setup lang="ts">
import { onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { ElButton, ElCard, ElRow, ElSpace, ElText, ElMessage, ElLoadingDirective } from 'element-plus';
import { useHomeworkStore } from '@/stores/homework';
import { useAuthStore } from '@/stores/auth';

const router = useRouter();
const homeworkStore = useHomeworkStore();
const authStore = useAuthStore();

// Directly use store state, which is already reactive
const homeworkData = computed(() => homeworkStore.homeworkList);
const isLoading = computed(() => homeworkStore.isLoading);
const currentPage = computed(() => homeworkStore.currentPage);
const totalPages = computed(() => homeworkStore.totalPages);

onMounted(() => {
  if (authStore.isAuthenticated) {
    homeworkStore.fetchHomework(1); // Fetch first page on mount
  } else {
    ElMessage.warning('请先登录以查看作业列表');
    router.push('/login');
  }
});

const jumpXxt = (url: string) => {
  if (url) {
    window.open(url, '_blank'); // Open in new tab for better UX
  } else {
    ElMessage.info('该作业没有提供外部链接');
  }
};

const remainingTime = (dueDate: string) => {
  const now = new Date();
  const due = new Date(dueDate);
  const diff = due.getTime() - now.getTime();
  if (diff <= 0) return 0;
  return Math.floor(diff / (1000 * 60 * 60)); // 返回剩余小时数
};

const refresh = () => {
  homeworkStore.refreshHomework();
};

const jumpCard = (taskrefId: string) => {
  if (taskrefId) {
    router.push({ name: 'detail', params: { id: taskrefId } });
  } else {
    ElMessage.warning('作业ID无效，无法跳转详情');
  }
};

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    homeworkStore.fetchHomework(currentPage.value + 1);
  }
};

const prevPage = () => {
  if (currentPage.value > 1) {
    homeworkStore.fetchHomework(currentPage.value - 1);
  }
};

</script>

<template>
  <main v-loading="isLoading">
    <div v-if="authStore.isAuthenticated && homeworkData.length > 0" class="homework_data">
      <ElRow class="title_header" justify="space-between" align="middle">
        <ElText size="large" class="homework_header">作业列表</ElText>
        <ElButton @click="refresh" type="primary" :loading="isLoading" class="refresh-btn">刷新</ElButton>
      </ElRow>
      <ElRow class="card-row">
        <div v-for="(homework) in homeworkData" :key="homework.taskrefId" class="homework-card-wrapper">
          <ElCard @click="jumpCard(homework.taskrefId)" class="clickable-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <ElText truncated class="homework-name">{{ homework.homework_name }}</ElText>
                <ElButton @click.stop="jumpXxt(homework.detail_url)" type="primary" size="small">查看原作业</ElButton>
              </div>
            </template>
            <div>
              <p><strong>科目：</strong>{{ homework.subject }}</p>
              <p v-if="homework.status === '未提交'"><strong>截止时间：</strong>{{ homework.due_date }}</p>
              <p><strong>状态：</strong>
                <ElText :type="homework.status === '未提交' ? 'danger' : (homework.status === '已提交' ? 'success' : 'info')">
                  {{ homework.status }}
                </ElText>
              </p>
              <ElText v-if="homework.status === '未提交' && remainingTime(homework.due_date) > 0" type="danger" size="small">
                还有 {{ remainingTime(homework.due_date) }} 小时截止
              </ElText>
               <ElText v-else-if="homework.status === '未提交' && remainingTime(homework.due_date) <= 0" type="warning" size="small">
                已截止
              </ElText>
            </div>
          </ElCard>
        </div>
      </ElRow>
      <ElRow justify="center" class="pagination-row">
        <ElSpace>
          <ElButton @click="prevPage" :disabled="currentPage <= 1 || isLoading" type="primary">上一页</ElButton>
          <ElText>第 {{ currentPage }} / {{ totalPages }} 页</ElText>
          <ElButton @click="nextPage" :disabled="currentPage >= totalPages || isLoading" type="primary">下一页</ElButton>
        </ElSpace>
      </ElRow>
    </div>
    <div v-else-if="!isLoading && authStore.isAuthenticated && homeworkData.length === 0" class="empty-state">
       <ElRow class="title_header" justify="space-between" align="middle">
        <ElText size="large" class="homework_header">作业列表</ElText>
        <ElButton @click="refresh" type="primary" :loading="isLoading" class="refresh-btn">刷新</ElButton>
      </ElRow>
      <ElText type="info" size="large">暂无作业数据，或尝试刷新列表。</ElText>
    </div>
    <div v-else-if="!authStore.isAuthenticated && !isLoading">
        <ElText type="warning" size="large">请先登录以查看作业列表。</ElText>
    </div>
  </main>
</template>

<style scoped>
.homework_header {
  display: flex;
  align-items: center;
  justify-content: left;
  font-size: large;
  margin-right: auto;
}

.homework_data {
  height: 80vh;
  overflow-y: auto;
  overflow-x: hidden; 
}

.homework_data .el-row {
  flex-wrap: wrap;
}

.title_header {
  display: flex;
  justify-content: flex-start;
  gap: 1.5rem;
  margin-bottom: 0.75rem;
}

.refresh-btn {
  margin-left: 0.75rem;
}

.card-row {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  gap: 1.5rem;
  padding: 0.75rem 1rem;
}

.homework-card-wrapper {
  width: calc(50% - 1.5rem);
  min-width: 18rem;
  margin-bottom: 0;
  flex-grow: 0;
}

.clickable-card {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.75rem;
  min-height: 2.5rem;
}

.homework-name {
  font-weight: bold;
  margin-right: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  align-self: center;
  display: flex;
  align-items: center;
  max-width: calc(100% - 7rem);
}

.card-header .el-button {
  align-self: center;
  flex-shrink: 0;
}

@media (min-width: 1200px) {
  .homework-card-wrapper {
    width: calc(33.333% - 1.5rem);
  }
}

@media (max-width: 768px) {
  .homework-card-wrapper {
    width: 100%;
  }
  
  .card-row {
    padding: 0.5rem;
    gap: 1rem;
  }
  
  .title_header {
    gap: 1rem;
    margin-bottom: 0.5rem;
  }
}
</style>

