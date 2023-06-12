from requests import get, Response, Session, cookies
from cloudscraper import CloudScraper
from utils.randomuser import users
from random import choice


class ResponseHandlers:
    def __init__(self):
        self._session = Session()
        self._session.cookies = cookies.RequestsCookieJar()
        self._cloud_session = CloudScraper()

    def get_response(self, url) -> any([None, Response]):
        headers = self._generate_headers()
        try:
            response = get(url=url, headers=headers)
            return response
        except Exception as e:
            print('[-] Unable to fetch response: ', e)
            return None

    def get_session_response(self, url) -> any([None, Response]):
        headers = self._generate_headers()
        try:
            response = self._session.get(url=url, headers=headers)
            return response
        except Exception as e:
            print('[-] Unable to fetch response: ', e)
            return None

    def get_cloud_bypass_response(self, url) -> any([None, Response]):
        headers = self._generate_headers()
        try:
            response = self._cloud_session.get(url=url, headers=headers)
            return response
        except Exception as e:
            print('[-] Unable to fetch response: ', e)
            return None

    @staticmethod
    def _generate_headers():
        user_header = choice(users)
        headers = {
            'User-Agent': user_header,
            'Accept-Language': 'en-US,en;q=0.8',
        }

        return headers
