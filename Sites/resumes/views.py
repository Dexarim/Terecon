from django.shortcuts import render, redirect
from .forms import ResumeUploadForm, JobDescriptionForm
from .models import Resume
from .utils import main
import os

def upload_resume(request):
    if request.method == 'POST':
        form = ResumeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            pdf_file = request.FILES['pdf_file']
            pdf_path = os.path.join('data/pdf/', pdf_file.name)
            with open(pdf_path, 'wb+') as destination:
                for chunk in pdf_file.chunks():
                    destination.write(chunk)

            # Запустите вашу функцию обработки
            csv_path = 'data/csv/output.csv'
            job_description = request.POST.get('job_description')
            desired_positions = request.POST.get('desired_positions').split(',')
            required_skills = request.POST.get('required_skills').split(',')
            main(pdf_path, csv_path, job_description, desired_positions, required_skills)

            return redirect('resume_list')  # Перенаправление на список резюме
    else:
        form = ResumeUploadForm()
    return render(request, 'upload.html', {'form': form})

def resume_list(request):
    resumes = Resume.objects.all()
    return render(request, 'resume_list.html', {'resumes': resumes})

def resume_detail(request, resume_id):
    resume = Resume.objects.get(id=resume_id)
    return render(request, 'resume_detail.html', {'resume': resume})