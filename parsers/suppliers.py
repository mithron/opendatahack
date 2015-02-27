
#encoding: utf8

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
import csvkit
from urllib import urlencode

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


def load_schools():
    read_file = codecs.open('schools_buh_data-csv.txt', 'r')
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
                        'regNum': contract['regNum'],
                        'kpp': contract['suppliers']['supplier'].get('kpp'),
                        'name': contract['suppliers']['supplier']['organizationName'],
                        'address_ur': contract['suppliers']['supplier']['postAddress'],
                        'address_fact':contract['suppliers']['supplier']['factualAddress']
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
                geo_url = u'http://geocode-maps.yandex.ru/1.x/?format=json&geocode=' + sup_data['address_ur']
                try:
                    response = unirest.get(httplib2.iri2uri(geo_url))
                    geo_data = json.loads(response.body)
                    if int(geo_data['response']['metaDataProperty']['found']):
                        # response.GeoObjectCollection.featureMember[0].GeoObject.Point.pos.split(" ")[1]
                        lng, lat = geo_data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos'].split(' ')
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

def get_buh_info():
    with open("schools_buh_data.csv",'w') as buh_file:
        result_writer = csvkit.writer(buh_file)
        with open("school_ratings_adr.csv", 'r') as full_file:
            ratings_reader = csvkit.reader(full_file)
            result_writer.writerow(ratings_reader.next()+['kpp', 'inn', 'contractsNum', 'clearsp_id'])
            errors = 0
            failed = []
            for row in ratings_reader:
                ask= urlencode({cust_ask_name: row[9].encode('utf-8'), cust_ask_fields: cust_ret_fields})

                response = unirest.get((cust_mashape_url+ask),
                                       headers=headers)

                try:
                    if unicode(response.body['customers']['data'][0]['fullName']) == unicode(row[9]):
                        result_writer.writerow(row+[response.body['customers']['data'][0]['kpp'],
                                                    response.body['customers']['data'][0]['inn'],
                                                    response.body['customers']['data'][0]['contractsCount'],
                                                    response.body['customers']['data'][0]['id']])
                    else:
                        failed.append(row[9])
                        result_writer.writerow(row)
                except:
                    errors += 1
                    failed.append(row[9])
                    result_writer.writerow(row)
            print("Errors: %s" % str(errors))
            print("Failed: %s" % unicode(", ".join(failed)))


