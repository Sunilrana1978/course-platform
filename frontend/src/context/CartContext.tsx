import { createContext, useContext, useState, useCallback, ReactNode } from 'react'
import * as cartApi from '../api/cart'
import type { Cart } from '../api/cart'
import { useAuth } from './AuthContext'

interface CartState {
  cart: Cart
  loading: boolean
  fetchCart: () => Promise<void>
  addItem: (item_type: 'course' | 'plan', id: number) => Promise<void>
  removeItem: (cartItemId: number) => Promise<void>
  clearCart: () => Promise<void>
}

const empty: Cart = { items: [], total: '0.00' }

const CartContext = createContext<CartState | null>(null)

export function CartProvider({ children }: { children: ReactNode }) {
  const { isAuthenticated } = useAuth()
  const [cart, setCart] = useState<Cart>(empty)
  const [loading, setLoading] = useState(false)

  const fetchCart = useCallback(async () => {
    if (!isAuthenticated) { setCart(empty); return }
    setLoading(true)
    try {
      setCart(await cartApi.getCart())
    } finally {
      setLoading(false)
    }
  }, [isAuthenticated])

  const addItem = async (item_type: 'course' | 'plan', id: number) => {
    await cartApi.addToCart(item_type === 'course' ? { item_type, course: id } : { item_type, plan: id })
    await fetchCart()
  }

  const removeItem = async (cartItemId: number) => {
    await cartApi.removeFromCart(cartItemId)
    await fetchCart()
  }

  const clearCart = async () => {
    await cartApi.clearCart()
    setCart(empty)
  }

  return (
    <CartContext.Provider value={{ cart, loading, fetchCart, addItem, removeItem, clearCart }}>
      {children}
    </CartContext.Provider>
  )
}

export function useCart() {
  const ctx = useContext(CartContext)
  if (!ctx) throw new Error('useCart must be inside CartProvider')
  return ctx
}
