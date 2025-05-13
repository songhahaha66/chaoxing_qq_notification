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
  height: 30px;
  margin-right: auto; /* 使标题占据左侧空间 */
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
  justify-content: flex-start; /* 改为左对齐，让标题和按钮靠近 */
  gap: 20px; /* 控制标题和按钮之间的间距 */
  margin-bottom: 10px;
}
.refresh-btn {
  margin-left: 10px; /* 确保按钮与标题有一定间距 */
}

.card-row {
  display: flex;
  flex-direction: row;     /* 水平排列 */
  flex-wrap: wrap;         /* 允许换行 */
  gap: 20px;               /* 卡片间距 */
  padding: 10px 15px;
}

.homework-card-wrapper {
  width: calc(50% - 20px); /* 每行两个卡片 */
  min-width: 280px;
  margin-bottom: 0;
  flex-grow: 0;            /* 防止卡片伸展 */
}

.clickable-card {
  height: 100%;            /* 确保同一行卡片高度一致 */
  /* 移除 max-width 和 margin，因为现在由 wrapper 控制宽度和位置 */
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;     /* 确保垂直居中对齐 */
  gap: 10px;               /* 控制标题和按钮间距 */
  min-height: 40px;        /* 保持一致的最小高度 */
}

.homework-name {
  font-weight: bold;
  margin-right: 0;         /* 移除右侧边距，使用上面的gap控制 */
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  align-self: center;      /* 确保自身居中 */
  display: flex;           /* 使元素能够垂直对齐 */
  align-items: center;     /* 垂直居中 */
  max-width: calc(100% - 110px); /* 给按钮留出空间 */
}

/* 确保卡片内按钮对齐 */
.card-header .el-button {
  align-self: center;     /* 按钮自身垂直居中 */
  flex-shrink: 0;         /* 防止按钮被压缩 */
}

/* 响应式调整 */
@media (min-width: 1200px) {
  .homework-card-wrapper {
    width: calc(33.333% - 20px); /* 大屏幕时每行三个卡片 */
  }
}

@media (max-width: 768px) {
  .homework-card-wrapper {
    width: 100%; /* 小屏幕时每行一个卡片 */
  }
}
</style>

