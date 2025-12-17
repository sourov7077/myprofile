# portfolio/models.py - COMPLETE NEW FILE

from django.db import models
from django.contrib.auth.models import User
import base64

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, default="Full Stack Developer")
    bio = models.TextField(default="Passionate developer creating amazing web experiences")
    email = models.EmailField(default="example@email.com")
    phone = models.CharField(max_length=20, default="+880 1234 567890")
    location = models.CharField(max_length=100, default="Dhaka, Bangladesh")
    
    # Base64 image fields
    profile_image_base64 = models.TextField(blank=True, null=True)
    profile_image_format = models.CharField(max_length=10, blank=True, null=True)
    
    # Social Links
    github = models.URLField(blank=True, default="https://github.com")
    linkedin = models.URLField(blank=True, default="https://linkedin.com")
    twitter = models.URLField(blank=True, default="https://twitter.com")
    facebook = models.URLField(blank=True, default="https://facebook.com")
    
    def __str__(self):
        return self.user.username
    
    @property
    def profile_image_url(self):
        if self.profile_image_base64 and self.profile_image_format:
            return f"data:image/{self.profile_image_format};base64,{self.profile_image_base64}"
        return None
    
    def set_profile_image(self, image_file):
        try:
            image_data = image_file.read()
            base64_str = base64.b64encode(image_data).decode('utf-8')
            
            filename = image_file.name.lower()
            if filename.endswith('.png'):
                format_str = 'png'
            elif filename.endswith('.jpg') or filename.endswith('.jpeg'):
                format_str = 'jpeg'
            elif filename.endswith('.gif'):
                format_str = 'gif'
            elif filename.endswith('.webp'):
                format_str = 'webp'
            else:
                format_str = 'jpeg'
            
            self.profile_image_base64 = base64_str
            self.profile_image_format = format_str
            self.save()
            return True
        except:
            return False
    
    def clear_profile_image(self):
        self.profile_image_base64 = None
        self.profile_image_format = None
        self.save()

class Project(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=200, default="Awesome Project")
    description = models.TextField(default="Project description goes here...")
    
    # Base64 image fields for project
    image_base64 = models.TextField(blank=True, null=True)
    image_format = models.CharField(max_length=10, blank=True, null=True)
    
    technologies = models.CharField(max_length=200, default="Django, React, PostgreSQL")
    github_link = models.URLField(blank=True, default="https://github.com")
    live_link = models.URLField(blank=True, default="https://example.com")
    featured = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
    @property
    def image_url(self):
        if self.image_base64 and self.image_format:
            return f"data:image/{self.image_format};base64,{self.image_base64}"
        return None
    
    def set_image(self, image_file):
        try:
            image_data = image_file.read()
            base64_str = base64.b64encode(image_data).decode('utf-8')
            
            filename = image_file.name.lower()
            if filename.endswith('.png'):
                format_str = 'png'
            elif filename.endswith('.jpg') or filename.endswith('.jpeg'):
                format_str = 'jpeg'
            elif filename.endswith('.gif'):
                format_str = 'gif'
            elif filename.endswith('.webp'):
                format_str = 'webp'
            else:
                format_str = 'jpeg'
            
            self.image_base64 = base64_str
            self.image_format = format_str
            self.save()
            return True
        except:
            return False
    
    def clear_image(self):
        self.image_base64 = None
        self.image_format = None
        self.save()

class Skill(models.Model):
    CATEGORY_CHOICES = [
        ('frontend', 'Frontend'),
        ('backend', 'Backend'),
        ('database', 'Database'),
        ('devops', 'DevOps'),
        ('design', 'Design'),
    ]
    
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='skills')
    name = models.CharField(max_length=50, default="Python")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='backend')
    percentage = models.IntegerField(default=85)
    color = models.CharField(max_length=20, default='#3498db')
    
    def __str__(self):
        return self.name

class Experience(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='experiences')
    company = models.CharField(max_length=100, default="Tech Company")
    position = models.CharField(max_length=100, default="Software Developer")
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    current = models.BooleanField(default=False)
    description = models.TextField(default="Worked on various projects...")
    
    def __str__(self):
        return f"{self.position} at {self.company}"