import { useEffect, useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { useCart } from '../../context/CartContext'
import { getCart } from '../../api/cart'
import type { Cart } from '../../api/cart'
import { initiatePayment, confirmPayment, getPaymentStatus } from '../../api/payments'
import type { CartItemPayload } from '../../api/payments'

function getOrCreateIdempotencyKey(): string {
  let key = sessionStorage.getItem('idempotency_key')
  if (!key) {
    key = crypto.randomUUID()
    sessionStorage.setItem('idempotency_key', key)
  }
  return key
}

function buildCartPayload(cart: Cart): CartItemPayload[] {
  return cart.items.map((item) => ({
    item_type: item.item_type,
    course_id: item.course ?? undefined,
    plan_id: item.plan ?? undefined,
    price: item.price,
  }))
}

export default function CheckoutPage() {
  const { cart, fetchCart, clearCart } = useCart()
  const navigate = useNavigate()

  const [paymentId, setPaymentId] = useState<string | null>(null)
  const [card, setCard] = useState({ number: '', expiry: '', cvc: '', name: '' })
  const [status, setStatus] = useState<'idle' | 'initiating' | 'ready' | 'paying' | 'polling' | 'done' | 'error'>('idle')
  const [errorMsg, setErrorMsg] = useState('')
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null)

  useEffect(() => {
    fetchCart().then(() => initiate())
    return () => { if (pollRef.current) clearInterval(pollRef.current) }
  }, [])

  const initiate = async () => {
    setStatus('initiating')
    const idempotencyKey = getOrCreateIdempotencyKey()
    try {
      const cartData = await getCart()
      if (cartData.items.length === 0) { navigate('/cart'); return }
      const payload = buildCartPayload(cartData)
      const res = await initiatePayment(idempotencyKey, payload)
      if (res.status === 'completed') {
        sessionStorage.removeItem('idempotency_key')
        navigate('/dashboard')
        return
      }
      setPaymentId(res.payment.id)
      setStatus('ready')
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail || 'Failed to initiate checkout.')
      setStatus('error')
    }
  }

  const handlePay = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!paymentId) return
    setStatus('paying')
    setErrorMsg('')
    try {
      const res = await confirmPayment({
        payment_id: paymentId,
        card_number: card.number.replace(/\s/g, ''),
        card_expiry: card.expiry,
        card_cvc: card.cvc,
        card_name: card.name,
      })
      if (res.status === 'completed') {
        sessionStorage.removeItem('idempotency_key')
        await clearCart()
        navigate('/dashboard?payment=success')
        return
      }
      if (res.status === 'processing') {
        setStatus('polling')
        startPolling(paymentId)
        return
      }
      // failed
      setErrorMsg(res.payment.error_detail || 'Payment failed. Please try again.')
      setStatus('ready')
    } catch (err: any) {
      if (err.response?.status === 202) {
        setStatus('polling')
        startPolling(paymentId)
        return
      }
      setErrorMsg(err.response?.data?.detail || 'Payment error.')
      setStatus('ready')
    }
  }

  const startPolling = (pid: string) => {
    pollRef.current = setInterval(async () => {
      try {
        const res = await getPaymentStatus(pid)
        if (res.status === 'completed') {
          clearInterval(pollRef.current!)
          sessionStorage.removeItem('idempotency_key')
          await clearCart()
          navigate('/dashboard?payment=success')
        } else if (res.status === 'failed') {
          clearInterval(pollRef.current!)
          setErrorMsg(res.payment.error_detail || 'Payment failed.')
          setStatus('ready')
        }
      } catch { /* keep polling */ }
    }, 2000)
  }

  const formatCardNumber = (v: string) =>
    v.replace(/\D/g, '').slice(0, 16).replace(/(.{4})/g, '$1 ').trim()

  const formatExpiry = (v: string) =>
    v.replace(/\D/g, '').slice(0, 4).replace(/^(\d{2})(\d)/, '$1/$2')

  if (status === 'initiating') return <div className="page"><p className="loading">Preparing checkout…</p></div>
  if (status === 'polling') return (
    <div className="page checkout-processing">
      <div className="spinner" />
      <h2>Processing payment…</h2>
      <p>Please wait. Do not close this tab.</p>
    </div>
  )
  if (status === 'done') return <div className="page"><p>Redirecting…</p></div>

  return (
    <div className="page checkout-page">
      <h1>Checkout</h1>
      <div className="checkout-layout">
        <div className="checkout-form-col">
          <h2>Payment details</h2>
          <p className="checkout-hint">Use any card number — this is a mock payment.</p>
          <form onSubmit={handlePay} className="payment-form">
            <label>
              Cardholder name
              <input
                placeholder="John Smith"
                required
                value={card.name}
                onChange={(e) => setCard({ ...card, name: e.target.value })}
              />
            </label>
            <label>
              Card number
              <input
                placeholder="4242 4242 4242 4242"
                required
                value={card.number}
                onChange={(e) => setCard({ ...card, number: formatCardNumber(e.target.value) })}
                inputMode="numeric"
              />
            </label>
            <div className="form-row">
              <label>
                Expiry (MM/YY)
                <input
                  placeholder="12/27"
                  required
                  value={card.expiry}
                  onChange={(e) => setCard({ ...card, expiry: formatExpiry(e.target.value) })}
                  inputMode="numeric"
                />
              </label>
              <label>
                CVC
                <input
                  placeholder="123"
                  required
                  maxLength={4}
                  value={card.cvc}
                  onChange={(e) => setCard({ ...card, cvc: e.target.value.replace(/\D/g, '').slice(0, 4) })}
                  inputMode="numeric"
                />
              </label>
            </div>
            {errorMsg && <p className="form-error">{errorMsg}</p>}
            <button type="submit" className="btn-primary btn-full" disabled={status === 'paying'}>
              {status === 'paying' ? 'Processing…' : `Pay $${cart.total}`}
            </button>
          </form>
        </div>
        <div className="checkout-summary-col">
          <h2>Order summary</h2>
          {cart.items.map((item) => (
            <div key={item.id} className="checkout-order-item">
              <span>
                {item.item_type === 'course'
                  ? item.course_detail?.title
                  : `${item.plan_detail?.name} Subscription`}
              </span>
              <span>${item.price}</span>
            </div>
          ))}
          <div className="checkout-order-total">
            <strong>Total</strong>
            <strong>${cart.total}</strong>
          </div>
        </div>
      </div>
    </div>
  )
}
