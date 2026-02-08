'use client'

import React, { useState } from 'react'
import { useTasks } from '@/hooks/useTasks'
import { Button } from '../ui/Button'
import { Input, Textarea } from '../ui/Input'

interface CreateTaskFormProps {
  onTaskCreated?: () => void
}

export function CreateTaskForm({ onTaskCreated }: CreateTaskFormProps) {
  const { createTask } = useTasks()
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [priority, setPriority] = useState<'low' | 'medium' | 'high'>('medium')
  const [dueDate, setDueDate] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const titleCharsLeft = 255 - title.length
  const descriptionCharsLeft = 1000 - description.length

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!title.trim()) {
      setError('Title is required')
      return
    }

    if (title.length > 255) {
      setError('Title must be 255 characters or less')
      return
    }

    if (description.length > 1000) {
      setError('Description must be 1000 characters or less')
      return
    }

    setLoading(true)
    setError('')

    try {
      await createTask({
        title: title.trim(),
        description: description.trim() || undefined,
        priority,
        due_date: dueDate || undefined
      })

      // Clear form on success
      setTitle('')
      setDescription('')
      setPriority('medium')
      setDueDate('')

      // Trigger callback if provided
      if (onTaskCreated) {
        onTaskCreated()
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create task')
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="bg-white p-6 rounded-lg shadow-md mb-6">
      <h2 className="text-xl font-semibold mb-4">Create New Task</h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 space-y-4">
        <div className="space-y-4">
          <Input
            label="Title"
            required
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Enter task title"
            maxLength={255}
            helperText={`${titleCharsLeft} characters remaining`}
          />

          <Textarea
            label="Description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Enter task description (optional)"
            rows={3}
            maxLength={1000}
            helperText={`${descriptionCharsLeft} characters remaining`}
          />
        </div>

        <div className="space-y-4">
          <div>
            <label htmlFor="priority" className="block text-sm font-medium text-gray-700 mb-1">
              Priority
            </label>
            <select
              id="priority"
              value={priority}
              onChange={(e) => setPriority(e.target.value as 'low' | 'medium' | 'high')}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>
          </div>

          <div>
            <label htmlFor="dueDate" className="block text-sm font-medium text-gray-700 mb-1">
              Due Date (Optional)
            </label>
            <input
              type="date"
              id="dueDate"
              value={dueDate}
              onChange={(e) => setDueDate(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        </div>
      </div>

      {error && (
        <p className="text-sm text-red-600 mt-2">{error}</p>
      )}

      <Button type="submit" loading={loading} disabled={!title.trim()} className="mt-4">
        Create Task
      </Button>
    </form>
  )
}
