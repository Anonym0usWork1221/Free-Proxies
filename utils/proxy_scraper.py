from utils.response_handlers import ResponseHandlers
from collections import Counter
from bs4 import BeautifulSoup
from time import sleep
import json


class ProxyScraper:
    def __init__(self):
        self._response = ResponseHandlers()
        self._http = set()
        self._https = set()
        self._socks4 = set()
        self._socks5 = set()

    def _scrape_free_proxies_list(self):
        try:
            response = self._response.get_response(url='https://free-proxy-list.net/')
            soup = BeautifulSoup(response.content, parser="html.parser", features="lxml")
            rows = soup.find_all('tr')
            https = []
            http = []
            for row in rows:
                data = [cell.text for cell in row.find_all('td')]
                if data:
                    if len(data) >= 8 and Counter(data[0])['.'] == 3:
                        ip_proxy = f'{data[0]}:{data[1]}'
                        if data[6].lower() == "yes":
                            https.append(ip_proxy)
                        elif data[6].lower() == "no":
                            http.append(ip_proxy)

            self._http.update(http)
            self._https.update(https)
            return True

        except Exception as e:
            print(e)
        return False

    def _scrape_socks_proxy_net(self):
        try:
            response = self._response.get_response(url='https://www.socks-proxy.net/')
            soup = BeautifulSoup(response.content, parser="html.parser", features="lxml")
            rows = soup.find_all('tr')
            socks4 = []
            socks5 = []
            for row in rows:
                data = [cell.text for cell in row.find_all('td')]
                if data:
                    if len(data) >= 8 and Counter(data[0])['.'] == 3:
                        ip_proxy = f'{data[0]}:{data[1]}'
                        if data[4].lower() == "socks4":
                            socks4.append(ip_proxy)
                        elif data[4].lower() == "socks5":
                            socks5.append(ip_proxy)

            self._socks4.update(socks4)
            self._socks5.update(socks5)
            return True

        except Exception as e:
            print(e)
        return False

    def _scrape_premium_proxy(self):
        try:
            http = []
            https = []
            socks4 = []
            socks5 = []

            http_request = self._response.get_response(url='https://premiumproxy.net/full-proxy-list').text
            http_soup = BeautifulSoup(http_request, parser="html.parser", features="lxml")
            http_data = http_soup.select_one(selector="table > tbody")
            http_data_rows = http_data.find_all(name="tr")

            for row in http_data_rows:
                data = [cell.text for cell in row.find_all('td')]
                if data:
                    if len(data) >= 6 and Counter(data[0])['.'] == 3:
                        ip_proxy = f'{data[0]}'
                        if "https" in data[1].lower():
                            https.append(ip_proxy)
                        elif "http" in data[1].lower():
                            http.append(ip_proxy)
                        elif "socks4" in data[1].lower():
                            socks4.append(ip_proxy)
                        elif "socks5" in data[1].lower():
                            socks5.append(ip_proxy)

            self._http.update(http)
            self._https.update(https)
            self._socks4.update(socks4)
            self._socks5.update(socks5)
            return True
        except Exception as e:
            print(e)
        return False

    def _scrape_proxy_list_download(self):
        try:
            http = []
            https = []
            socks4 = []
            socks5 = []
            p_types = ["http", "https", "socks4", "socks5"]
            for proxy_type in p_types:
                response = self._response.get_session_response(
                    url=f'https://www.proxy-list.download/api/v1/get?type={proxy_type}')
                if response.status_code == 200:
                    response_soup = BeautifulSoup(response.text, features="xml")
                    response_str = response_soup.text.strip()
                    response_content = [content.strip() for content in response_str.split()]
                    if proxy_type == "http":
                        http.extend(response_content)
                    elif proxy_type == "https":
                        https.extend(response_content)
                    elif proxy_type == "socks4":
                        socks4.extend(response_content)
                    elif proxy_type == "socks4":
                        socks5.extend(response_content)
                    sleep(5)
            self._http.update(http)
            self._https.update(https)
            self._socks4.update(socks4)
            self._socks5.update(socks5)
            return True
        except Exception as e:
            print(e)
        return False

    def _scrape_proxy_scan(self):
        try:
            http = []
            https = []
            socks4 = []
            socks5 = []
            p_types = ["http", "https", "socks4", "socks5"]
            for proxy_type in p_types:
                response = self._response.get_session_response(
                    url=f'https://www.proxyscan.io/api/proxy?format=txt&type={proxy_type}&limit=1000')
                if response == 200:
                    response_soup = BeautifulSoup(response.text, features="xml")
                    response_str = response_soup.text.strip()
                    response_content = [content.strip() for content in response_str.split()]
                    if proxy_type == "http":
                        http.extend(response_content)
                    elif proxy_type == "https":
                        https.extend(response_content)
                    elif proxy_type == "socks4":
                        socks4.extend(response_content)
                    elif proxy_type == "socks4":
                        socks5.extend(response_content)
            self._http.update(http)
            self._https.update(https)
            self._socks4.update(socks4)
            self._socks5.update(socks5)
            return True
        except Exception as e:
            print(e)
        return False

    def _scrape_geonode_com(self):
        try:
            http = []
            https = []
            socks4 = []
            socks5 = []
            response = self._response.get_session_response(
                url='https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by='
                    'lastChecked&sort_type=desc')
            if response.status_code == 200:
                json_data = response.content.decode()
                data = json.loads(json_data)
                ip_port_list = [(entry['ip'], entry['port'], entry['protocols']) for entry in data['data']]
                for ip, port, protocols in ip_port_list:
                    if protocols:
                        if "http" in protocols:
                            http.append(f"{ip}:{port}")
                        if "https" in protocols:
                            https.append(f"{ip}:{port}")
                        if "socks4" in protocols:
                            socks4.append(f"{ip}:{port}")
                        if "socks5" in protocols:
                            socks5.append(f"{ip}:{port}")

            self._http.update(http)
            self._https.update(https)
            self._socks4.update(socks4)
            self._socks5.update(socks5)
            return True
        except Exception as e:
            print(e)
        return False

    def test_run(self):
        self._scrape_proxy_list_download()
        self._scrape_free_proxies_list()
        self._scrape_socks_proxy_net()
        self._scrape_premium_proxy()
        self._scrape_geonode_com()
        self._scrape_proxy_scan()
        return self._http, self._https, self._socks4, self._socks5

    def reset_sets(self):
        self._http.clear()
        self._https.clear()
        self._socks4.clear()
        self._socks5.clear()

    def scrape_proxies_lists(self) -> tuple:
        self._scrape_proxy_list_download()
        self._scrape_free_proxies_list()
        self._scrape_socks_proxy_net()
        self._scrape_premium_proxy()
        self._scrape_geonode_com()
        self._scrape_proxy_scan()
        tuple_data = (list(self._http), list(self._https), list(self._socks4), list(self._socks5))
        return tuple_data

