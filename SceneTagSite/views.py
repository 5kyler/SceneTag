from __future__ import unicode_literals

from django.shortcuts import render


# Create your views here.

def test(request):
    return render(request, 'SceneTagSite/test.html', {
    })
