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
            if qte > produit.stock_bis:
                message = "Stock insuffisant !"
                tags = "warning"
            else:
                message = "Produit ajouté au panier"
                tags = "success"
                self.cart[produit_id] = {'qte': qte, 'prix': str(produit.prix)}

        else:
            if override_qte:
                if qte > produit.stock:
                    message = "Stock insuffisant !"
                    tags = "warning"
                else:
                    self.cart[produit_id]['qte'] = qte
            else:
                if self.cart[produit_id]['qte'] + qte > produit.stock_bis:
                    message = "Stock insuffisant !"
                    tags = "warning"
                else:
                    message = "Quantité mise à jour"
                    tags = "success"
                    self.cart[produit_id]['qte'] += qte
        self.save()
        return message, tags

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
            item['prix'] = float(item['prix'])
            item['total'] = item['prix'] * item['qte']
            yield item

    def __len__(self):
        return sum(item['qte'] for item in self.cart.values())

    def get_total_prix(self):
        return sum(float(item['prix'])*float(item['qte']) for item in self.cart.values())

    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        self.save()

    def update_qte(self, produit, qte):
        produit_id = str(produit.id)
        print("Quantite : %s" % qte)
        print("Stock : %s" % produit.stock_bis)
        print("OK")
        if qte > produit.stock_bis:
            message = "Stock insuffisant !"
            tags = "warning"
        else:
            if produit_id in self.cart:
                item = self.cart[produit_id]
                item['qte'] = qte
                self.save()
            message = "Quantité mise à jour !"
            tags = "success"
        # return self.cart.values()
        return message, tags

    def update_prix(self, produit, prix):
        produit_id = str(produit.id)
        if produit_id in self.cart:

            item = self.cart[produit_id]
            prix = prix.replace(",", ".")

            if is_float(prix):
                prix = round(float(prix), 2)
                item['prix'] = prix
                self.save()
        return self.cart.values()


def is_float(number):
    try:
        float(number)
        return True
    except ValueError:
        return False