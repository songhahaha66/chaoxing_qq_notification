export interface Homework {
  taskrefId: string;
  homework_name: string;
  subject: string;
  due_date: string;
  status: string;
  detail_url: string;
  // 其他可能的字段
  description?: string;
  created_at?: string;
  updated_at?: string;
}
