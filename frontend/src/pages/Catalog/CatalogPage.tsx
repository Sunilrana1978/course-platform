import { useEffect, useState } from 'react'
import { getCourses } from '../../api/courses'
import type { Course } from '../../api/courses'
import CourseCard from '../../components/CourseCard'
import { useCart } from '../../context/CartContext'
import { useAuth } from '../../context/AuthContext'
import { useNavigate } from 'react-router-dom'

const CATEGORIES = [
  { value: '', label: 'All' },
  { value: 'web', label: 'Web Dev' },
  { value: 'data', label: 'Data Science' },
  { value: 'devops', label: 'DevOps' },
]

export default function CatalogPage() {
  const [courses, setCourses] = useState<Course[]>([])
  const [category, setCategory] = useState('')
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const { addItem, fetchCart } = useCart()
  const { isAuthenticated } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    setLoading(true)
    getCourses({ category: category || undefined, search: search || undefined })
      .then(setCourses)
      .finally(() => setLoading(false))
  }, [category, search])

  const handleAddToCart = async (course: Course) => {
    if (!isAuthenticated) { navigate('/login'); return }
    await addItem('course', course.id)
    await fetchCart()
  }

  return (
    <div className="page">
      <div className="catalog-header">
        <h1>All Courses</h1>
        <div className="catalog-filters">
          <input
            className="search-input"
            placeholder="Search courses…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <div className="category-tabs">
            {CATEGORIES.map((c) => (
              <button
                key={c.value}
                className={`tab ${category === c.value ? 'tab-active' : ''}`}
                onClick={() => setCategory(c.value)}
              >
                {c.label}
              </button>
            ))}
          </div>
        </div>
      </div>
      {loading ? (
        <p className="loading">Loading…</p>
      ) : courses.length === 0 ? (
        <p className="empty">No courses found.</p>
      ) : (
        <div className="course-grid">
          {courses.map((course) => (
            <CourseCard
              key={course.id}
              course={course}
              onAddToCart={() => handleAddToCart(course)}
            />
          ))}
        </div>
      )}
    </div>
  )
}
