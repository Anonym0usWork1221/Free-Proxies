from utils.response_handlers import ResponseHandlers
from bs4 import BeautifulSoup, ResultSet, XMLParsedAsHTMLWarning
from traceback import format_exc
from collections import Counter
from threading import Lock, Thread
from time import sleep
import warnings
import json

warnings.filterwarnings(action="ignore", category=XMLParsedAsHTMLWarning, module="bs4")


class ProxyScraper:
    PROXIES: dict = {
        "http": [],
        "https": [],
        "socks4": [],
        "socks5": [],
    }
    BRACKET_RE: str = "\\(.*?\\)"

    def __init__(self, lock: Lock = Lock(), enable_threading: bool = True) -> None:
        self._response: ResponseHandlers = ResponseHandlers()
        self.__enable_threading: bool = enable_threading
        self.__threading_lock: Lock = lock

    def _append_proxy(self, protocol: str, proxy_info: dict[str, str]) -> None:
        with self.__threading_lock:
            self.PROXIES[protocol].append(proxy_info)

    def _scrape_free_proxies_list(
            self, url: str, protocol_column: int, protocol_value: str, if_else_set: tuple[str, str]
    ) -> bool:
        try:
            # https://free-proxy-list.net/
            # https://www.socks-proxy.net/
            response = self._response.get_response(url=url)
            rows: ResultSet = BeautifulSoup(
                markup=response.content, parser="html.parser", features="lxml"
            ).find_all(name='tr')
            for row in rows:
                data: list[str] = [cell.text for cell in row.find_all(name='td')]
                if data and len(data) >= 8 and Counter(data[0])['.'] == 3:
                    proxy, country_name = f'{data[0]}:{data[1]}', data[3]
                    is_protocol: bool = data[protocol_column].lower() == protocol_value  # 6, yes
                    proxy_info: dict = {
                        'proxy': proxy,
                        'country_name': country_name,
                    }
                    if is_protocol:
                        # https
                        self._append_proxy(protocol=if_else_set[0], proxy_info=proxy_info)
                    else:
                        # http
                        self._append_proxy(protocol=if_else_set[1], proxy_info=proxy_info)
            return True

        except Exception as e:
            error_trace_back: str = f"[ERROR]: {format_exc()} {e}"
            print(error_trace_back)
        return False

    def _scrape_free_proxy_list(self) -> None:
        self._scrape_free_proxies_list(url="https://free-proxy-list.net/", protocol_column=6,
                                       protocol_value="yes", if_else_set=("https", "http"))
        self._scrape_free_proxies_list(url="https://www.us-proxy.org/", protocol_column=6,
                                       protocol_value="yes", if_else_set=("https", "http"))
        self._scrape_free_proxies_list(url="https://free-proxy-list.net/uk-proxy.html", protocol_column=6,
                                       protocol_value="yes", if_else_set=("https", "http"))
        self._scrape_free_proxies_list(url="https://www.sslproxies.org/", protocol_column=6,
                                       protocol_value="yes", if_else_set=("https", "http"))
        self._scrape_free_proxies_list(url="https://free-proxy-list.net/anonymous-proxy.html", protocol_column=6,
                                       protocol_value="yes", if_else_set=("https", "http"))
        self._scrape_free_proxies_list(url="https://www.socks-proxy.net/", protocol_column=4,
                                       protocol_value="socks4", if_else_set=("socks4", "socks5"))

    def _scrape_proxy_scrape(self):
        # https://proxyscrape.com/free-proxy-list
        try:
            scraped_proxies: list[str] = self._response.get_response(
                url='https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies&proxy_format'
                    '=protocolipport&format=text').text.strip().split()

            for proxy in scraped_proxies:
                if proxy.startswith('socks4'):
                    proxy_info: dict = {
                        'proxy': proxy.replace('socks4://', ''),
                        'country_name': "Unknown",
                    }
                    self._append_proxy(proxy_info=proxy_info, protocol='socks4')
                elif proxy.startswith('socks5'):
                    proxy_info: dict = {
                        'proxy': proxy.replace('socks5://', ''),
                        'country_name': "Unknown",
                    }
                    self._append_proxy(proxy_info=proxy_info, protocol='socks5')
                elif proxy.startswith('http'):
                    proxy_info: dict = {
                        'proxy': proxy.replace('http://', ''),
                        'country_name': "Unknown",
                    }
                    self._append_proxy(proxy_info=proxy_info, protocol='http')
                elif proxy.startswith('https'):
                    proxy_info: dict = {
                        'proxy': proxy.replace('https://', ''),
                        'country_name': "Unknown",
                    }
                    self._append_proxy(proxy_info=proxy_info, protocol='https')
            return True
        except Exception as e:
            error_trace_back: str = f"[ERROR]: {format_exc()} {e}"
            print(error_trace_back)
        return False

    def _scrape_git_proxify(self):
        try:
            scraped_proxies: list[dict[str, any([str, dict])]] = json.loads(self._response.get_response(
                url='https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/all/data.json'
            ).text)

            for proxy_item in scraped_proxies:
                proxy = proxy_item['proxy']
                country = proxy_item['geolocation']['country']
                if proxy.startswith('socks4'):
                    proxy_info: dict = {
                        'proxy': proxy.replace('socks4://', ''),
                        'country_name': country,
                    }
                    self._append_proxy(proxy_info=proxy_info, protocol='socks4')
                elif proxy.startswith('socks5'):
                    proxy_info: dict = {
                        'proxy': proxy.replace('socks5://', ''),
                        'country_name': country,
                    }
                    self._append_proxy(proxy_info=proxy_info, protocol='socks5')
                elif proxy.startswith('http'):
                    proxy_info: dict = {
                        'proxy': proxy.replace('http://', ''),
                        'country_name': country,
                    }
                    self._append_proxy(proxy_info=proxy_info, protocol='http')
                elif proxy.startswith('https'):
                    proxy_info: dict = {
                        'proxy': proxy.replace('https://', ''),
                        'country_name': country,
                    }
                    self._append_proxy(proxy_info=proxy_info, protocol='https')
            return True
        except Exception as e:
            error_trace_back: str = f"[ERROR]: {format_exc()} {e}"
            print(error_trace_back)
        return False

    def _scrape_proxy_list_download(self):
        try:
            with self.__threading_lock:
                protocols = self.PROXIES.keys()
            for proxy_type in protocols:
                response = self._response.get_session_response(
                    url=f'https://www.proxy-list.download/api/v1/get?type={proxy_type}')
                if response.status_code == 200:
                    proxies_list: list[str] = BeautifulSoup(response.text,
                                                            parser="html.parser",
                                                            features="lxml").text.strip().split()
                    for proxy in proxies_list:
                        proxy_info: dict = {
                            'proxy': proxy.strip(),
                            'country_name': "Unknown",
                        }
                        self._append_proxy(protocol=proxy_type, proxy_info=proxy_info)
                    sleep(5)
        except Exception as e:
            error_trace_back: str = f"[ERROR]: {format_exc()} {e}"
            print(error_trace_back)
        return False

    def _clean_proxies(self) -> None:
        iterated_proxies: set = set()
        unique_proxies: dict = {}
        for protocol, proxies in self.PROXIES.items():
            unique_proxies[protocol] = []
            for proxy in proxies:
                if proxy["proxy"] not in iterated_proxies:
                    iterated_proxies.add(proxy["proxy"])
                    unique_proxies[protocol].append(proxy)

        self.PROXIES = unique_proxies

    def scrape_proxies_lists(self) -> dict:
        functions_to_call = [
            self._scrape_git_proxify,
            self._scrape_free_proxy_list,
            self._scrape_proxy_scrape,
            self._scrape_proxy_list_download

        ]
        if not self.__enable_threading:
            for function in functions_to_call:
                function()
        else:
            launched_threads = []
            for function in functions_to_call:
                thread_id = Thread(target=function)
                thread_id.start()
                launched_threads.append(thread_id)
            # Wait for all threads to complete
            for thread in launched_threads:
                thread.join()
        self._clean_proxies()
        return self.PROXIES

