import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useCart } from '../context/CartContext'

export default function Navbar() {
  const { user, isAuthenticated, logout } = useAuth()
  const { cart } = useCart()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  return (
    <nav className="navbar">
      <Link to="/" className="navbar-brand">LearnHub</Link>
      <div className="navbar-links">
        <Link to="/">Courses</Link>
        <Link to="/subscriptions">Pricing</Link>
        {isAuthenticated ? (
          <>
            <Link to="/cart" className="cart-link">
              Cart {cart.items.length > 0 && <span className="cart-badge">{cart.items.length}</span>}
            </Link>
            <Link to="/dashboard">My Learning</Link>
            <span className="navbar-user">{user?.first_name || user?.email}</span>
            <button className="btn-outline" onClick={handleLogout}>Log out</button>
          </>
        ) : (
          <>
            <Link to="/login">Log in</Link>
            <Link to="/register" className="btn-primary">Sign up</Link>
          </>
        )}
      </div>
    </nav>
  )
}
