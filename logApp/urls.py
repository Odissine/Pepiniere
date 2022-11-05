from django.urls import path
from django.conf.urls import url
from logApp.views import *

app_name = 'logApp'

urlpatterns = [
    path('csv', data_to_csv, name='data-to-csv'),
    # GRAPH
    path('graph/line/<produit>', show_line, name='show-line'),
]
