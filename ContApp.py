
import time
import requests
import redis
import yaml
import logging
import ast
from ast import literal_eval
from enum import Enum

SUCCESS = 200
INCORRECTUSERNAME = 401
TIMEOUT = 403

class SiteProperties(Enum):
    SITE=1
    TITLE=2
    REDIRECT=3
    TIME=4
    COMMENTS=5

logging.basicConfig(filename="test.log",format='%(asctime)s %(levelname)s:%(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)
redis_host = "localhost"
redis_port = 6379
redis_password = ""

def reverese_hebrew_string(str):
    return "".join(reversed(str))


class Scanner(object):
    def __init__(self, site):

        self.__startTime=0
        domainName = site.site
        logging.info("------------------- Start the test ----------------------")
        logging.info("Site to validate is: %s", site.site)

        self.__startTime = time.time()
        try:
            response=requests.get(domainName)
        except requests.exceptions.ConnectionError as error:
            logging.error("Failed to browse to the site. value error:%s", error)
        logging.info("domain name is %s", response.url)
        try:
            self.__handle_response(site, response)
        except:
            logging.error("---------------------- Test Result:failed -----------------  Validation on this site have failed. Please check this site")



    def __handle_response(self, domain, resp):
        """Handle the response:
        1. Verify the url
        2. Verify the site content
        3.SMNP tests
        4.Check the url status"""

        #Check Url status

        logging.info("-----Test 1: Check the Url status-----")

        logging.info("-----Url status test has passed succefully----- ") if (self.__checkUrlStatus(resp.status_code)) else logging.error("--Invalid Url status--")
        # Check the redirect
        logging.info("-----Test 2: Check the Url redirect-----")

        logging.info("-----Url redirect test has passed succefully----- ") if (self.__isUrlRedirect(domain, resp)) else logging.error("-----Url redirect test failed-----")

        #self.__isUrlRedirect(domain, resp)
        # Check the site content
        page= resp.text
        title= page[page.find('<title>') + 7 : page.find('</title>')]
        logging.info("-----Test 3: Check the site content-----")

        logging.info("-----Comarpe content test has passed successfully-----") if (self.__checkTitle(domain, title))else logging.error(
            "-----compare contenet test failed-----")
        logging.info("-----Test 4: Check the Url page laoding-----")

        logging.info("-----Page loading test has passed succefully-----")if(self.__pageLoading(resp))else logging.error("-----Page loading test failed-----")

    def  __checkUrlStatus(self, respStstus):

        logging.info("the site staus is %s", respStstus)
        if respStstus == SUCCESS:
            logging.info("Browsing the site has been successful")
            return True
        if respStstus == INCORRECTUSERNAME:
            logging.info("Username and Password is incorrect.")
            return False
        if respStstus == TIMEOUT:
            logging.info("Too many failed login attempts. Try putting in the"
                  "correct credentials after some time has passed.")
            return False

    def __isUrlRedirect(self, site,  resp):
        """Verify the url
                """
        urls_lst = []
        # Check if  URL was redirected or not
        if resp.history:

            logging.info("Request was redirected")
            for response in resp.history:
                urls_lst.append(response.url)
        else:

            logging.info("Request was not redirected")
        # Verify that browsing has passed as expected
        logging.info("Verifying the browsing. "
                     "compare between the expected url %s and current url title %s", site.redirect, urls_lst[-1])

        if urls_lst[-1]==site.redirect or resp.url==site.redirect:
            print('Browser browsing was done properly')
            return True
        else:
            print("Browsing issue")
            return False

    def __checkTitle(self, site, title):
        logging.info("compare between the expected title %s and current site title %s", title, site.title)
        if title in site.title:
            return True
        else:
            return False
    def __pageLoading(self, response):
        # Printing the total time of the scan
        logging.info("")
        totalTime = time.time() - self.__startTime
        logging.info("The total time of the scan is --- %s seconds ---" % (time.time() - self.__startTime))

        # verify the total time of scan was  as expected
        if totalTime <= site.timeToReport:

            logging.info("Page load time was as expected")
            return True
        else:

            logging.info("Page load time was as expected")
            return False




def getUrl():
    try:
        r = redis.Redis(host=redis_host, port=redis_port, db=0)
    except ValueError as error:
        print("value error:", error)
    else:
        url = r.rpoplpush("sites", "sites")
        url = str(url, 'utf-8')
        #url = ast.literal_eval(url)
    if url =="None":
        print("Site not found as requested")
    try:
        siteIndx = url.find(SiteProperties.SITE.name.lower())
        tIndx = url.find(SiteProperties.TITLE.name.lower())
        rIndx = url.find(SiteProperties.REDIRECT.name.lower())
        timeIndx = url.find(SiteProperties.TIME.name.lower())
        commentIndx = url.find(SiteProperties.COMMENTS.name.lower())
    except ValueError as error:
        logging.error("value error:", error)

    site = url[siteIndx + 5:tIndx]
    title = url[tIndx + 6:rIndx]
    redirectUrl = url[rIndx + 14:timeIndx]
    timeToReport = url[timeIndx + 13:commentIndx]
    return SiteObj(site, title, redirectUrl, timeToReport)



   # object=abc(site,title,redirectUrl,timeToReport)

class SiteObj(object):
    def __init__(self, site, title, redirectUrl, timeToReport):
        self.site         = site
        self.title        = title
        self.redirect     = redirectUrl
        self.timeToReport = timeToReport

if __name__ == '__main__':

    scanner = Scanner(getUrl())  # ['gov.il', 'www.shabak.gov.il/Pages/index.html#=1'])


