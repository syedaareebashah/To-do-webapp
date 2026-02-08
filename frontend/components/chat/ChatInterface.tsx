'use client'

import React, { useState, useRef, useEffect } from 'react'
import axios from 'axios'
import { useAuth } from '@/contexts/AuthContext'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  tool_calls?: any[]
}

interface ChatInterfaceProps {
  onTaskUpdate?: () => void
}

export default function ChatInterface({ onTaskUpdate }: ChatInterfaceProps) {
  const { user } = useAuth()
  const [messages, setMessages] = useState<Message[]>([])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [conversationId, setConversationId] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const sendMessage = async () => {
    if (!inputMessage.trim() || !user) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputMessage,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInputMessage('')
    setIsLoading(true)

    try {
      // Use direct axios call to the chatbot API on port 8001
      // The backend expects a MessageCreate object which requires 'content', 'role', and 'conversation_id'
      // Even though the backend will override the conversation_id, it still needs to be in the request
      const requestBody = {
        content: inputMessage,
        role: 'user',
        conversation_id: conversationId || '00000000-0000-0000-0000-000000000000'  // Default UUID if none exists
      };

      // Construct the URL with the conversation_id as a query parameter if it exists
      // Actually, based on the backend signature, the conversation_id in the path parameter 
      // is separate from the one in the MessageCreate object
      let url = `http://localhost:8001/api/${user.user_id}/chat`;
      
      const response = await axios.post(url, requestBody, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
          'Content-Type': 'application/json'
        }
      })

      // Log the response to debug
      console.log('Chat response:', response.data);

      // Check if the response has the expected structure
      if (!response.data || typeof response.data !== 'object') {
        throw new Error('Invalid response format from chat API');
      }

      const { response: assistantResponse, conversation_id, tool_calls } = response.data;

      // Store conversation ID for future messages
      if (conversation_id && !conversationId) {
        setConversationId(conversation_id);
      }

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: assistantResponse || 'No response from assistant',
        timestamp: new Date(),
        tool_calls: tool_calls || []
      };

      setMessages(prev => [...prev, assistantMessage]);

      // If tasks were modified, trigger refresh after a small delay to ensure DB operations complete
      if (tool_calls && tool_calls.length > 0 && onTaskUpdate) {
        // Check if any of the tool calls affect tasks (add, complete, delete)
        const hasTaskOperations = tool_calls.some((tool_call: any) => 
          ['add_task', 'complete_task', 'delete_task', 'update_task'].includes(tool_call.tool_name)
        );
        
        if (hasTaskOperations) {
          setTimeout(() => {
            onTaskUpdate();
          }, 800); // Increased delay to ensure DB operations complete
        }
      }
    } catch (error: any) {
      console.error('Error sending message:', error);
      
      // Extract error details more carefully
      let errorMessageText = 'An unknown error occurred';
      if (error.response) {
        // Server responded with error status
        if (error.response.data && typeof error.response.data === 'object') {
          errorMessageText = error.response.data.detail || error.response.data.message || JSON.stringify(error.response.data);
        } else {
          errorMessageText = error.response.data || error.response.statusText;
        }
      } else if (error.request) {
        // Request was made but no response received
        errorMessageText = 'Network error: Unable to connect to the chat service';
      } else {
        // Something else happened
        errorMessageText = error.message;
      }

      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `Sorry, I encountered an error: ${errorMessageText}`,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div className="flex flex-col h-full bg-white rounded-lg shadow-lg">
      {/* Chat Header */}
      <div className="px-4 py-3 border-b border-gray-200 bg-gradient-to-r from-blue-500 to-blue-600">
        <h2 className="text-lg font-semibold text-white">AI Task Assistant</h2>
        <p className="text-xs text-blue-100">Ask me to manage your tasks</p>
      </div>

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4" style={{ maxHeight: '500px' }}>
        {messages.length === 0 && (
          <div className="text-center text-gray-500 mt-8">
            <div className="mb-4">
              <svg className="w-16 h-16 mx-auto text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
              </svg>
            </div>
            <p className="text-sm">Start a conversation with your AI assistant</p>
            <p className="text-xs text-gray-400 mt-2">Try: "Add a task to buy groceries" or "Show my tasks"</p>
          </div>
        )}

        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] rounded-lg px-4 py-2 ${
                message.role === 'user'
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-100 text-gray-800'
              }`}
            >
              <p className="text-sm whitespace-pre-wrap">{message.content}</p>

              {/* Show tool calls if any */}
              {message.tool_calls && message.tool_calls.length > 0 && (
                <div className="mt-2 pt-2 border-t border-gray-300">
                  <p className="text-xs text-gray-600 font-semibold mb-1">Actions taken:</p>
                  {message.tool_calls.map((tool, idx) => (
                    <div key={idx} className="text-xs text-gray-600">
                      • {tool.tool_name}
                    </div>
                  ))}
                </div>
              )}

              <p className="text-xs mt-1 opacity-70">
                {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </p>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-lg px-4 py-2">
              <div className="flex space-x-2">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="px-4 py-3 border-t border-gray-200 bg-gray-50">
        <div className="flex space-x-2">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message..."
            disabled={isLoading}
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
          />
          <button
            onClick={sendMessage}
            disabled={isLoading || !inputMessage.trim()}
            className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
          >
            {isLoading ? (
              <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            ) : (
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            )}
          </button>
        </div>
      </div>
    </div>
  )
}
