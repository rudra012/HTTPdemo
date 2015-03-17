#!/usr/bin/python

# http://127.0.0.1:8880/data

from twisted.internet import reactor
from twisted.web.server import Site
from twisted.web.resource import Resource

data = 1

def update_data():
    global data
    data += 1
    reactor.callLater(0, update_data)

class DataPage(Resource):
    isLeaf = True
    def render_GET(self, request):
        return "<html><body>%s</body></html>" % (data, )

root = Resource()
root.putChild("data", DataPage())
factory = Site(root)
reactor.listenTCP(8880, factory)

update_data()

print "running"
reactor.run()

