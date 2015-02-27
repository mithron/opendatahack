"""
Use refine filter for export from school_buh_data:

    {
      "full_name" : {{jsonize(cells["full_name"].value)}},
      "lng" : {{jsonize(cells["lng"].value)}},
      "lat" : {{jsonize(cells["lat"].value)}},
      "kpp" : {{jsonize(cells["kpp"].value)}},
      "inn" : {{jsonize(cells["inn"].value)}},
    }
"""
import unirest
from collections import OrderedDict
import json
import httplib2
import codecs

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
    read_file =  codecs.open('schools_buh_data-csv.txt','r')
    data = json.load(read_file).get('rows')
    with codecs.open("schools-suppliers.txt", 'w', encoding='utf8') as result_file:
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
                sup_inn = contract['suppliers']['supplier']['inn']
                if sup_inn in suppliers:
                    suppliers[sup_inn]['summ'] += contract['price']
                suppliers[sup_inn] = {
                    'inn': sup_inn,
                    'summ': contract['price'],
                    'kpp': contract['suppliers']['supplier'].get('kpp'),
                    'name': contract['suppliers']['supplier']['organizationName'],
                    'address': contract['suppliers']['supplier']['postAddress']
                }
            for sup_inn, sup_data in suppliers.iteritems():
                geo_url = u'u"http://geocode-maps.yandex.ru/1.x/?format=json&geocode=' + sup_data['address']
                try:
                    response = unirest.get(httplib2.iri2uri(geo_url))
                    geo_data = json.loads(response.body)
                    if int(geo_data['response']['metaDataProperty']['found']):
                        lng, lat = geo_data['response']['GeoObjectCollection']['featureMember'][0]['.']['Point']['pos'].split(' ')
                    suppliers[sup_inn]['lng'] = lng
                    suppliers[sup_inn]['lat'] = lat
                except:
                    continue
            for sup_inn, sup_data in suppliers.iteritems():
                result_row = row
                result_row['suppliers'] = sup_data
                result_file.write(json.dumps(result_row) + ', ')
        result_file.write("]")

load_schools()