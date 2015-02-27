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


def load_schools():
    data = json.load(open('schools_buh_data-csv.txt')).get('rows')
    with open("schools-suppliers.txt", "w") as result_file:
        result_file.write("[")
        for row in data:
            suppliers = {}
            try:
                response = unirest.get(("https://clearspending.p.mashape.com/v1/"
                                        "contracts/select/?customerinn={0}&perpage=500").format(row['inn']),
                                        headers=headers)
            except:
                continue
            if type(response.body) != dict:
                print response.body
                continue
            for contract in response.body['contracts']['data']:
                try:
                    sup_inn = contract['suppliers']['supplier'].get('inn')
                    if not sup_inn:
                        continue
                    if sup_inn in suppliers:
                        suppliers[sup_inn]['summ'] += contract['price']
                    print contract['suppliers']['supplier']
                    suppliers[sup_inn] = {
                        'inn': sup_inn,
                        'summ': contract['price'],
                        'kpp': contract['suppliers']['supplier'].get('kpp'),
                        'name': contract['suppliers']['supplier'].get('organizationName'),
                        'address': contract['suppliers']['supplier'].get('postAddress')
                    }
                except:
                    pass
            for sup_inn, sup_data in suppliers.iteritems():
                if not sup_data['address']:
                    continue
                geo_url = u'u"http://geocode-maps.yandex.ru/1.x/?format=json&geocode=' + sup_data['address']
                try:
                    response = unirest.get(httplib2.iri2uri(geo_url))
                    geo_data = json.loads(response.body)
                    if int(geo_data['response']['metaDataProperty']['found']):
                        lng, lat = geo_data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos'].split(' ')
                    suppliers[sup_inn]['lng'] = lng
                    suppliers[sup_inn]['lat'] = lat
                except:
                    continue
            for sup_inn, sup_data in suppliers.iteritems():
                result_row = row
                result_row['suppliers'] = sup_data
                result_file.write(json.dumps(result_row))
                if sup_inn != suppliers.keys()[-1]:
                    result_file.write(', ')
        result_file.write("]")

load_schools()