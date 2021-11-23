from django.shortcuts import render


# Create your views here.
def index_template(request):
    return render(request, 'live_app.html')
