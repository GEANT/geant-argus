from django.conf import settings

def geant_global(request):
    return {"theme": "geant_global"}

def geant_theme(request):
    """Set the argus theme in the render context"""
    return {"theme": settings.DEFAULT_THEME}
