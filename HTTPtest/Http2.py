import cx_Oracle
import json
from twisted.internet import reactor, task
from twisted.web.resource import Resource
from twisted.web.server import Site, NOT_DONE_YET
from twisted.enterprise import adbapi

salesVolumeResult = []
unscheduledResult = []

class SalesVolume(Resource):
    isLeaf = True

def render_GET(self, request):
    return salesVolumeResult

class Unscheduled(Resource):
    isLeaf = True

    def render_GET(self, request):
    	return unscheduledResult

class GetResultsFromDB():
    def __init__(self):
    	print '__init__'
    	self.myDsn = cx_Oracle.makedsn('ipaddress',1521,'SID')
    	self.dbpool = adbapi.ConnectionPool('cx_Oracle', user='uname', password     ='password', dsn= self.myDsn)

    def _getResults(self, txn, query):
        print '_getResults'
        txn.execute(query)
        return txn.fetchall()


    def printResults(self, results, query_type):
        print 'printResults'

        #here is the logic to get result
        if query_type == 'sales':
            global salesVolumeResult
            salesVolumeResult = json.dumps(results)
        elif query_type == 'unscheduled':
             global unscheduledResult
             unscheduledResult = json.dumps(results)
        else:
             print 'Unknown query type'

    def printError(self, error):
        print error.getErrorMessage()
        self.dbpool.close

    def closeDBCallback(self, results):
        print 'closeDBCallback'
        print 'successful'
        self.dbpool.close

    def queryUnscheduledResults(self, result):
        print 'queryUnscheduledResults'
        query_unscheduled = "select query which runs for 10 seconds"
        (self.dbpool.runInteraction(self._getResults, query_unscheduled).addCallback(
            self.printResults, "unscheduled").addErrback(self.printError)).addCallbacks(self.closeDBCallback).addErrback(self.printError)


    def querySalesResult(self):
        print 'querySalesResult'

        query_salesVolume = "select ..."
        (self.dbpool.runInteraction(self._getResults, query_salesVolume).addCallback(
            self.printResults, "sales").addErrback(self.printError)).addCallbacks(self.queryUnscheduledResults).addErrback(self.printError)

    def initiateDBIteration(self):
        print 'initiateDBIteration'
        i = task.LoopingCall(self.querySalesResult)
        i.start(300.0).addCallbacks(self.initiateDBIteration, self.printError)

def main():
    GetResultsFromDB().initiateDBIteration()
    root = Resource()
    root.putChild("salesvolume", SalesVolume())
    root.putChild("unscheduled", Unscheduled())
    factory = Site(root)
    reactor.listenTCP(8888, factory)
    reactor.run()

if __name__ == "__main__":
    main()