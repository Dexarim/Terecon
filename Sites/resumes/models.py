from django.db import models

class Resume(models.Model):
    name = models.CharField(max_length=255)
    desired_position = models.CharField(max_length=255)
    experience = models.IntegerField()
    score = models.IntegerField()
    ai_evaluation = models.CharField(max_length=50)

    def __str__(self):
        return self.name