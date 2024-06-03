from django.contrib import admin
from .models import ProfessionalRole, JobVacancy


@admin.register(ProfessionalRole)
class ProfessionalRoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'keywords')
    search_fields = ('name',)


@admin.register(JobVacancy)
class JobVacancyAdmin(admin.ModelAdmin):
    list_display = ('title', 'professional_role')
    search_fields = ('title', 'description')
