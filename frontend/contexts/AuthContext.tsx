'use client'

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import apiClient from '@/lib/api-client'

interface User {
  user_id: string
  email: string
  created_at: string
}

interface AuthContextType {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  signup: (email: string, password: string) => Promise<void>
  signin: (email: string, password: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('auth_token')
    if (token) {
      apiClient.get('/auth/me')
        .then(res => setUser(res.data))
        .catch(() => localStorage.removeItem('auth_token'))
        .finally(() => setIsLoading(false))
    } else {
      setIsLoading(false)
    }
  }, [])

  const signup = async (email: string, password: string) => {
    try {
      const response = await apiClient.post('/auth/signup', { email, password })
      const { token, user: userData } = response.data
      localStorage.setItem('auth_token', token)
      setUser(userData)
    } catch (err) {
      console.error('Signup failed:', err)
      throw new Error('Signup failed. Check email/password.')
    }
  }

  const signin = async (email: string, password: string) => {
    try {
      const response = await apiClient.post('/auth/signin', { email, password })
      const { token, user: userData } = response.data
      localStorage.setItem('auth_token', token)
      setUser(userData)
    } catch (err) {
      console.error('Signin failed:', err)
      throw new Error('Signin failed. Check email/password.')
    }
  }

  const logout = () => {
    localStorage.removeItem('auth_token')
    setUser(null)
  }

  return (
    <AuthContext.Provider
      value={{ user, isAuthenticated: !!user, isLoading, signup, signin, logout }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth must be used within AuthProvider')
  return context
}
