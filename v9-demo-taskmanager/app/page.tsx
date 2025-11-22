'use client'

import { useState, useEffect } from 'react'
import { Task, TaskPriority, TaskStatus } from '@/types/task'
import { TaskCard } from '@/components/task-card'
import { Button } from '@/components/ui/button'
import { Plus, Sparkles, Filter } from 'lucide-react'
import { generateId } from '@/lib/utils'

export default function Home() {
  const [tasks, setTasks] = useState<Task[]>([])
  const [isFormOpen, setIsFormOpen] = useState(false)
  const [filter, setFilter] = useState<TaskStatus | 'all'>('all')
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    priority: 'medium' as TaskPriority,
  })

  useEffect(() => {
    const stored = localStorage.getItem('taskflow-tasks')
    if (stored) {
      const parsed = JSON.parse(stored)
      setTasks(parsed.map((t: Task) => ({
        ...t,
        createdAt: new Date(t.createdAt),
        completedAt: t.completedAt ? new Date(t.completedAt) : undefined,
      })))
    }
  }, [])

  useEffect(() => {
    localStorage.setItem('taskflow-tasks', JSON.stringify(tasks))
  }, [tasks])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!formData.title.trim()) return

    const newTask: Task = {
      id: generateId(),
      title: formData.title,
      description: formData.description,
      priority: formData.priority,
      status: 'todo',
      createdAt: new Date(),
    }

    setTasks([newTask, ...tasks])
    setFormData({ title: '', description: '', priority: 'medium' })
    setIsFormOpen(false)
  }

  const handleStatusChange = (id: string, status: TaskStatus) => {
    setTasks(tasks.map(task =>
      task.id === id
        ? { ...task, status, completedAt: status === 'completed' ? new Date() : undefined }
        : task
    ))
  }

  const handleDelete = (id: string) => {
    setTasks(tasks.filter(task => task.id !== id))
  }

  const filteredTasks = filter === 'all' 
    ? tasks 
    : tasks.filter(task => task.status === filter)

  const stats = {
    total: tasks.length,
    todo: tasks.filter(t => t.status === 'todo').length,
    inProgress: tasks.filter(t => t.status === 'in-progress').length,
    completed: tasks.filter(t => t.status === 'completed').length,
  }

  return (
    <main className="container mx-auto px-4 py-8 max-w-4xl">
      <div className="mb-8 text-center">
        <div className="flex items-center justify-center gap-2 mb-2">
          <Sparkles className="w-8 h-8 text-purple-400" />
          <h1 className="text-4xl font-bold text-white">TaskFlow</h1>
        </div>
        <p className="text-gray-300">Built with SuperAgent V9 • Next.js 15 + TypeScript</p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <div className="glass glass-dark rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-white">{stats.total}</div>
          <div className="text-sm text-gray-400">Total Tasks</div>
        </div>
        <div className="glass glass-dark rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-blue-400">{stats.todo}</div>
          <div className="text-sm text-gray-400">To Do</div>
        </div>
        <div className="glass glass-dark rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-yellow-400">{stats.inProgress}</div>
          <div className="text-sm text-gray-400">In Progress</div>
        </div>
        <div className="glass glass-dark rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-green-400">{stats.completed}</div>
          <div className="text-sm text-gray-400">Completed</div>
        </div>
      </div>

      <div className="flex items-center justify-between mb-6">
        <div className="flex gap-2">
          <Button
            variant={filter === 'all' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setFilter('all')}
          >
            All
          </Button>
          <Button
            variant={filter === 'todo' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setFilter('todo')}
          >
            To Do
          </Button>
          <Button
            variant={filter === 'in-progress' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setFilter('in-progress')}
          >
            In Progress
          </Button>
          <Button
            variant={filter === 'completed' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setFilter('completed')}
          >
            Completed
          </Button>
        </div>

        <Button onClick={() => setIsFormOpen(!isFormOpen)}>
          <Plus className="w-4 h-4 mr-2" />
          New Task
        </Button>
      </div>

      {isFormOpen && (
        <form onSubmit={handleSubmit} className="glass glass-dark rounded-lg p-6 mb-6">
          <h2 className="text-xl font-semibold text-white mb-4">Create New Task</h2>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Title
              </label>
              <input
                type="text"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                className="w-full px-4 py-2 rounded-md bg-white/5 border border-white/10 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500"
                placeholder="Enter task title..."
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Description
              </label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                className="w-full px-4 py-2 rounded-md bg-white/5 border border-white/10 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 resize-none"
                placeholder="Add details..."
                rows={3}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Priority
              </label>
              <select
                value={formData.priority}
                onChange={(e) => setFormData({ ...formData, priority: e.target.value as TaskPriority })}
                className="w-full px-4 py-2 rounded-md bg-white/5 border border-white/10 text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </div>

            <div className="flex gap-3">
              <Button type="submit" className="flex-1">
                Create Task
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => setIsFormOpen(false)}
              >
                Cancel
              </Button>
            </div>
          </div>
        </form>
      )}

      <div className="space-y-3">
        {filteredTasks.length === 0 ? (
          <div className="text-center py-12 text-gray-400">
            <p>No tasks found. Create one to get started!</p>
          </div>
        ) : (
          filteredTasks.map(task => (
            <TaskCard
              key={task.id}
              task={task}
              onStatusChange={handleStatusChange}
              onDelete={handleDelete}
            />
          ))
        )}
      </div>
    </main>
  )
}
