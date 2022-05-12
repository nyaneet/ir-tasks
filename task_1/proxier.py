"""
Proxy manager class
"""
from typing import List
from logging import Logger
from random import choice

import requests
from bs4 import BeautifulSoup


class ProxyManager():
    """
    Class for scrapping, storing and managing proxy list.

    Attributes:
        proxies: List of initial proxies.
        checked_url: Url used for checking if proxy is working.
        logger: Logger used for logging.
    """

    def __init__(self,
                 logger: Logger,
                 proxies: List[str] = None,
                 checked_url: str = 'https://www.google.com/') -> None:
        """
        Init ProxyManager
        """
        self.logger = logger
        self.checked_url = checked_url
        self._user_agent = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4)'
                            ' AppleWebKit/537.36 (KHTML, like Gecko) Chrome/'
                            '83.0.4103.97 Safari/537.36')
        self._proxy_source_url = ('https://hidemy.name/en/proxy-list/?maxtime'
                                  '=100&type=h#list')

        if proxies is not None:
            self.proxies = proxies.copy()
        else:
            self._update_proxies()

    def _update_proxies(self) -> None:
        """
        Clear old proxies and parse new ones.
        """
        self.proxies = []
        self._load_proxies()

    def _load_proxies(self) -> None:
        """
        Parse proxies from https://hidemy.name/ and update proxy list.
        """
        try:
            headers = {'User-Agent': self._user_agent}
            html_text = requests.get(url=self._proxy_source_url,
                                     headers=headers).text
            soup = BeautifulSoup(markup=html_text, features='lxml')

            free_proxy_container = soup.find('div', {'class': 'table_block'})
            free_proxy_table = free_proxy_container.find('tbody')

            for row in free_proxy_table.find_all('tr'):
                cols = row.find_all('td')
                if len(cols) != 0:
                    proxy_address = f'{cols[0].text}:{cols[1].text}'
                    if self._check_proxy(proxy_address):
                        self.proxies.append(proxy_address)

        except requests.exceptions.RequestException as err:
            self.logger.error(
                'An error occured while parsing proxies from "%s": %s',
                self._proxy_source_url, err)

    def _check_proxy(self, proxy_address: str) -> bool:
        """
        Check that the proxy is working.

        Args:
            proxy_address: Endpoint of the checking proxy, '{ip}:{port}'.

        Returns:
            True if the proxy is working, False otherwise.
        """
        headers = {'User-Agent': self._user_agent}
        proxies = {'http': f'http://{proxy_address}'}
        is_working_proxy = False

        try:
            response = requests.get(url=self.checked_url,
                                    headers=headers,
                                    proxies=proxies)

            response_status = response.status_code
            if response_status == 200:
                is_working_proxy = True
                self.logger.info('Checked proxy "%s"; Proxy is working',
                                 proxy_address)
            else:
                self.logger.info(
                    'Checked proxy "%s"; Response status code - %d',
                    proxy_address, response_status)

        except requests.exceptions.RequestException as err:
            self.logger.error('An error occured while checking proxy "%s": %s',
                              proxy_address, err)

        return is_working_proxy

    def get_proxy(self) -> str:
        """
        Return random proxy from proxy list.

        Returns:
            Endpoint of the proxy, '{ip}:{port}'.

        Raises:
            IndexError: An error occured accessing the proxy
        """
        if len(self.proxies) == 0:
            raise IndexError('ProxyManager proxy list is empty')

        random_proxy_address = choice(self.proxies)
        return random_proxy_address

    def remove_proxy(self, proxy_address: str) -> None:
        """
        Remove proxy from proxy list.

        Args:
            proxy_address: Endpoint of the proxy to remove.
        """
        if proxy_address in self.proxies:
            self.proxies.remove(proxy_address)
            self.logger.info('Proxy "%s" removed from proxy list',
                             proxy_address)
        else:
            self.logger.warning('Proxy list does not contain "%s"',
                                proxy_address)

        if len(self.proxies) == 0:
            self._update_proxies()
