from django import forms

class ResumeUploadForm(forms.Form):
    pdf_file = forms.FileField()

class JobDescriptionForm(forms.Form):
    job_description = forms.CharField(widget=forms.Textarea)
    desired_positions = forms.CharField()
    required_skills = forms.CharField()