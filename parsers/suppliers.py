#encoding: utf8

"""
Use refine filter for export from school_buh_data:

    {
      "full_name" : {{jsonize(cells["full_name"].value)}},
      "lng" : {{jsonize(cells["lng"].value)}},
      "lat" : {{jsonize(cells["lat"].value)}},
      "kpp" : {{jsonize(cells["kpp"].value)}},
      "inn" : {{jsonize(cells["inn"].value)}}
    }
"""
import unirest
from collections import OrderedDict
import json
import httplib2
import csvkit
from urllib import urlencode
import io

headers = {
    "X-Mashape-Key": "uJeBYfacdymsht703eCMb02gNbpAp1VneSSjsnW1f5sK8lxEav",
    "Accept": "application/json"
}

class Item:
    def __init__(self, name, lng, lat, kpp, inn):
        self.name = name
        self.lng = lng
        self.tal = lat
        self.kpp = kpp
        self.inn = inn


class Schools(Item):
    suppliers_sums = {} #  Item: summ

cont_mashape_url = 'https://clearspending.p.mashape.com/v1/contracts/select/?'
cont_ask_name = 'name'
cont_ask_like = 'namesearch'
cont_ask_fields = 'returnfields'
cont_ret_fields = '[inn,kpp,id,contractsCount,fullName]'

cust_mashape_url = 'https://clearspending.p.mashape.com/v1/customers/search/?'
cust_ask_name = 'name'
cust_ask_like = 'namesearch'
cust_ask_fields = 'returnfields'
cust_ret_fields = '[suppliers,products,price,signDate,regNum]'


def get_all_suppliers_for_refine():
    data = json.load(open('schools_buh_data-csv.txt')).get('rows')
    errors = []
    with io.open("log.txt", "w", encoding='utf8') as log_file:
        with io.open("schools-suppliers.json", "w", encoding='utf8') as result_file:
            result_file.write(u"[")
            for i, row in enumerate(data):
                print("Going for %s" % str(i))
                try:
                    response = unirest.get(("https://clearspending.p.mashape.com/v1/"
                                        "contracts/select/?customerinn={0}&perpage=500").format(row['inn']),
                                        headers=headers)

                except:
                    try:
                        ask= urlencode({cont_ask_name: row['full_name'].encode('utf-8'), cont_ask_fields: cont_ret_fields})
                        response = unirest.get((cont_mashape_url+ask),headers=headers)
                    except:
                        errors.append(format(row['inn']))
                        print(row['inn'])
                        log_file.write(json.dumps(row, ensure_ascii=False, encoding='utf8' ))
                        continue
                if type(response.body) != dict:
                    print(response.body)
                    errors.append(format(row['inn']))
                    print(row['inn'])
                    log_file.write(json.dumps(row, ensure_ascii=False, encoding='utf8' ))
                    continue
                else:
                    result_file.write(json.dumps(response.body, ensure_ascii=False, encoding='utf8'))
                if (i + 1) < len(data):
                    result_file.write(u', ')
            result_file.write(u"]")
    print("Errors: %s" % str(len(errors)))
    print("Failed inns: %s" % unicode(", \n".join(errors)))


get_all_suppliers_for_refine()

def load_schools():
    data = json.load(open('schools_buh_data-csv.txt')).get('rows')
    with io.open("schools-suppliers.txt", "w", encoding='utf8') as result_file:
        result_file.write(u"[")
        for i, row in enumerate(data):
            suppliers = {}
            try:
                response = unirest.get(("https://clearspending.p.mashape.com/v1/"
                                        "contracts/select/?customerinn={0}&perpage=500").format(row['inn']),
                                        headers=headers)

            except:
                try:
                    ask= urlencode({cont_ask_name: row['full_name'].encode('utf-8'), cont_ask_fields: cont_ret_fields})
                    response = unirest.get((cont_mashape_url+ask),headers=headers)
                except:
                    continue
            if type(response.body) != dict:
                print response.body
                continue
            for contract in response.body['contracts']['data']:
                sup_inn = contract['suppliers']['supplier']['inn']
                if sup_inn in suppliers:
                    suppliers[sup_inn]['summ'] += contract['price']
                    suppliers[sup_inn]['contracts'].append({'date': contract['signDate'], 'price': contract['price'],
                                                            'regNum': contract['regNum'],'products': []})

                else:
                    suppliers['sup_inn'] = {
                        'contracts': [{'date': contract['signDate'],'price': contract['price'], 'products': []}],
                        'inn': sup_inn,
                        'cont_id': contract['regNum'],
                        'kpp': contract['suppliers']['supplier'].get('kpp'),
                        'name': contract['suppliers']['supplier'].get('organizationName'),
                        'address_ur': contract['suppliers']['supplier'].get('postAddress'),
                        'address_fact':contract['suppliers']['supplier'].get('factualAddress')
                        }
                if type(contract['products']['product']) != list:
                    try:
                        suppliers['sup_inn']['contracts'][-1]['products'].append(
                            {'name': contract['products']['product']['name']})
                    except:
                        continue
                else:
                    for item in contract['products']['product']:
                        suppliers['sup_inn']['contracts'][-1]['products'].append(
                            {'name': item['name']})
            for sup_inn, sup_data in suppliers.iteritems():
                if not sup_data['address']:
                    continue
                geo_url = u'http://geocode-maps.yandex.ru/1.x/?format=json&geocode=' + sup_data['address']
                try:
                    response = unirest.get(httplib2.iri2uri(geo_url))
                    geo_data = response.body
                    if int(geo_data['response']['GeoObjectCollection']['metaDataProperty']['GeocoderResponseMetaData']['found']):
                        # response.GeoObjectCollection.featureMember[0].GeoObject.Point.pos.split(" ")[1]
                        lng, lat = geo_data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos'].split(' ')
                    suppliers[sup_inn]['lng'] = lng
                    suppliers[sup_inn]['lat'] = lat
                except:
                    continue
        
            result_row = row
            result_row['suppliers'] = suppliers
            result_file.write(json.dumps(result_row, ensure_ascii=False, encoding='utf8'))
            if (i + 1) < len(data):
                result_file.write(u', ')
        result_file.write(u"]")


