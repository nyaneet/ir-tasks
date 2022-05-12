"""
Script to run the crawler
"""
import argparse

from task_1 import crawler

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--first',
        type=int,
        required=True,
        help='ID of the first post to be crawled',
    )
    parser.add_argument(
        '--last',
        type=int,
        required=True,
        help='ID of the last post to be crawled',
    )
    parser.add_argument(
        '-p',
        '--processes_number',
        type=int,
        default=1,
        help=('The maximum number of processes that will be used, '
              'recommended <=8, default 1'),
    )
    parser.add_argument(
        '--path',
        type=str,
        default='data/unprocessed_posts',
        help=('Directory where posts are downloaded, default data/'
              'unprocessed_posts'),
    )
    parser.add_argument(
        '-D',
        '--debug',
        action='store_true',
        help='Setting the log level to DEBUG, default INFO',
    )

    args = parser.parse_args()

    if (args.first < 0 or args.last < 0):
        raise ValueError('Post id must be positive')
    if args.first > args.last:
        raise ValueError('Last id must be greater than first id')

    crawler.crawl(first_id=args.first,
                  last_id=args.last,
                  max_workers=args.processes_number,
                  path=args.path,
                  debug=args.debug)
