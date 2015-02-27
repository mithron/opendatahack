from datetime import datetime
import json
from urlparse import urlparse
from pymongo.connection import Connection
from pymongo import json_util

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

from tornado.options import define, options

define("port", default=8888, help="run on the given port", type=int)

MONGO_URL = "" # found with $>heroku config
we_live = True

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/([^/]*)", MainHandler)
        ]
        settings = dict(
            autoescape=None,
        )
        tornado.web.Application.__init__(self, handlers, **settings)

        if we_live:
            self.con = Connection(MONGO_URL)
            self.database = self.con[urlparse(MONGO_URL).path[1:]]
        else:
            self.con = Connection('localhost', 27017)
            self.database = self.con["moscow"]


class MainHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.database

    def get(self, inn=None):
        if inn:
            suppliers = self.db["suppliers"].find({'inn': inn})
        else:
            suppliers = self.db["suppliers"].find()
        j_suppliers = []
        for supplier in suppliers:
            j_supplier = json.dumps(supplier, default=json_util.default)
            j_suppliers.append(j_supplier)
        self.write( json.dumps(j_suppliers) )


def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()