import logging
import sys
from datetime import datetime
from order.models import *
from django.db.models import Sum, F
from django.urls import reverse
from django.shortcuts import HttpResponseRedirect
from onlineshop.models import *

order_logger = logging.getLogger('order')
produit_logger = logging.getLogger('produit')
cart_logger = logging.getLogger('cart')


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
    inventaire = Inventaire.objects.filter(start_date__gte=datetime.now())
    if len(inventaire) > 0:
        inventaire = Inventaire.objects.filter(start_date__gte=datetime.now()).order_by('end_date').first()
        print(inventaire)
        order.inventaire = inventaire
        order.save()
    else:
        last_inventaire = Inventaire.objects.all().order_by('-end_date').first()
        print(last_inventaire)
        # start_date = datetime.datetime.strptime(last_inventaire.start_date, "%d/%m/%Y")
        start_date = last_inventaire.end_date + datetime.timedelta(days=1)
        end_date = datetime(last_inventaire.end_date.year + 1, last_inventaire.end_date.month, last_inventaire.end_date.day)
        inventaire = Inventaire.objects.create(start_date=start_date, end_date=end_date)
        inventaire.save()
    order.inventaire = inventaire
    order.save()

    return inventaire


# QUANTITE TOTALE COMMANDE SUR DES COMMANDES DE LA PERIODE STATUT EN COURS / VALIDEE
def total_qte_inventaire_progress(produit):
    statut_valide = Statut.objects.get(nom="Validée")
    statut_encours = Statut.objects.get(nom="En cours")
    inventaire = Inventaire.objects.get(actif=True)
    total_qte = \
        Commande.objects.filter(Cartdbs__produit=produit, inventaire=inventaire, statut__in=[statut_valide, statut_encours]).aggregate(sum=Sum('Cartdbs__qte'))[
            'sum']
    print(produit)
    print(total_qte)

    if total_qte is None:
        total_qte = 0

    return total_qte


def get_admin_mode(user):
    try:
        admin_mode = AccessMode.objects.get(user=user).admin
    except:
        admin_mode = False
    return admin_mode


def custom_redirect(url_name, *args, **kwargs):
    import urllib.parse
    url = reverse(url_name, args=args)
    params = urllib.parse.urlencode(kwargs)
    return HttpResponseRedirect(url + "?%s" % params)


def get_orders_items_max(max_val=5):
    produits = Produit.objects.all()
    statut_encours = Statut.objects.get(nom="En cours")
    commandes_list = []
    commandes_query = Cartdb.objects.filter(qte__gte=max_val, commande__statut=statut_encours).order_by('commande__pk')
    commandes = list(set([x.commande for x in commandes_query]))

    # all_commandes = Commande.objects.filter(statut=statut_encours, Cartdbs__qte_lte=max_val)
    # print(len(all_commandes))
    # val = len(all_commandes)
    # for produit in produits:
    #     commandes = Cartdb.objects.filter(produit=produit, commande__statut=statut_encours)
    #     if len(commandes) > max_val:
    #         commandes = [x.commande for x in commandes]
    #         commandes_list.extend(list(commandes))
    # # new_commandes_list = set(commandes_list)
    # seen = set()
    # unique = []
    # for obj in commandes_list:
    #     if obj.id not in seen:
    #         unique.append(obj)
    #         seen.add(obj.id)
    #
    # unique.sort(key=lambda x: x.id)
    commandes_list = sorted(commandes, key=lambda x: x.id)
    return commandes_list


def log_order(user, order, action, field, old_data, new_data):
    message = {'user': user, 'order': order, 'action': action, 'field': field, 'old_data': old_data, 'new_data': new_data}
    order_logger.info(message)
    return True


def log_produit(model, user, produit, order, action, field, old_data, new_data):
    message = {'model': model, 'user': user, 'produit': produit, 'order': order, 'action': action, 'field': field, 'old_data': old_data, 'new_data': new_data}
    produit_logger.info(message)
    return True


def log_cart(user, cart, order, produit, action, field, old_data, new_data):
    message = {'user': user, 'cart': cart, 'order': order, 'produit': produit, 'action': action, 'field': field, 'old_data': old_data, 'new_data': new_data}
    cart_logger.info(message)
    return True