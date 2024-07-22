from django.shortcuts import render

def modal_view(request):
    return render(request, 'htmx/incidents/modal.html')
