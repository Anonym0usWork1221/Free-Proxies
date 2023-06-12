from requests.exceptions import RequestException
from requests import get


class ProxyCheckers:
    TEST_ADDR = 'https://api.my-ip.io/ip'

    def __init__(self, time_out: int = 80):
        self._time_out = time_out
        super().__init__()

    @staticmethod
    def _proxy_unpacker(proxy: str) -> tuple:
        proxy_host, proxy_port = proxy.split(":")
        return proxy_host, proxy_port

    def check_proxy_validation(self, proxy: str,  proxy_type: str) -> dict:
        proxy_host, proxy_port = self._proxy_unpacker(proxy)
        proxy_url = f'{proxy_type}://{proxy_host}:{proxy_port}'
        target_url = self.TEST_ADDR
        proxies = {
            proxy_type: proxy_url,
        }
        try:
            response = get(target_url, proxies=proxies, timeout=self._time_out)
            if response.ok:
                ip_api_url = f'http://ip-api.com/json/{proxy_host}'
                ip_info = get(ip_api_url).json()
                country = ip_info.get('country')

                return {
                    'country': country,
                    'proxy': proxy_host,
                    'status': 'Valid',
                    'response_code': response.status_code
                }
            else:
                return {
                    'proxy': proxy_host,
                    'status': 'Invalid',
                    'response_code': response.status_code
                }
        except RequestException:
            return {
                'proxy': proxy_host,
                'status': 'Error',
                'response_code': None
            }
