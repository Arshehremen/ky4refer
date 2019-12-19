"""Unit wikipedia API Kabanov Andrew"""
# Модуль для обращения к API википедии
# специализирован для получения случайных статей

# interface

# uses
import requests

# type

"""
classes:
    WikipediaReader   //
"""

# const
LOGGING = False
WIKIPEDIA_API_URL = "https://ru.wikipedia.org/w/api.php"

# implementation


# класс для чтения сайтов википедии
class WikipediaReader:
    def __init__(self):
        self.titles_info = []
        self.texts = []

    def take_rnd(self, count=1):
        session = requests.Session()
        params = {
            "action": "query",
            "format": "json",
            "list": "random",
            'rnnamespace': 0,
            "rnlimit": count
        }
        request_result = session.get(url=WIKIPEDIA_API_URL, params=params)
        self.titles_info = request_result.json()['query']['random']
        return self
        
    def take_random_pages(self):
        def take_text(site):
            session = requests.Session()
            if LOGGING:
                print(str(site['id']) + ' : ' + site['title'])
            params = {
                "action": "query",
                "format": "json",
                'prop': 'extracts|revisions',
                'explaintext': '',
                'rvprop': 'ids',
                "pageids": str(site['id'])
            }
            request_result = session.get(url=WIKIPEDIA_API_URL, params=params)
            return request_result.json()['query']['pages'][str(site['id'])]['extract']
        
        self.texts = [take_text(site) for site in self.titles_info]
        
        return self

    def take_random_page_id(self):
        return self.take_rnd().titlesInfo[0]['id']
