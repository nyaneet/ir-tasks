# IR-Tasks-2022
Tasks in the course of information retrieval.

# Task 1
Collecting and cleaning the data from the [Habr](https://habr.com/ru/all/), Russian collaborative blog about IT.

## Installation and use

Install the required packages with pip
```
pip install -r requirements.txt
```
### Data collecting
To start collecting data use the script `crawl.py`
```console
$ python3 ./crawl.py -h
usage: crawl.py [-h] --first FIRST --last LAST [-p PROCESSES_NUMBER] [--path PATH] [-D]

optional arguments:
  -h, --help            show this help message and exit
  --first FIRST         ID of the first post to be crawled
  --last LAST           ID of the last post to be crawled
  -p PROCESSES_NUMBER, --processes_number PROCESSES_NUMBER
                        the maximum number of processes that will be used, recommended
                        <=8, default 1
  --path PATH           directory where posts are downloaded, default
                        data/unprocessed_posts
  -D, --debug           setting the log level to DEBUG, default INFO

```
For example, to download about 190.000 posts and save the post html files in the `./data/unprocessed_posts/` directory
```
python3 crawl.py --first 1 --last 400000 -p 8
```
### Data cleaning
To cleaning the data use the script `extract.py`
```console
$ python3 ./extract.py -h
usage: extract.py [-h] [--src SRC] [--dest DEST]

optional arguments:
  -h, --help   show this help message and exit
  --src SRC    directory where unprocessed posts are stored, default data/unprocessed_posts
  --dest DEST  directory where processed posts will be saved, default data/processed_posts

```
For example, to process downloaded html posts and save them as json files in the `./data/processed_posts` directory
```
python3 extract.py
```
