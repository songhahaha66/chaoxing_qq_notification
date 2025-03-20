# 数据库的创建
```
CREATE TABLE homework  (
  taskrefId SERIAL PRIMARY KEY,
  subject VARCHAR(255) NOT NULL,
  homework_name TEXT NOT NULL,
  due_date TIMESTAMP,
  status TEXT NOT NULL,
  url TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```
创建了表 homework。