from urllib import urlopen
from django.conf import settings
from xml.dom.minidom import parseString
import eveapi


class DefaultClassMethods(type):
    _auth = None

    def __getattr__(cls, attr):
        if not DefaultClassMethods._auth:
            api = eveapi.EVEAPIConnection()
            DefaultClassMethods._auth = api.auth(keyID=settings.EVE_USERID, vCode=settings.EVE_APIKEY)
        return getattr(DefaultClassMethods._auth, attr)


class EVEAPI(object):
    __metaclass__ = DefaultClassMethods


class MarketAPI(object):
    BASE_URL = 'http://api.eve-central.com/api/'

    @staticmethod
    def to_dict(data, items):
        return dict(
            (i, data.getElementsByTagName(i).item(0).childNodes[0].data)
            for i in items)

    @staticmethod
    def quicklock(id):
        page = urlopen("%squicklook?typeid=%s&usesystem=30000142" % (MarketAPI.BASE_URL, id))
        if page.code != 200:
            raise Exception(page.code)
        data = parseString(page.read())
        page.close()
        return data