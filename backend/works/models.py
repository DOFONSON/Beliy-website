from django.db import models

class LiteraryWork(models.Model):
    title = models.CharField(max_length=255)
    year = models.IntegerField()
    description = models.TextField()
    genre = models.CharField(max_length=100)