import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getCourse } from '../../api/courses'
import type { Course } from '../../api/courses'
import { useCart } from '../../context/CartContext'
import { useAuth } from '../../context/AuthContext'

export default function CourseDetailPage() {
  const { id } = useParams<{ id: string }>()
  const [course, setCourse] = useState<Course | null>(null)
  const [loading, setLoading] = useState(true)
  const [adding, setAdding] = useState(false)
  const [added, setAdded] = useState(false)
  const { addItem, fetchCart } = useCart()
  const { isAuthenticated } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    if (!id) return
    getCourse(Number(id)).then(setCourse).finally(() => setLoading(false))
  }, [id])

  const handleAdd = async () => {
    if (!isAuthenticated) { navigate('/login'); return }
    setAdding(true)
    try {
      await addItem('course', Number(id))
      await fetchCart()
      setAdded(true)
    } finally {
      setAdding(false)
    }
  }

  if (loading) return <div className="page"><p className="loading">Loading…</p></div>
  if (!course) return <div className="page"><p>Course not found.</p></div>

  return (
    <div className="page course-detail">
      <div className="course-detail-hero">
        <img src={course.thumbnail_url} alt={course.title} className="course-detail-img" />
        <div className="course-detail-info">
          <span className="badge">{course.category_display}</span>
          <h1>{course.title}</h1>
          <p className="course-instructor">By {course.instructor}</p>
          <p className="course-meta">{course.duration_hours} hours of content</p>
          <div className="course-detail-price-row">
            <span className="course-price-lg">${course.price}</span>
            {course.has_access ? (
              <span className="badge badge-success badge-lg">You're enrolled</span>
            ) : added ? (
              <button className="btn-primary" onClick={() => navigate('/cart')}>View Cart</button>
            ) : (
              <button className="btn-primary" onClick={handleAdd} disabled={adding}>
                {adding ? 'Adding…' : 'Add to Cart'}
              </button>
            )}
          </div>
        </div>
      </div>
      <div className="course-detail-body">
        <h2>About this course</h2>
        <p>{course.description}</p>
      </div>
    </div>
  )
}
