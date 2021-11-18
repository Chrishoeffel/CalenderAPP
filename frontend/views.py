import requests
from django.shortcuts import render
from django.views import View
# Create your views here.
# def index(request):
#     return render(request, 'frontend/index.html')


class IndexView(View):
    
    def get(self, request):
        return render(request, 'frontend/index.html') #this file is placed in templates of project dir 

def index(request):
    r = requests.get('http://httpbin.org/status/418')
    print(r.text)
    return HttpResponse('<pre>' + r.text + '</pre>') 