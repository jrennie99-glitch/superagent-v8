'use client'

import { Task, TaskStatus } from '@/types/task'
import { Button } from '@/components/ui/button'
import { CheckCircle2, Circle, Trash2, Clock, AlertCircle } from 'lucide-react'
import { cn } from '@/lib/utils'

interface TaskCardProps {
  task: Task
  onStatusChange: (id: string, status: TaskStatus) => void
  onDelete: (id: string) => void
}

export function TaskCard({ task, onStatusChange, onDelete }: TaskCardProps) {
  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'text-red-400 bg-red-500/10 border-red-500/20'
      case 'medium':
        return 'text-yellow-400 bg-yellow-500/10 border-yellow-500/20'
      case 'low':
        return 'text-green-400 bg-green-500/10 border-green-500/20'
      default:
        return 'text-gray-400 bg-gray-500/10 border-gray-500/20'
    }
  }

  const getStatusIcon = () => {
    switch (task.status) {
      case 'completed':
        return <CheckCircle2 className="w-5 h-5 text-green-400" />
      case 'in-progress':
        return <Clock className="w-5 h-5 text-yellow-400" />
      default:
        return <Circle className="w-5 h-5 text-gray-400" />
    }
  }

  return (
    <div className={cn(
      'glass glass-dark rounded-lg p-4 transition-all hover:scale-[1.02]',
      task.status === 'completed' && 'opacity-60'
    )}>
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-3 flex-1">
          <button
            onClick={() => {
              const nextStatus: TaskStatus = 
                task.status === 'todo' ? 'in-progress' :
                task.status === 'in-progress' ? 'completed' : 'todo'
              onStatusChange(task.id, nextStatus)
            }}
            className="mt-1 hover:scale-110 transition-transform"
          >
            {getStatusIcon()}
          </button>
          
          <div className="flex-1">
            <h3 className={cn(
              'font-semibold text-white mb-1',
              task.status === 'completed' && 'line-through text-gray-400'
            )}>
              {task.title}
            </h3>
            <p className="text-sm text-gray-300 mb-2">{task.description}</p>
            
            <div className="flex items-center gap-2">
              <span className={cn(
                'text-xs px-2 py-1 rounded border font-medium',
                getPriorityColor(task.priority)
              )}>
                {task.priority}
              </span>
              <span className="text-xs text-gray-400">
                {new Date(task.createdAt).toLocaleDateString()}
              </span>
            </div>
          </div>
        </div>

        <Button
          variant="ghost"
          size="icon"
          onClick={() => onDelete(task.id)}
          className="text-red-400 hover:text-red-300 hover:bg-red-500/10"
        >
          <Trash2 className="w-4 h-4" />
        </Button>
      </div>
    </div>
  )
}
