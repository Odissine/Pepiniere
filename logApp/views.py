from django.shortcuts import render
import os
from pepiniere.settings import BASE_DIR
import ast
from datetime import datetime
import pandas as pd
from io import BytesIO
from django.http import HttpResponse, JsonResponse
import json


# Create your views here.
def read_log(mode="order"):
    data_dic = {}
    LOG_DIR = os.path.join(BASE_DIR, 'logs')
    if mode == "order":
        LOG_FILE = os.path.join(LOG_DIR, 'order_file.log')
        data_dic = {
            'user': [],
            'order': [],
            'action': [],
            'field': [],
            'old_data': [],
            'new_data': [],
            'year': [],
            'month': [],
            'day': [],
            'hours': [],
            'minutes': []
        }
    if mode == "produit":
        LOG_FILE = os.path.join(LOG_DIR, 'produit_file.log')
        data_dic = {
            'user': [],
            'produit': [],
            'order': [],
            'action': [],
            'field': [],
            'old_data': [],
            'new_data': [],
            'year': [],
            'month': [],
            'day': [],
            'hours': [],
            'minutes': []
        }
    if mode == "cart":
        LOG_FILE = os.path.join(LOG_DIR, 'cart_file.log')
        data_dic = {
            'user': [],
            'cart': [],
            'order': [],
            'produit': [],
            'action': [],
            'field': [],
            'old_data': [],
            'new_data': [],
            'year': [],
            'month': [],
            'day': [],
            'hours': [],
            'minutes': []
        }
    data_file = open(LOG_FILE, "r")
    data = []
    # my_dic = []
    for data in data_file:
        my_data = data.split(' ', 3)
        my_dic = my_data[3][:-1]
        my_dic = ast.literal_eval(my_dic)

        log_date = datetime.strptime(my_data[1], '%Y-%m-%d')
        log_time = datetime.strptime(my_data[2], '%H:%M:%S')
        my_dic['year'] = datetime.strftime(log_date, '%Y')
        my_dic['month'] = datetime.strftime(log_date, '%m')
        my_dic['day'] = datetime.strftime(log_date, '%d')
        my_dic['hours'] = datetime.strftime(log_time, '%H')
        my_dic['minutes'] = datetime.strftime(log_time, '%M')

        for key in my_dic:
            data_dic[key].append(my_dic[key])
    return data_dic


def data_to_csv(request):
    order = read_log('order')
    cart = read_log('cart')
    produit = read_log('produit')
    with BytesIO() as b:
        order_df = pd.DataFrame(order)
        cart_df = pd.DataFrame(cart)
        produit_df = pd.DataFrame(produit)
        with pd.ExcelWriter(b) as writer:
            order_df.to_excel(writer, sheet_name="ORDER", index=False)
            cart_df.to_excel(writer, sheet_name="CART", index=False)
            produit_df.to_excel(writer, sheet_name="PRODUIT", index=False)
        filename = "Logs.xlsx"
        res = HttpResponse(
            b.getvalue(),  # Gives the Byte string of the Byte Buffer object
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        res['Content-Disposition'] = f'attachment; filename={filename}'
        return res

    # print("DF", df)
    # csv = df.to_csv()
    # print("CSV", csv)


def show_line(request, produit):
    dic = read_log(mode="produit")
    data = {'status' : True}
    sf = []
    sp = []
    sb = []
    stock = {}
    stock['sf'] = []
    stock['sb'] = []
    stock['sp'] = [0]
    labels = ['Début']
    i = 0
    first_sf = True
    first_sb = True
    first_sp = True

    for p in dic['produit']:
        if str(p) == str(produit) and dic['order'][i] is not None:

            # STOCK PRECOMMANDE
            if dic['field'][i] == "sp":
                if first_sp:
                    stock['sp'].append(dic['old_data'][i])
                    first_sp = False
                stock['sp'].append(dic['new_data'][i])
            else:
                if 0 < len(stock['sp']) < len(labels):
                    stock['sp'].append(stock['sp'][len(stock['sp']) - 1])
                else:
                    stock['sp'].append(0)

            # STOCK FINAL
            if dic['field'][i] == "sf":
                if first_sf:
                    stock['sf'].append(dic['old_data'][i])
                    while len(stock['sf']) < len(stock['sp']):
                        stock['sf'].append(dic['old_data'][i])
                    first_sf = False
                stock['sf'].append(dic['new_data'][i])
            else:
                if len(stock['sf']) > 0:
                    stock['sf'].append(stock['sf'][len(stock['sf'])-1])

            # STOCK BIS
            if dic['field'][i] == "sb":
                if first_sb:
                    stock['sb'].append(dic['old_data'][i])
                    while len(stock['sb']) < len(stock['sp']) and len(stock['sb']) < len(labels):
                        stock['sb'].append(dic['old_data'][i])
                    first_sb = False
                stock['sb'].append(dic['new_data'][i])
            else:
                if len(stock['sb']) > 0:
                    stock['sb'].append(stock['sb'][len(stock['sb']) - 1])

            # stock[dic['field'][i]].append(dic['new_data'][i])
            labels.append(dic['day'][i]+"-"+dic['month'][i]+" @ "+dic['hours'][i]+":"+dic['minutes'][i])

        i += 1
    # df = pd.DataFrame(dic)

    # data = read_log(mode="produit")
    # df = px.data.gapminder().data("order" == "472")
    # fig = px.line(df, x='year', y='produit', color='action', symbol="new_data")
    # fig.show()
    # df = px.data.gapminder().query("continent == 'Oceania'")
    print(stock['sb'])
    data['chart'] = {
        'labels': labels,
        'datasets': [
            {
                'label' : 'Stock Final',
                'backgroundColor': 'rgb(120, 200, 90)',
                'borderColor': 'rgb(120, 200, 90)',
                'data': stock['sf'],

            },
            {
                'label': 'Stock En cours',
                'backgroundColor': 'rgb(255, 199, 85)',
                'borderColor': 'rgb(255, 199, 85)',
                'data': stock['sb'],
            },
            {
                'label': 'Stock Futur',
                'backgroundColor': 'rgb(100, 175, 200)',
                'borderColor': 'rgb(100, 175, 200)',
                'data': stock['sp'],
            },
        ]
              }
    return JsonResponse(data, safe=False)