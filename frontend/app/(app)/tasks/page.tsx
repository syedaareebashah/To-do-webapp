'use client'

import { useState } from 'react'
import ProtectedRoute from '@/components/ProtectedRoute'
import { useAuth } from '@/contexts/AuthContext'
import { CreateTaskForm } from '@/components/tasks/CreateTaskForm'
import { TaskList } from '@/components/tasks/TaskList'
import ChatInterface from '@/components/chat/ChatInterface'

export default function TasksPage() {
  const { user, logout } = useAuth()
  const [refreshTrigger, setRefreshTrigger] = useState(0)
  const [showChat, setShowChat] = useState(false)

  const handleTaskUpdate = () => {
    // Trigger task list refresh
    setRefreshTrigger(prev => prev + 1)
  }

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50">
        <nav className="bg-white shadow">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex items-center">
                <h1 className="text-xl font-bold">Todo App</h1>
              </div>
              <div className="flex items-center space-x-4">
                <button
                  onClick={() => setShowChat(!showChat)}
                  className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 flex items-center space-x-2"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                  </svg>
                  <span>{showChat ? 'Hide' : 'Show'} AI Chat</span>
                </button>
                <span className="text-gray-700">{user?.email}</span>
                <button
                  onClick={logout}
                  className="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                >
                  Logout
                </button>
              </div>
            </div>
          </div>
        </nav>

        <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <div className="px-4 py-6 sm:px-0">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Tasks Section */}
              <div className={`${showChat ? 'lg:col-span-2' : 'lg:col-span-3'}`}>
                <CreateTaskForm onTaskCreated={handleTaskUpdate} />
                <TaskList key={refreshTrigger} />
              </div>

              {/* Chat Section */}
              {showChat && (
                <div className="lg:col-span-1">
                  <div className="sticky top-6">
                    <ChatInterface onTaskUpdate={handleTaskUpdate} />
                  </div>
                </div>
              )}
            </div>
          </div>
        </main>
      </div>
    </ProtectedRoute>
  )
}
