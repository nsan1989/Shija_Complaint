from django.shortcuts import render

# home view.
def Home(request):
    return render(request, 'home.html')
