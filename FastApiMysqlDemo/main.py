from fastapi import FastAPI
from course.course_curd import course_router
import auth

app = FastAPI()
app.include_router(course_router)
app.include_router(auth.login_router)
