import { useEffect, useState } from 'react'
import { useSearchParams, Link } from 'react-router-dom'
import { getCourses } from '../../api/courses'
import type { Course } from '../../api/courses'
import { getMySubscription } from '../../api/subscriptions'
import type { UserSubscription } from '../../api/subscriptions'
import { useAuth } from '../../context/AuthContext'

export default function DashboardPage() {
  const { user } = useAuth()
  const [courses, setCourses] = useState<Course[]>([])
  const [subscription, setSubscription] = useState<UserSubscription | null>(null)
  const [loading, setLoading] = useState(true)
  const [searchParams] = useSearchParams()
  const paymentSuccess = searchParams.get('payment') === 'success'

  useEffect(() => {
    Promise.all([getCourses(), getMySubscription()])
      .then(([allCourses, subData]) => {
        setCourses(allCourses.filter((c) => c.has_access))
        setSubscription(subData.subscription)
      })
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="page"><p className="loading">Loading your dashboard…</p></div>

  return (
    <div className="page">
      {paymentSuccess && (
        <div className="alert alert-success">
          Payment successful! Your courses are now available below.
        </div>
      )}
      <h1>Welcome back, {user?.first_name || user?.email}</h1>

      {subscription && (
        <div className="subscription-banner">
          <div>
            <strong>{subscription.plan_detail.name} Subscription</strong>
            <span> — {subscription.days_remaining} days remaining</span>
          </div>
          <span className="badge badge-success">Active</span>
        </div>
      )}

      <h2>My Courses {courses.length > 0 && `(${courses.length})`}</h2>
      {courses.length === 0 ? (
        <div className="empty-dashboard">
          <p>You haven't enrolled in any courses yet.</p>
          <Link to="/" className="btn-primary">Browse Courses</Link>
        </div>
      ) : (
        <div className="course-grid">
          {courses.map((course) => (
            <div key={course.id} className="course-card">
              <Link to={`/courses/${course.id}`}>
                <img src={course.thumbnail_url} alt={course.title} className="course-thumb" />
              </Link>
              <div className="course-card-body">
                <span className="badge">{course.category_display}</span>
                <Link to={`/courses/${course.id}`}>
                  <h3 className="course-title">{course.title}</h3>
                </Link>
                <p className="course-instructor">{course.instructor}</p>
                <span className="badge badge-success">Enrolled</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
