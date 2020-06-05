"""smierg URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from django.conf.urls import re_path

from explorer import views
import SMIerg2020 as smi

SYMBOLS = smi.SYMBOLS
INTERVALS = smi.INTERVALS

def mkChoiceRegex (L):
    s = ""
    for l in L:
        if l != L[-1]:
            s += f'({l})|'
        else:
            s += f'({l})'
    return s 

rs = mkChoiceRegex(SYMBOLS)
ri = mkChoiceRegex(INTERVALS)

urlpatterns = [
    re_path(r'^(?i)(?P<symbol>' + rs + ')/(?P<interval>' + ri + ')/$',
        views.home,
        name='home',),
]
