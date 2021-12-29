# Credits To TheNewBoston | Youtube: https://www.youtube.com/channel/UCJbPGzawDH1njbqV-D5HqKw
# Spider, Main, LinkFinder, General, Domain In One File
# This Was Orginaly 5 Files Now Everything Is In One.

import os
import queue
import threading
from urllib.parse import urlparse
from html.parser import HTMLParser
from urllib import parse
from urllib.request import urlopen
from queue import Queue

def get_domain_name(url):
    try:
        results = get_sub_dubomain_name(url).split(".")
        return results[-2] + "." + results[-1]
    except:
        return ''

def get_sub_dubomain_name(url):
    try:
        return urlparse(url).netloc
    except:
        return ''

def create_project_dir(directory):
    if not os.path.exists(directory):
        print("Creating Project " + directory)
        os.makedirs(directory)

def create_data_files(project_name, base_url):
    queue = project_name + "/queue.txt"
    crawled = project_name + "/crawled.txt"
    if not os.path.isfile(queue):
        write_file(queue, base_url)
    if not os.path.isfile(crawled):
        write_file(crawled, '')

def write_file(path, data):
    f = open(path, "w")
    f.write(data)
    f.close()

def append_to_file(path, data):
    with open(path, "a") as f:
        f.write(data + "\n")

def delete_file_contents(path):
    with open(path, "w"):
        pass

def file_to_set(file_name):
    results = set()
    with open(file_name, "rt") as f:
        for line in f:
            results.add(line.replace("\n", ""))
    return results

def set_to_file(links, file):
    delete_file_contents(file)
    for link in sorted(links):
        append_to_file(file, link)

class LinkFinder(HTMLParser):
    def error(self, message):
        pass

    def __init__(self, base_url, page_url):
        super().__init__()
        self.base_url = base_url
        self.page_url = page_url
        self.links = set()

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for attribute, value in attrs:
                if attribute == "href":
                    url = parse.urljoin(self.base_url, value)
                    self.links.add(url)
    
    def page_links(self):
        return self.links

class Spider:

    project_name = ''
    base_url = ''
    domain_name = ''
    queue_file = ''
    crawled_file = ''
    queue = set()
    crawled = set()

    def __init__(self, project_name, base_url, domain_name):
        Spider.project_name = project_name
        Spider.base_url = base_url
        Spider.domain_name = domain_name
        Spider.queue_file = Spider.project_name + "/queue.txt"
        Spider.crawled_file = Spider.project_name + "/crawled.txt"
        self.boot()
        self.crawl_page("First Bot", Spider.base_url)
    
    @staticmethod
    def boot():
        create_project_dir(Spider.project_name)
        create_data_files(Spider.project_name, Spider.base_url)
        Spider.queue = file_to_set(Spider.queue_file)
        Spider.crawled = file_to_set(Spider.crawled_file)

    @staticmethod
    def crawl_page(thread_name, page_url):
        if page_url not in Spider.crawled:
            print(thread_name + " Crawling " + page_url)
            print("[Queue] " + str(len(Spider.queue)) + " | [Crawled]  " + str(len(Spider.crawled)))
            Spider.add_links_to_queue(Spider.gather_links(page_url))
            Spider.queue.remove(page_url)
            Spider.crawled.add(page_url)
            Spider.update_files()

    @staticmethod
    def gather_links(page_url):
        html_string = ''
        try:
            response = urlopen(page_url)
            if response.getheader("Content-Type") == "text/html":
                html_bytes = response.read()
                html_string = html_bytes.decode("utf-8")
            finder = LinkFinder(Spider.base_url, page_url)
            finder.feed(html_string)
        except:
            print("Error: Cannot Crawl Page ")
            return set()
        return finder.page_links()
    
    @staticmethod
    def add_links_to_queue(links):
        for url in links:
            if url in Spider.queue:
                continue
            if url in Spider.crawled:
                continue
            if Spider.domain_name not in url:
                continue
            Spider.queue.add(url)

    @staticmethod
    def update_files():
        set_to_file(Spider.queue, Spider.queue_file)
        set_to_file(Spider.crawled, Spider.crawled_file )

def create_workers():
    for _ in range(NUMBER_THEREADS):
        t = threading.Thread(target=work)
        t.daemon = True
        t.start()

def work():
    while True:
        url = queue.get()
        Spider.crawl_page(threading.current_thread().name, url)
        queue.task_done()

def create_jobs():
    for link in file_to_set(QUEUE_FILE):
        queue.put(link)
    queue.join()
    crawl()

def crawl():
    queued_links = file_to_set(QUEUE_FILE)
    if len(queued_links) > 0:
        print(str(len(queued_links)) + " Links In Queue")
        create_jobs()

ProjectName = input("Project Name: ")
Homepage = input("Where Does The Bot Start Crawling? (Use A URL) ")

PROJECT_NAME = ProjectName
HOMEPAGE = Homepage
DOMAIN_NAME = get_domain_name(HOMEPAGE)
QUEUE_FILE = PROJECT_NAME + "/queue.txt"
CRAWLED_FILE = PROJECT_NAME + "/crawled.txt"
NUMBER_THEREADS = 3
queue = Queue()
Spider(PROJECT_NAME, HOMEPAGE, DOMAIN_NAME)

create_workers()
crawl()