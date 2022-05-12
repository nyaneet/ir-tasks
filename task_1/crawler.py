"""
Crawler for scrap data from https://habr.com
"""
from cgitb import html
import os
from typing import List
from multiprocessing import freeze_support, RLock
from concurrent.futures import ProcessPoolExecutor, as_completed

import requests
from tqdm.auto import tqdm
from bs4 import BeautifulSoup, SoupStrainer

from task_1.proxier import ProxyManager
from utils import subintervals, logging


def html_filter(html_text: str, classes: List[str] = None) -> str:
    """
    Extract and return html tags with specified classes.

    Args:
        html_text: HTML page content.
        classes: List of classes to extract.
    Returns:
        Сontent of extracted tags or original page content if no classes
        are specified.
    """
    if classes is None:
        soup = BeautifulSoup(markup=html_text, features='html5lib')
        return str(soup)

    parse_only = SoupStrainer(name='div', class_=classes)
    soup = BeautifulSoup(markup=html_text,
                         features='lxml',
                         parse_only=parse_only)
    return str(soup)


def download_posts(first_id: int,
                   last_id: int,
                   process_number: int,
                   proxies: List[str] = None,
                   path: str = None) -> None:
    """
    Download posts data from https://habr.com

    Args:
        first_id: ID of the first post to be downloaded.
        last_id: ID of the last post to be downloaded.
        process_number: Running process number.
        proxies: Initial proxy list.
        path: Directory where posts are downloaded.
    """
    logger = logging.get_logger(f'crawler_{process_number}')
    proxy_manager = ProxyManager(logger=logger, proxies=proxies)
    headers = {
        'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83'
                       '.0.4103.97 Safari/537.36')
    }

    for post_id in tqdm(range(first_id, last_id),
                        desc=f'{process_number:2}',
                        position=(process_number + 1),
                        leave=False):
        try:
            proxy_address = proxy_manager.get_proxy()
            proxies = {'http': f'http://{proxy_address}'}
            post_url = f'https://habr.com/ru/post/{post_id}/'
            response = requests.get(url=post_url,
                                    headers=headers,
                                    proxies=proxies)

            response_status = response.status_code
            if response_status == 200:
                html_text = html_filter(
                    html_text=response.content,
                    classes=[
                        'tm-article-presenter__body', 'tm-article-author'
                    ],
                )
                with open(f'{path}/{post_id}.html', 'w+',
                          encoding='utf-8') as file_:
                    file_.write(html_text)
                logger.info('Post "%s" saved as %s/%s.html', post_url, path,
                            post_id)
            elif response_status in (404, 403):
                logger.info(('Failed to download post "%s"; Post is not'
                             ' available, response status code - %d'),
                            post_url, response_status)
            else:
                proxy_manager.remove_proxy(proxy_address)
                logger.info(('Failed to download post "%s"; Response '
                             'status code - %d'), post_url, response_status)

        except requests.exceptions.RequestException as err:
            logger.error('An error occurred while downloading post "%s": %s',
                         post_url, str(err))


def crawl(first_id: int,
          last_id: int,
          max_workers: int = 1,
          path: str = 'data/unprocessed_posts') -> None:
    """
    Crawl posts data from https://habr.com

    Note:
        It is not recommended to set the value of the max_workers above 8.

    Args:
        first_id: ID of the first post to be crawled.
        last_id: ID of the last post to be crawled.
        max_workers: The maximum number of processes that will be used
        to crawling.
    """
    freeze_support()  # for Windows

    if not os.path.exists(path):
        os.makedirs(path)

    max_workers = min(max_workers, last_id - first_id)
    first_ids, last_ids = subintervals.get_subintervals(
        left=first_id, right=last_id, n_intervals=max_workers)

    logger = logging.get_logger(filename='clrawler_main')
    proxy_manager = ProxyManager(logger=logger)
    proxies = proxy_manager.proxies

    with ProcessPoolExecutor(max_workers=max_workers,
                             initargs=(RLock(), ),
                             initializer=tqdm.set_lock) as executor:
        with tqdm(total=max_workers,
                  position=0,
                  desc=f'Running {max_workers} processes') as process_bar:
            futures = [
                executor.submit(download_posts, first_ids[i], last_ids[i], i,
                                proxies, path) for i in range(max_workers)
            ]
            for _ in as_completed(futures):
                process_bar.update()
