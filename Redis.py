from redis import Redis, RedisError
import yaml
import logging

logging.basicConfig(filename="testRedis.log",format='%(asctime)s %(levelname)s:%(message)s', datefmt='%m/%d/%Y %I:%M:%S %p' )


redis_host = "localhost"
redis_port = 6379
redis_password = ""


class initRedis(object):


    def __init__(self):

        self.__count = 0
        self.__index = 1

        try:
            self.datamap = yaml.load(open('document.yaml')) #load data from document file
        except IOError as err:
            logging.error("There is an issue with yaml doc loading",err.message )
        #init redis
        try:
            self.__r = Redis(host=redis_host, port=redis_port, db=0)
        except Exception as err:
            logging.error(err.message)

        logging.info("------------------- Start the test ----------------------")

        self.__list = self.__r.keys()

        self.__delete()
        self.__initDb()
        b = self.__r.lrange("sites", "0", "-1")
        logging.info("------------------- print the list value ----------------------", b)
        print("print the list value", b)
        self.__rpop()



    def __initDb(self):
        # Init redis with data from document yaml file
        #logging.info("init db with data from document file")
        index = 1
        try:
            while (index < self.__countSites() + 1):
                curSite = "site" + str(index)
                self.__r.rpush("sites", self.datamap[curSite])
                index += 1
        except:
            pass
    def __delete(self):
    #delete old values from db
        logging.info("Clean the db from previous values")
        list=self.__list
        if (list):
            for site in list:
                logging.info("the site is", site)

                self.__r.delete(site)
    #Todo: update db with new data
    def __countSites(self):
        # calc the site in db
        siteCount = 0
        with open('document.yaml', 'r') as lines:
            for line in lines:
                if "site" in line:
                    siteCount = siteCount + 1
        siteCount = siteCount // 2
        return siteCount
    def __rpop(self):
        count=0
        while (count < self.__countSites()):
            site = self.__r.rpoplpush("sites", "sites")
            logging.info("-----------", count, site.decode('UTF-8'))
            print("----------------------", count, site.decode('UTF-8'))

            count = count + 1
        content = self.__r.rpop("sites")
        #logging.info("the content is", content)

if __name__ == '__main__':
    init=initRedis()
