import client from './client'
import type { Course } from './courses'
import type { Plan } from './subscriptions'

export interface CartItem {
  id: number
  item_type: 'course' | 'plan'
  course: number | null
  plan: number | null
  course_detail: Course | null
  plan_detail: Plan | null
  price: string
  added_at: string
}

export interface Cart {
  items: CartItem[]
  total: string
}

export const getCart = () => client.get<Cart>('/cart/').then((r) => r.data)

export const addToCart = (data: { item_type: 'course' | 'plan'; course?: number; plan?: number }) =>
  client.post<CartItem>('/cart/items/', data).then((r) => r.data)

export const removeFromCart = (id: number) => client.delete(`/cart/items/${id}/`)

export const clearCart = () => client.post('/cart/clear/')
