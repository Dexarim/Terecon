from django.urls import path
from .views import upload_resume, resume_list, resume_detail

urlpatterns = [
    path('upload/', upload_resume, name='upload_resume'),
    path('', resume_list, name='resume_list'),  # Удалите пробел перед ''
    path('resumes/<int:resume_id>/', resume_detail, name='resume_detail'),
]