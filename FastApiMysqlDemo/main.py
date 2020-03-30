from fastapi import FastAPI
from course.course_curd import course_router

app = FastAPI()
app.include_router(course_router)
