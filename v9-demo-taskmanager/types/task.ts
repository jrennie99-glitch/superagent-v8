export type TaskPriority = 'low' | 'medium' | 'high'
export type TaskStatus = 'todo' | 'in-progress' | 'completed'

export interface Task {
  id: string
  title: string
  description: string
  priority: TaskPriority
  status: TaskStatus
  createdAt: Date
  completedAt?: Date
}

export interface TaskFormData {
  title: string
  description: string
  priority: TaskPriority
}
