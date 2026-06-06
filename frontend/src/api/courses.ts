import client from './client'

export interface Course {
  id: number
  title: string
  description: string
  price: string
  category: string
  category_display: string
  thumbnail_url: string
  duration_hours: number
  instructor: string
  has_access: boolean
}

export const getCourses = (params?: { category?: string; search?: string }) =>
  client.get<Course[]>('/courses/', { params }).then((r) => r.data)

export const getCourse = (id: number) =>
  client.get<Course>(`/courses/${id}/`).then((r) => r.data)

export const getCourseAccess = (id: number) =>
  client.get<{ has_access: boolean; reason?: string; plan?: string }>(`/courses/${id}/access/`).then((r) => r.data)
