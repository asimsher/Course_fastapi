from course_app.db.models import UserProfile, Category, Course
from sqladmin import ModelView


class UserProfileAdmin( ModelView, model=UserProfile ):
    column_list = [UserProfile.id, UserProfile.username, UserProfile.role]


class CategoryAdmin( ModelView, model=Category ):
    column_list = [Category.id, Category.category_name]


class CoursesAdmin( ModelView, model=Course ):
    column_list = [Course.course_name, Course.price]
