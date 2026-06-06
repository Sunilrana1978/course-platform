import client from './client'
import axios from 'axios'

export interface User {
  id: number
  email: string
  username: string
  first_name: string
  last_name: string
}

export interface AuthTokens {
  access: string
  refresh: string
  user: User
}

export const register = (data: {
  email: string
  username: string
  password: string
  first_name?: string
  last_name?: string
}) => axios.post<AuthTokens>('/api/auth/register/', data).then((r) => r.data)

export const login = (email: string, password: string) =>
  axios.post<AuthTokens>('/api/auth/login/', { email, password }).then((r) => r.data)

export const getMe = () => client.get<User>('/auth/me/').then((r) => r.data)
