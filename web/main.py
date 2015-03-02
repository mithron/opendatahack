from datetime import datetime
import json
import os
from urlparse import urlparse
from pymongo.connection import Connection

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

from tornado.options import define, options


MONGO_URL = "" # found with $>heroku config
we_live = True

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/list/", MainHandler),
            (r"/([0-9]+)/", SchoolHandler)
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


class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.database


class SchoolHandler(BaseHandler):
    def get(self, inn=None):
        if inn:
            suppliers = list(self.db["suppliers"].find({'inn': int(inn)}, fields={"_id": False}))
            self.write(json.dumps(suppliers, ensure_ascii=False, encoding='utf8'))
        else:
            self.write("[]")


class MainHandler(BaseHandler):
    def get(self):
        schools = list(self.db["suppliers"].find(fields={"full_name": True, "inn": True, "_id": False}))
        self.write(json.dumps(schools, ensure_ascii=False, encoding='utf8'))


def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(int(os.environ.get("PORT", 8888)))
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()