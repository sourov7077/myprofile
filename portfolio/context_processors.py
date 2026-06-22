from .models import Profile

def project_context(request):
    """
    Context processor to make profile data available to all templates
    """
    try:
        profile = Profile.objects.first()
    except:
        profile = None
    
    return {
        'profile': profile
    }
