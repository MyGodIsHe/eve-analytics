from django.conf import settings
from django.http import Http404
from django.shortcuts import render

class AccessMiddleware(object):

    def process_request(self, request):
        if request.path == '/'\
            or request.path.startswith(settings.MEDIA_URL)\
            or request.path.startswith(settings.STATIC_URL):
            return
        if request.user.is_anonymous():
            return render(request, '401.html')
        if request.path.startswith('/admin/') and not request.user.is_staff:
            raise Http404