from order.models import *


def get_frais_from_id(id):
    val = None
    if not id is None:
        val = Frais.objects.get(id=id)
    return val


def get_tva_from_id(id):
    val = None
    if not id is None:
        val = Tva.objects.get(id=id)
    return val
