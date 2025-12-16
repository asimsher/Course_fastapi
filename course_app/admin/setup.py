from fastapi import FastAPI
from sqladmin import Admin
from .views import UserProfileAdmin, CategoryAdmin, CoursesAdmin
from course_app.db.database import engine


def setup_admin(app: FastAPI):
    admin = Admin(app, engine)
    admin.add_view(UserProfileAdmin)
    admin.add_view(CategoryAdmin)
    admin.add_view(CoursesAdmin)