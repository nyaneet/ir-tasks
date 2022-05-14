"""
Script to run the data extracting from downloaded posts
"""
import argparse

from task_1 import extracter

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--src',
        type=str,
        default='data/unprocessed_posts',
        help=('directory where unprocessed posts are stored, default data/'
              'unprocessed_posts'),
    )
    parser.add_argument(
        '--dest',
        type=str,
        default='data/processed_posts',
        help=('directory where processed posts will be saved, default data/'
              'unprocessed_posts'),
    )
    
    args = parser.parse_args()

    print('Data extracting started.')
    extracter.extract_posts_data(
        path_src=args.src,
        path_dest=args.dest,
    )
    print('Done.')
