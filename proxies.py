import signal
from concurrent.futures import ThreadPoolExecutor
from utils.proxy_handlers import ProxyCheckers
from utils.proxy_scraper import ProxyScraper
from os.path import exists, abspath
from os import makedirs


class Proxies:
    DIR_PATH = "./proxy_files"

    def __init__(self, num_workers=5):
        self._check_the_path()
        self._proxy_checker = ProxyCheckers()
        self._proxy_scraper = ProxyScraper()
        self._valid_http = set()
        self._valid_https = set()
        self._valid_socks4 = set()
        self._valid_socks5 = set()
        self._num_workers = num_workers
        self._stop_requested = False

    def _check_the_path(self):
        if not exists(abspath(self.DIR_PATH)):
            makedirs(abspath(self.DIR_PATH))

    def _create_files(self):
        with open(f"{self.DIR_PATH}/http_proxies.txt", "w") as file:
            file.write("\n".join(self._valid_http))

        with open(f"{self.DIR_PATH}/https_proxies.txt", "w") as file:
            file.write("\n".join(self._valid_https))

        with open(f"{self.DIR_PATH}/socks4_proxies.txt", "w") as file:
            file.write("\n".join(self._valid_socks4))

        with open(f"{self.DIR_PATH}/socks5_proxies.txt", "w") as file:
            file.write("\n".join(self._valid_socks5))

    def _validate_proxy(self, proxy, proxy_type):
        if self._stop_requested:
            return

        data_dict = self._proxy_checker.check_proxy_validation(proxy=proxy, proxy_type=proxy_type)
        if data_dict["status"] == "Valid":
            if proxy_type == "http":
                self._valid_http.add(proxy)
            elif proxy_type == "https":
                self._valid_https.add(proxy)
            elif proxy_type == "socks4":
                self._valid_socks4.add(proxy)
            elif proxy_type == "socks5":
                self._valid_socks5.add(proxy)

    def _validate_proxies(self, proxies_list, proxies_type):
        with ThreadPoolExecutor(max_workers=self._num_workers) as executor:
            futures = []
            for proxy in proxies_list:
                future = executor.submit(self._validate_proxy, proxy, proxies_type)
                futures.append(future)

            for future in futures:
                if self._stop_requested:
                    break
                future.result()

    def _commit_on_git(self):
        ...

    def _handle_signal(self, signum, frame):
        print("\n[+] Ctrl+C signal received. Stopping...")
        self._stop_requested = True

    def proxies_scraper(self):
        signal.signal(signal.SIGINT, self._handle_signal)

        print("[+] Fetching Proxies from different sources")
        http, https, socks4, socks5 = self._proxy_scraper.scrape_proxies_lists()
        p_types = ["http", "https", "socks4", "socks5"]
        print(f"[+] Validating Proxies: Working thread {self._num_workers}")
        with ThreadPoolExecutor(max_workers=self._num_workers) as executor:
            futures = []
            for proxy_type in p_types:
                print(f"[+] Validating Proxies of Type: {proxy_type}")
                future = executor.submit(self._validate_proxies, http, proxy_type)
                futures.append(future)
            for future in futures:
                if self._stop_requested:
                    break
                future.result()

        self._create_files()


if __name__ == '__main__':
    number_of_threads = 100
    proxies_fetcher = Proxies(num_workers=number_of_threads)
    proxies_fetcher.proxies_scraper()
