import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { getPlans } from '../../api/subscriptions'
import type { Plan } from '../../api/subscriptions'
import { useCart } from '../../context/CartContext'
import { useAuth } from '../../context/AuthContext'

export default function PlansPage() {
  const [plans, setPlans] = useState<Plan[]>([])
  const [loading, setLoading] = useState(true)
  const [adding, setAdding] = useState<number | null>(null)
  const { addItem, fetchCart } = useCart()
  const { isAuthenticated } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    getPlans().then(setPlans).finally(() => setLoading(false))
  }, [])

  const handleSelect = async (plan: Plan) => {
    if (!isAuthenticated) { navigate('/login'); return }
    setAdding(plan.id)
    try {
      await addItem('plan', plan.id)
      await fetchCart()
      navigate('/cart')
    } finally {
      setAdding(null)
    }
  }

  if (loading) return <div className="page"><p className="loading">Loading plans…</p></div>

  return (
    <div className="page plans-page">
      <div className="plans-header">
        <h1>Simple, transparent pricing</h1>
        <p>Get unlimited access to all courses. Cancel anytime.</p>
      </div>
      <div className="plans-grid">
        {plans.map((plan, i) => (
          <div key={plan.id} className={`plan-card ${i === 1 ? 'plan-card-featured' : ''}`}>
            {i === 1 && <div className="plan-badge-top">Best value</div>}
            <h2 className="plan-name">{plan.name}</h2>
            <div className="plan-price">
              <span className="plan-amount">${plan.price}</span>
              <span className="plan-period">/{plan.duration_days === 30 ? 'month' : 'year'}</span>
            </div>
            <p className="plan-description">{plan.description}</p>
            <ul className="plan-features">
              <li>Unlimited course access</li>
              <li>All categories included</li>
              <li>New courses each month</li>
              {plan.duration_days === 365 && <li>2 months free vs monthly</li>}
            </ul>
            <button
              className={`btn-full ${i === 1 ? 'btn-primary' : 'btn-outline'}`}
              onClick={() => handleSelect(plan)}
              disabled={adding === plan.id}
            >
              {adding === plan.id ? 'Adding…' : `Get ${plan.name}`}
            </button>
          </div>
        ))}
      </div>
      <div className="plans-also">
        <p>Prefer to buy individual courses? <a href="/">Browse the catalog</a></p>
      </div>
    </div>
  )
}
