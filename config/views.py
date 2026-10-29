from django.http import HttpResponse
from django.shortcuts import render

def principal(request):
    return render(request, 'principal.html')

def login(request):
    return render(request, 'log_ing.html')