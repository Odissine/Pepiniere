import datetime

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


def set_inventaire_for_pre_order(order_id):
    order = Commande.objects.get(id=order_id)
    inventaire = Inventaire.objects.filter(start_date__gte=datetime.datetime.now())
    if len(inventaire) > 0:
        inventaire = Inventaire.objects.filter(start_date__gte=datetime.datetime.now()).order_by('end_date').first()
        print(inventaire)
        order.inventaire = inventaire
        order.save()
    else:
        last_inventaire = Inventaire.objects.all().order_by('-end_date').first()
        print(last_inventaire)
        # start_date = datetime.datetime.strptime(last_inventaire.start_date, "%d/%m/%Y")
        start_date = last_inventaire.end_date + datetime.timedelta(days=1)
        end_date = datetime.datetime(last_inventaire.end_date.year+1, last_inventaire.end_date.month, last_inventaire.end_date.day)
        inventaire = Inventaire.objects.create(start_date=start_date, end_date=end_date)
        inventaire.save()
    order.inventaire = inventaire
    order.save()

    return True
