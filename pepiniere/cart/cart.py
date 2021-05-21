from decimal import Decimal
from django.conf import settings
from onlineshop.models import Produit


class Cart(object):

    def __init__(self, request):
        """ INIT CART """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, produit, qte, override_qte=False):
        produit_id = str(produit.id)

        if produit_id not in self.cart:
            self.cart[produit_id] = {'qte': qte, 'prix': str(produit.prix)}

        else:
            if override_qte:
                self.cart[produit_id]['qte'] = qte
            else:
                self.cart[produit_id]['qte'] += qte
        self.save()

    def save(self):
        self.session.modified = True

    def remove(self, produit):
        produit_id = str(produit.id)
        if produit_id in self.cart:
            del self.cart[produit_id]
            self.save()

    def __iter__(self):
        produit_ids = self.cart.keys()
        produits = Produit.objects.filter(id__in=produit_ids)

        cart = self.cart.copy()
        for produit in produits:
            cart[str(produit.id)]['produit'] = produit

        for item in cart.values():
            item['prix'] = Decimal(item['prix'])
            item['total'] = item['prix'] * item['qte']
            yield item

    def __len__(self):
        return sum(item['qte'] for item in self.cart.values())

    def get_total_prix(self):
        return sum(Decimal(item['prix'])*Decimal(item['qte']) for item in self.cart.values())

    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        self.save()
