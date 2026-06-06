import client from './client'

export interface PaymentResponse {
  status: 'pending' | 'processing' | 'completed' | 'failed'
  payment: {
    id: string
    amount: string
    currency: string
    status: string
    error_detail: string
    created_at: string
  }
}

export interface CartItemPayload {
  item_type: 'course' | 'plan'
  course_id?: number
  plan_id?: number
  price: string
}

export const initiatePayment = (idempotency_key: string, cart_items: CartItemPayload[]) =>
  client.post<PaymentResponse>('/payments/initiate/', { idempotency_key, cart_items }).then((r) => r.data)

export const confirmPayment = (data: {
  payment_id: string
  card_number: string
  card_expiry: string
  card_cvc: string
  card_name: string
}) => client.post<PaymentResponse>('/payments/confirm/', data).then((r) => r.data)

export const getPaymentStatus = (paymentId: string) =>
  client.get<PaymentResponse>(`/payments/${paymentId}/status/`).then((r) => r.data)
