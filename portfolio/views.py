from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Profile, Project, Skill, Experience
from django.core.mail import send_mail
from django.conf import settings

def home(request):
    try:
        profile = Profile.objects.first()
        skills = Skill.objects.filter(profile=profile)
        projects = Project.objects.filter(profile=profile, featured=True)[:6]
        experiences = Experience.objects.filter(profile=profile).order_by('-start_date')
    except:
        profile = None
        skills = []
        projects = []
        experiences = []
    
    context = {
        'profile': profile,
        'skills': skills,
        'featured_projects': projects,
        'experiences': experiences,
    }
    return render(request, 'portfolio/home.html', context)

def project_list(request):
    projects = Project.objects.all()
    return render(request, 'portfolio/projects.html', {'projects': projects})

def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    return render(request, 'portfolio/project_detail.html', {'project': project})

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        
        # Send email
        send_mail(
            f'Contact from {name}',
            message,
            email,
            [settings.DEFAULT_FROM_EMAIL],
            fail_silently=False,
        )
        return JsonResponse({'success': True})
    
    return render(request, 'portfolio/contact.html')