# coding=utf-8

import datetime
import os
import requests
from subprocess import call
import logging
#from comm import str2unicode
APP_ID = '19762331'
API_KEY = 'a03GHp49ozDAV3K9StkZIsoF'
SECRET_KEY = 'RqDeiu7L75qhEkb85QDQLnqSMZAwBT4y'
WEATHER_VOICE_FILE_PATH="."
class BaiDuVoice(object):
    def __init__(self):
        self._key = "a03GHp49ozDAV3K9StkZIsoF"
        self._s_key = "RqDeiu7L75qhEkb85QDQLnqSMZAwBT4y"
        self._token = None
        self.filename = None

    def _get_token(self):
        url = "https://openapi.baidu.com/oauth/2.0/token"
        querystring = {"grant_type": "client_credentials", "client_id": self._key,
                       "client_secret": self._s_key}
        try:
            response = requests.get(url, params=querystring)
            #logger.info(response.content)
            data = response.json()
            token = data.get('access_token')
            self._token = token
        except Exception as e:
            print("wrong")
            #logger.error(e.message)

    def get_voice(self, text):
        self._get_token()
        if not self._token:
            return
        url = "https://tsn.baidu.com/text2audio"
        querystring = {"tok": self._token, "tex": text, "cuid": "ji", "ctp": "1", "lan": "zh"}

        resp = requests.get(url, params=querystring)
        chunk_size = 200
        path = '{}/{}.mp3'.format(WEATHER_VOICE_FILE_PATH, datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))
        with open(path, 'wb') as fd:
            for chunk in resp.iter_content(chunk_size):
                fd.write(chunk)
        self.filename = os.path.abspath(path)

WEATHER_KEY="39f274e1d133482e8bed1529aa4d788e"
class WeatherFetcher(object):
    def __init__(self, location):
        self._key = WEATHER_KEY
        self._location=location
        #self._location = str2unicode(location)

    def get_weather(self):
        """
        获取实时天气
        :param location:
        :return:
        """
        #https://api.heweather.net/s6/weather/now?location=beiging&key=39f274e1d133482e8bed1529aa4d788e&lang=en&unit=m
        params = {
            "location": self._location,
            "lang": "en",
            "unit": "m",
            "key":self._key
        }
        url = 'https://api.heweather.net/s6/weather/now'
        try:
            resp = requests.get(url, params=params, timeout=5)
            if resp.status_code == 200:
                results = resp.json().get('results')
                items = []
                for item in results:
                    now = item.get('now')
                    desc = now.get('text')
                    temp = now.get('temperature')
                    content = u'{},今天:{},温度:{} 摄氏度'.format(self._location, desc, temp)
                    items.append(content)
                return u'。'.join(items)
            else:
                status_code = resp.json().get('status_code')
                return   u'天气获取失败'
        except Exception as e:
            logging.error(e, exc_info=True)
            return e

    def get_suggestion(self):
        """
        获取生活指数
        :return:
        """
        params = {
            "key": self._key,
            "location": self._location,
            "language": "zh-Hans"
        }
        url = 'https://api.seniverse.com/v3/life/suggestion.json'
        try:
            resp = requests.get(url, params=params, timeout=5)
            if resp.status_code == 200:
                results = resp.json().get('results')
                items = []
                for item in results:
                    suggestion = item.get('suggestion')
                    data = []
                    for k in suggestion.keys():
                        name = WEATHER_DESC.get(k)
                        if not name:
                            continue
                        v = suggestion.get(k)
                        logger.info(u"{}_{}".format(k, v))
                        value = u';'.join(v.values())
                        data.append(u'{},{}'.format(name, value))
                    items.append(u'。'.join(data))
                return u'。'.join(items)
            else:
                status_code = resp.json().get('status_code')
                #msg = WEATHER_CODE.get(status_code)
                return u'生活指数获取失败'
        except Exception as e:
            logging.error(e, exc_info=True)
            return e

class Speaker(object):
    @staticmethod
    def speak(file_path):
        logging.info('Mp3 File:{}'.format(file_path))
        try:
            call(['mpg123', file_path])
        except Exception as e:
            logging.error(e, exc_info=True)

def broad_weather(locations):
    for location in locations:
        wf = WeatherFetcher(location=location)
        weather = wf.get_weather()
        print(weather)
        suggestion = wf.get_suggestion()
        print(suggestion)
        bd = BaiDuVoice()
        bd.get_voice(u"天气预报: {}, 以下是建议:{}".format(weather, suggestion))
        if bd.filename:
             Speaker.speak(bd.filename)


if __name__ == '__main__':
    broad_weather(['beijing'])
