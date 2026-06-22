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
    except Exception as e:
        print(f"Error loading home: {e}")
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
    try:
        profile = Profile.objects.first()
        projects = Project.objects.all()
    except Exception as e:
        print(f"Error loading projects: {e}")
        profile = None
        projects = []
    
    return render(request, 'portfolio/projects.html', {
        'projects': projects,
        'profile': profile
    })

def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    try:
        profile = project.profile
    except:
        profile = None
    
    return render(request, 'portfolio/project_detail.html', {
        'project': project,
        'profile': profile
    })

def contact(request):
    profile = None
    try:
        profile = Profile.objects.first()
    except:
        pass
    
    if request.method == 'POST':
        try:
            name = request.POST.get('name', '').strip()
            email = request.POST.get('email', '').strip()
            message = request.POST.get('message', '').strip()
            
            # Validation
            if not all([name, email, message]):
                return JsonResponse({'success': False, 'error': 'All fields are required'})
            
            if '@' not in email:
                return JsonResponse({'success': False, 'error': 'Invalid email address'})
            
            # Send email
            subject = f'Portfolio Contact: {name}'
            body = f'Name: {name}\nEmail: {email}\n\nMessage:\n{message}'
            
            send_mail(
                subject,
                body,
                settings.DEFAULT_FROM_EMAIL,
                [settings.DEFAULT_FROM_EMAIL],
                fail_silently=False,
            )
            return JsonResponse({'success': True, 'message': 'Message sent successfully!'})
        except Exception as e:
            print(f"Error sending email: {e}")
            return JsonResponse({'success': False, 'error': f'Error: {str(e)}'})
    
    return render(request, 'portfolio/contact.html', {'profile': profile})

def jokes(request):
    """Random Joke Generator Page using external APIs"""
    try:
        profile = Profile.objects.first()
    except:
        profile = None
    
    return render(request, 'portfolio/jokes.html', {'profile': profile})
