import logging
import json
import os
import ast
from django.apps import apps
from logging import FileHandler, Handler, StreamHandler

request_logger = logging.getLogger('django.request')


class PepiniereFileHandler(FileHandler):

    def __init__(self, filename, mode='a', encoding=None, delay=False, errors=None):
        filename = os.fspath(filename)
        open(filename, 'a').close()

        self.baseFilename = os.path.abspath(filename)
        self.mode = mode
        self.encoding = encoding
        self.delay = delay
        self.errors = errors
        if delay:
            Handler.__init__(self)
            self.stream = None
        else:
            StreamHandler.__init__(self, self._open())


class PepiniereModelHandler(Handler):

    def __init__(self, *args, **kwargs):
        # self.model = kwargs

        # print(self.model)
        super(PepiniereModelHandler, self).__init__(*args, **kwargs)

    def emit(self, record):
        model = ""
        dic_message = ast.literal_eval(record.getMessage())
        message = dic_message

        user = message['user']
        order = message['order']
        action = message['action']
        field = message['field']
        old_value = message['old_data']
        new_value = message['new_data']
        model = message['model']

        if model == "Commande":
            Model = apps.get_model('order', 'LogOrder')
            obj = Model.objects.create(user=user, order=order, action=action, field=field, old_value=old_value, new_value=new_value)
        if model == "Produit":
            Model = apps.get_model('onlineshop', 'LogProduit')
            produit = message['produit']
            obj = Model.objects.create(user=user, produit=produit, order=order, action=action, field=field, old_value=old_value, new_value=new_value)
        if model == "Cart":
            Model = apps.get_model('onlineshop', 'LogCart')
            user_text = message['user_text']
            produit = message['produit']
            cart = message['cart']
            obj = Model.objects.create(user=user, user_text=user_text, cart=cart, order=order, produit=produit, action=action, field=field, old_value=old_value, new_value=new_value)
