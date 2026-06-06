import { Link } from 'react-router-dom'
import type { Course } from '../api/courses'

interface Props {
  course: Course
  onAddToCart?: () => void
  cartLoading?: boolean
}

export default function CourseCard({ course, onAddToCart, cartLoading }: Props) {
  return (
    <div className="course-card">
      <Link to={`/courses/${course.id}`}>
        <img
          src={course.thumbnail_url || `https://picsum.photos/seed/${course.id}/400/225`}
          alt={course.title}
          className="course-thumb"
        />
      </Link>
      <div className="course-card-body">
        <span className="badge">{course.category_display}</span>
        <Link to={`/courses/${course.id}`}>
          <h3 className="course-title">{course.title}</h3>
        </Link>
        <p className="course-instructor">{course.instructor}</p>
        <p className="course-meta">{course.duration_hours}h</p>
        <div className="course-card-footer">
          <span className="course-price">${course.price}</span>
          {course.has_access ? (
            <span className="badge badge-success">Enrolled</span>
          ) : (
            onAddToCart && (
              <button className="btn-primary btn-sm" onClick={onAddToCart} disabled={cartLoading}>
                Add to Cart
              </button>
            )
          )}
        </div>
      </div>
    </div>
  )
}
