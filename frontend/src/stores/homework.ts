import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Homework } from '@/types/homework' // Assuming you will create a type definition for Homework
import { useAuthStore } from './auth'
import apiClient from '@/services/api' // Assuming api.ts will be created in services
import { ElMessage } from 'element-plus'

// Define a type for homework items if not already defined elsewhere
// For example, in /src/types/homework.ts
// export interface Homework {
//   taskrefId: string;
//   homework_name: string;
//   subject: string;
//   due_date: string;
//   status: string;
//   detail_url: string;
//   // Add other relevant fields
// }

export const useHomeworkStore = defineStore('homework', () => {
  const homeworkList = ref<Homework[]>([])
  const currentPage = ref(1)
  const totalPages = ref(0)
  const isLoading = ref(false)
  const authStore = useAuthStore()

  async function fetchHomework(page: number = 1) {
    if (!authStore.isAuthenticated) {
      ElMessage.error('用户未登录，无法获取作业列表')
      return
    }
    isLoading.value = true
    try {
      const response = await apiClient.get('/get/homework', {
        params: {
          page: page,
          page_size: 10
        }
      })
      homeworkList.value = response.data.data
      totalPages.value = response.data.total_pages
      currentPage.value = page
    } catch (error) {
      console.error('获取作业列表失败:', error)
      ElMessage.error('获取作业列表失败，请稍后再试')
      homeworkList.value = [] // Clear list on error
      totalPages.value = 0
    } finally {
      isLoading.value = false
    }
  }

  async function refreshHomework() {
    if (!authStore.isAuthenticated) {
      ElMessage.error('用户未登录，无法刷新作业列表')
      return
    }
    isLoading.value = true;
    try {
      await apiClient.get('/update/homework');
      ElMessage.success('作业列表已刷新');
      await fetchHomework(currentPage.value); // Refresh current page after update
    } catch (error) {
      console.error('刷新作业列表失败:', error);
      ElMessage.error('刷新作业列表失败，请稍后再试');
    } finally {
      isLoading.value = false;
    }
  }

  // Function to get homework details, can be added if needed for a dedicated detail store or page
  // async function fetchHomeworkDetail(homeworkId: string) {
  //   if (!authStore.isAuthenticated) return;
  //   isLoading.value = true;
  //   try {
  //     const response = await apiClient.get(`/get/homework/${homeworkId}`);
  //     // Process and store detail data
  //   } catch (error) {
  //     console.error('获取作业详情失败:', error);
  //     ElMessage.error('获取作业详情失败');
  //   } finally {
  //     isLoading.value = false;
  //   }
  // }

  return {
    homeworkList,
    currentPage,
    totalPages,
    isLoading,
    fetchHomework,
    refreshHomework
  }
})

