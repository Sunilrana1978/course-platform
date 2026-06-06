import client from './client'

export interface Plan {
  id: number
  name: string
  price: string
  duration_days: number
  description: string
}

export interface UserSubscription {
  id: number
  plan: number
  plan_detail: Plan
  start_date: string
  end_date: string
  is_active: boolean
  days_remaining: number
}

export const getPlans = () => client.get<Plan[]>('/subscriptions/plans/').then((r) => r.data)

export const getMySubscription = () =>
  client.get<{ subscription: UserSubscription | null }>('/subscriptions/me/').then((r) => r.data)
