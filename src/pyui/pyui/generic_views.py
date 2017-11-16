from django.http import HttpResponse
from django.shortcuts import render


def dummy(_):
    return HttpResponse(status=204)


def about(request):
    return render(request, 'about.html')


def contact(request):
    return render(request, 'contact.html')
