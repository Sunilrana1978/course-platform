import { useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useCart } from '../../context/CartContext'

export default function CartPage() {
  const { cart, loading, fetchCart, removeItem } = useCart()
  const navigate = useNavigate()

  useEffect(() => { fetchCart() }, [])

  if (loading) return <div className="page"><p className="loading">Loading cart…</p></div>

  return (
    <div className="page">
      <h1>Your Cart</h1>
      {cart.items.length === 0 ? (
        <div className="empty-cart">
          <p>Your cart is empty.</p>
          <Link to="/" className="btn-primary">Browse Courses</Link>
        </div>
      ) : (
        <>
          <div className="cart-items">
            {cart.items.map((item) => (
              <div key={item.id} className="cart-item">
                <div className="cart-item-info">
                  {item.item_type === 'course' && item.course_detail && (
                    <>
                      <img src={item.course_detail.thumbnail_url} alt={item.course_detail.title} className="cart-item-thumb" />
                      <div>
                        <p className="cart-item-title">{item.course_detail.title}</p>
                        <span className="badge">{item.course_detail.category_display}</span>
                      </div>
                    </>
                  )}
                  {item.item_type === 'plan' && item.plan_detail && (
                    <div>
                      <p className="cart-item-title">{item.plan_detail.name} Subscription</p>
                      <p className="cart-item-sub">{item.plan_detail.description}</p>
                    </div>
                  )}
                </div>
                <div className="cart-item-right">
                  <span className="cart-item-price">${item.price}</span>
                  <button className="btn-ghost btn-sm" onClick={() => removeItem(item.id)}>Remove</button>
                </div>
              </div>
            ))}
          </div>
          <div className="cart-summary">
            <div className="cart-total">
              <span>Total</span>
              <span className="total-amount">${cart.total}</span>
            </div>
            <button className="btn-primary btn-full" onClick={() => navigate('/checkout')}>
              Proceed to Checkout
            </button>
          </div>
        </>
      )}
    </div>
  )
}
