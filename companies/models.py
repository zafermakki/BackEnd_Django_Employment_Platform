from email.policy import default
from django.db import models
from django.conf import settings
from django.utils import timezone

class Company(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="companies"
        )
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True, null=True)
    industry = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    logo = models.ImageField(upload_to="company_logos/", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class JobAd(models.Model):
    JOB_TYPE_CHOICES = [
        ('job', 'Job'),
        ('internship', 'Internship'),
    ]

    company = models.ForeignKey(
        'Company',
        on_delete=models.CASCADE,
        related_name="job_ads"
    )

    title = models.CharField(max_length=255)
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES)  
    description = models.TextField()  
    location = models.CharField(max_length=255, blank=True, null=True) 
    salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  
    requirements = models.TextField(blank=True, null=True) 
    deadline = models.DateField(blank=True, null=True)   

    created_at = models.DateTimeField(auto_now_add=True)  
    updated_at = models.DateTimeField(auto_now=True)       

    def __str__(self):
        return f"{self.title} - {self.company.name}"


class JobApplication(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    job_ad = models.ForeignKey(
        'JobAd',
        on_delete=models.CASCADE,
        related_name="applications"
    )
    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="applications"
    )
    full_name = models.CharField(max_length=255)  
    email = models.EmailField()  
    cv = models.FileField(upload_to="cvs/")  
    cover_letter = models.TextField(blank=True, null=True)  
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    applied_at = models.DateTimeField(auto_now_add=True)  

    def __str__(self):
        return f"Application by {self.full_name} for {self.job_ad.title}"

class Message(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="messages"
    )
    job_application = models.ForeignKey(
        JobApplication,
        on_delete=models.CASCADE,
        related_name="messages"
    )
    subject = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message to {self.user.username} - {self.subject}"

class WorkSession(models.Model):
    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="work_sessions"
    )
    company = models.ForeignKey(
        "Company",
        on_delete=models.CASCADE,
        related_name="work_sessions"
    )
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(blank=True, null=True)

    def duration(self):
        if self.end_time:
            return self.end_time - self.start_time
        return timezone.now() - self.start_time

    def __str__(self):
        return f"{self.employee.username} @ {self.company.name}"