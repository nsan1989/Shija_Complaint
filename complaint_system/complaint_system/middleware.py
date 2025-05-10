from django.conf import settings
from django.shortcuts import redirect
from django.urls import resolve

class RequireLoginMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        exempt_view_names = [
            'login',
            'home',
            'register',
            'admin:login',
        ]

        match = resolve(request.path)
        if not request.user.is_authenticated and match.view_name not in exempt_view_names:
            return redirect(f'{settings.LOGIN_URL}?next={request.path}')
        
        return self.get_response(request)
    