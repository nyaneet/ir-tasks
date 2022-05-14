"""
Post processing for data extracting
"""
import os
import re
import json
from typing import Dict, List
from pathlib import Path

from bs4 import BeautifulSoup
from tqdm.auto import tqdm


def validate_post(post: Dict) -> bool:
    """
    Check post content length.

    Returns:
        True if the length >= 2000, False otherwise.
    """
    if len(post['content']) < 2000:
        return False
    return True


def clean_text(text: str) -> str:
    """
    Removes punctuation marks, special characters, extra spaces and urls.

    Args:
        text: Text to clean up.

    Returns:
        Clean text.
    """
    # Remove everything except letters, numbers, strings
    text = re.sub(r'-', '', text)
    text = re.sub(r'[^\w\s]+', ' ', text)
    # Remove all numbers
    text = re.sub(r'\s\d+\s', ' ', text)
    # Remove all urls
    text = re.sub(
        (r'(http|ftp|https):\/\/([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:\/~'
         '+#-]*[\w@?^=%&\/~+#-])'), '', text)
    # Remove all extra spaces
    text = re.sub(r'\s+', ' ', text)
    return text


def filter_post_html(post_soup: BeautifulSoup) -> None:
    """
    Remove <code> and <img> tags from post html tree.

    Args:
        post_soup: Post html tree as BeautifulSoup data structure.
    """
    code_tags = post_soup.find_all('code')
    for code_tag in code_tags:
        code_tag.decompose()

    img_tags = post_soup.find_all('img')
    for img_tag in img_tags:
        img_tag.decompose()


def extract_title(post_soup: BeautifulSoup) -> str:
    """
    Extract post title.

    Args:
        post_soup: Post html tree as BeautifulSoup data structure.
    """
    title = post_soup.find('h1', {'class': 'tm-article-snippet__title'}).text
    return title


def extract_datetime(post_soup: BeautifulSoup) -> str:
    """
    Extract post datetime.

    Args:
        post_soup: Post html tree as BeautifulSoup data structure.
    """
    datetime = post_soup.find('span', {
        'class': 'tm-article-snippet__datetime-published'
    }).find('time')['datetime']
    return datetime


def extract_rating(post_soup: BeautifulSoup) -> int:
    """
    Extract post rating.

    Args:
        post_soup: Post html tree as BeautifulSoup data structure.
    """
    rating = post_soup.find('span', {
        'class': 'tm-votes-meter__value_rating'
    }).text
    return int(rating)


def extract_bookmarks_count(post_soup: BeautifulSoup) -> int:
    """
    Extract post bookmarks count.

    Args:
        post_soup: Post html tree as BeautifulSoup data structure.
    """
    bookmarks_count = post_soup.find('span', {
        'class': 'bookmarks-button__counter'
    }).text
    return int(bookmarks_count)


def extract_comments_count(post_soup: BeautifulSoup) -> int:
    """
    Extract post comments count.

    Args:
        post_soup: Post html tree as BeautifulSoup data structure.
    """
    comments_count_element = post_soup.find(
        'span', {'class': 'tm-article-comments-counter-link__value'})
    if comments_count_element is None:
        return 0
    comments_count = re.sub(r'[^\d]+', '', comments_count_element.text)
    if comments_count == '':
        return 0
    return int(comments_count)


def extract_watch_count(post_soup: BeautifulSoup) -> int:
    """
    Extract post watch count.

    Args:
        post_soup: Post html tree as BeautifulSoup data structure.
    """
    watch_count = post_soup.find('span', {
        'class': 'tm-icon-counter__value'
    }).text
    is_thousands = 'K' in watch_count
    is_millions = 'M' in watch_count
    is_floating = '.' in watch_count
    watch_count = re.sub(r'[KM\.]', '', watch_count)
    watch_count = int(watch_count)
    if is_thousands:
        watch_count *= 1000
    if is_millions:
        watch_count *= 1000000
    if is_floating:
        watch_count /= 10
    return int(watch_count)


def extract_content(post_soup: BeautifulSoup) -> str:
    """
    Extract post content.

    Args:
        post_soup: Post html tree as BeautifulSoup data structure.
    """
    content = post_soup.find('div', {'id': 'post-content-body'}).get_text(' ')
    content = clean_text(content)
    return content


def extract_tags(post_soup: BeautifulSoup) -> List[str]:
    """
    Extract post tags.

    Args:
        post_soup: Post html tree as BeautifulSoup data structure.
    """
    tags_and_habs_element = post_soup.findAll(
        'div',
        {'class': 'tm-separated-list'},
    )

    for element in tags_and_habs_element:
        if element.span.get_text(strip=True) == 'Теги:':
            tags_elements = element.find('ul')
            tags = [
                tag.get_text(strip=True) for tag in tags_elements.findAll('li')
            ]
            return tags

    return []


def extract_habs(post_soup: BeautifulSoup) -> List[str]:
    """
    Extract post habs.

    Args:
        post_soup: Post html tree as BeautifulSoup data structure.
    """
    tags_and_habs_element = post_soup.findAll(
        'div',
        {'class': 'tm-separated-list'},
    )

    for element in tags_and_habs_element:
        if element.span.get_text(strip=True) == 'Хабы:':
            habs_elements = element.find('ul')
            habs = [
                hab.get_text(strip=True) for hab in habs_elements.findAll('li')
            ]
            return habs

    return []


def extract_user_data(post_soup: BeautifulSoup) -> Dict:
    """
    Doc
    """
    username = post_soup.find('a', {'class': 'tm-user-card__nickname'})
    if username is None:
        return {}
    url = username['href']
    karma = post_soup.find('div', {'class': 'tm-karma__votes'}).text
    rating = post_soup.find('div', {'class': 'tm-rating__counter'}).text
    return {
        'url': f'https://habr.com{url}',
        'username': username.text.strip(),
        'karma': int(karma),
        'rating': float(rating),
    }


def extract_post_data(file_path: str) -> Dict:
    """
    Extract post data.

    Args:
        file_path:

    Returns:
        Dictionary of extracted post data.
    """
    post_id = Path(file_path).stem

    with open(file_path, encoding='utf-8') as file_:
        post_soup = BeautifulSoup(
            markup=file_,
            features='lxml',
        )
        filter_post_html(post_soup)
        return {
            'id': post_id,
            'url': f'https://habr.com/ru/post/{post_id}/',
            'title': extract_title(post_soup),
            'datetime': extract_datetime(post_soup),
            'rating': extract_rating(post_soup),
            'bookmarksCount': extract_bookmarks_count(post_soup),
            'watchCount': extract_watch_count(post_soup),
            'commentsCount': extract_comments_count(post_soup),
            'content': extract_content(post_soup),
            'tags': extract_tags(post_soup),
            'habs': extract_habs(post_soup),
            'user': extract_user_data(post_soup),
        }


def extract_posts_data(path_src: str = 'data/unprocessed_posts',
                       path_dest: str = 'data/processed_posts') -> None:
    """
    Doc
    """
    if not os.path.exists(path_dest):
        os.makedirs(path_dest)

    for file_ in tqdm(os.listdir(path_src)):
        if file_.endswith('.html'):
            post = extract_post_data(f'{path_src}/{file_}')

            if not validate_post(post):
                continue

            post_id = post['id']
            with open(f'{path_dest}/{post_id}.json', 'w+',
                      encoding='utf-8') as file_p:
                json.dump(
                    obj=post,
                    fp=file_p,
                    sort_keys=True,
                    indent=4,
                    ensure_ascii=False,
                )
