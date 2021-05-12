
from server.apiserver import ApiServer, ApiRoute, ApiError, ApiHandler
import json
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MyServer(ApiServer):
        @ApiRoute("/popup")
        def addbar(req):
            return {"boo":req["bar"]+1}

        @ApiRoute("/baz")
        def justret(req):
            if req:
                 raise ApiError(501,"no data in for baz")
            return {"obj":1}
        @ApiRoute("/ezserver/api")
        def pyQuandCandle(req):

            queryString = ''
            if 'querystring' in req:
                queryString = req['querystring'][0]

            logger.debug("Search Sting : {}".format(queryString))

            #TODO
            # add the code to get the data from the arxiv database

            searchres = {  "organic_results":[
                {
                "position":  2,
                "title": "Best Coffee Shops in Austin, Winter 2019 - Eater Austin",
                "link":
                "https://austin.eater.com/maps/best-coffee-austin-cafes",
                "displayed_link":
                "https://austin.eater.com › maps › best-coffee-austin-cafes",
                "date":
                "Jan 10, 2020",
                "author":"BullFrog",
                "abstract":
                "28 Excellent Coffee Shops in Austin, Winter 2020 · 1. Machine Head Coffee · 2. Epoch Coffee · 3. Houndstooth Coffee · 4. Cherrywood ...",
                "score":25
                },
                {
                "position":3,
                "title": "13 Health Benefits of Coffee, Based on Science - Healthline",
                "link": "https://www.healthline.com/nutrition/top-13-evidence-based-health-benefits-of-coffee",
                "displayed_link":  "https://healthline.com › nutrition › top-13-evidence-bas...",
                "date": "Sep 20, 2018",
                "abstract":  "Coffee is the biggest source of antioxidants in the diet. It has many health benefits, such as improved brain function and a lower risk of serious ..."
                },
                {
                "position":  4,
                "title":
                "Peet's Coffee: The Original Craft Coffee",
                "link":
                "https://www.peets.com/",
                "displayed_link":
                "https://peets.com",
                "author":"BullFrog",
                "abstract":
                "Since 1966, Peet's Coffee has offered superior coffees and teas by sourcing the best quality coffee beans and tea leaves in the world and adhering to strict ...",
                "score":23
                }]
            }
            return json.dumps(searchres)

if __name__ == '__main__':
    from sys import argv
    if len(argv) == 2:
        MyServer("127.0.0.1",argv[1]).serve_forever()
    else:
        MyServer("127.0.0.1", 8001).serve_forever()
