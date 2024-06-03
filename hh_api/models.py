from django.db import models


class ProfessionalRole(models.Model):
    name = models.CharField(max_length=100, unique=True)
    keywords = models.TextField(help_text="Comma-separated list of keywords")

    def __str__(self):
        return self.name

    def get_keywords(self):
        return [keyword.strip().lower() for keyword in self.keywords.split(',')]


class JobVacancy(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    professional_role = models.ForeignKey(ProfessionalRole, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

