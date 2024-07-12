from utils.proxy_handlers import ProxyCheckers
from utils.proxy_scraper import ProxyScraper
from os.path import exists, abspath
from threading import Lock
from os import makedirs
import json


class Proxies:
    DIR_PATH: str = "./proxy_files"
    HTTP_DIR: str = f"{DIR_PATH}/http_proxies.txt"
    HTTPS_DIR: str = f"{DIR_PATH}/https_proxies.txt"
    SOCKS4_DIR: str = f"{DIR_PATH}/socks4_proxies.txt"
    SOCKS5_DIR: str = f"{DIR_PATH}/socks5_proxies.txt"
    PROXIES_DUMP: str = f"{DIR_PATH}/proxies_dump.json"

    def __init__(self,
                 validate_proxies: bool = False,
                 enable_threading: bool = True
                 ) -> None:
        self.__enable_threading: bool = enable_threading
        self.__threading_lock: Lock = Lock()
        self._proxy_checker: ProxyCheckers = ProxyCheckers()
        self._proxy_scraper: ProxyScraper = ProxyScraper(
            lock=self.__threading_lock,
            enable_threading=self.__enable_threading
        )
        self._validate_proxies: bool = validate_proxies
        self._stop_requested: bool = False
        self._check_the_path()

    def _check_the_path(self) -> None:
        if not exists(abspath(self.DIR_PATH)):
            makedirs(abspath(self.DIR_PATH))

    def _create_files(self, proxies: dict) -> None:
        http_proxies_list: list = [proxy['proxy'] for proxy in proxies['http']]
        https_proxies_list: list = [proxy['proxy'] for proxy in proxies['https']]
        socks4_proxies_list: list = [proxy['proxy'] for proxy in proxies['socks4']]
        socks5_proxies_list: list = [proxy['proxy'] for proxy in proxies['socks5']]
        file_directories: dict = {
            self.HTTP_DIR: http_proxies_list,
            self.HTTPS_DIR: https_proxies_list,
            self.SOCKS4_DIR: socks4_proxies_list,
            self.SOCKS5_DIR: socks5_proxies_list,
        }
        for directory, write_data in file_directories.items():
            with open(directory, "w") as file:
                file.write("\n".join(write_data))
                file.close()

        # dump the complete proxies file
        with open(self.PROXIES_DUMP, "w") as file:
            json.dump(obj=proxies, fp=file)
            file.close()

    """
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

    def _validate_proxies_aliveness(self, proxies_list, proxies_type):
        with ThreadPoolExecutor(max_workers=self._num_workers) as executor:
            futures = []
            for proxy in proxies_list:
                future = executor.submit(self._validate_proxy, proxy, proxies_type)
                futures.append(future)

            for future in futures:
                if self._stop_requested:
                    break
                future.result()
    """

    def proxies_scraper(self):
        print("[INFO] Fetching Proxies from different sources")

        proxies: dict = self._proxy_scraper.scrape_proxies_lists()
        if self._validate_proxies:
            print(f"[+] Validating Proxies: Disabled For Now")

            # This validation is not correct I will change it in future
            # with ThreadPoolExecutor(max_workers=self._num_workers) as executor:
            #     futures = []
            #     for proxy_type in proxies.keys():
            #         print(f"[+] Validating Proxies of Type: {proxy_type}")
            #         future = executor.submit(self._validate_proxies_aliveness, http, proxy_type)
            #         futures.append(future)
            #     for future in futures:
            #         if self._stop_requested:
            #             break
            #         future.result()

        print("[INFO] Saving fetched data in files")
        self._create_files(proxies=proxies)


if __name__ == '__main__':
    number_of_threads = 10
    proxies_fetcher = Proxies()
    proxies_fetcher.proxies_scraper()
