from onlineshop.models import *

def get_object_from_id(id_object, model):
    val = None
    if id_object is None:
        val = None
    else:
        if model == 'espece':
            val = Espece.objects.get(id=id_object)
        if model == 'variete':
            val = Variete.objects.get(id=id_object)
        if model == 'portegreffe':
            val = PorteGreffe.objects.get(id=id_object)
        if model == 'spec':
            val = Spec.objects.get(id=id_object)
    return val
