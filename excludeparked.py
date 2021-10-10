#!/usr/bin/env python3

import argparse
import math
import re
import threading

import requests

try:
    import requests.packages.urllib3

    requests.packages.urllib3.disable_warnings()
except:
    pass

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

BLUE = '\033[94m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BOLD = '\033[1m'
ENDC = '\033[0m'

MIN_THREADING_INPUT_SIZE = 20

lock = threading.Semaphore(value=1)


def thread_safe_print(message):
    lock.acquire()
    print(message + ENDC)
    lock.release()


def is_content_parked(content):
    return any(re.findall(r'buy this domain|parked free|godaddy|is for sale'
                          r'|domain parking|renew now|this domain|namecheap|buy now for'
                          r'|hugedomains|is owned and listed by|sav.com|searchvity.com'
                          r'|domain for sale|register4less|aplus.net|related searches'
                          r'|related links|search ads|domain expert|united domains'
                          r'|domian name has been registered|this domain may be for sale'
                          r'|domain name is available for sale|premium domain'
                          r'|this domain name|this domain has expired|domainpage.io'
                          r'|sedoparking.com|parking-lander', content, re.IGNORECASE))


# Follow valid redirects and examine destination content
def follow_url(url, timeout, allow_insecure, accept_new_domain, debug):
    try:
        res = requests.get(url, headers={
            'User-Agent': 'Mozilla/5.0 (Mobile; ALCATELOneTouch4012X; rv:18.1) Gecko/18.1 Firefox/18.1',
            'Accept-Encoding': 'gzip',
            'Accept-Language': 'en-US',
            'Accept': 'text/html,application/xml,application/xhtml+xml',
        }, allow_redirects=False, timeout=timeout, verify=(not allow_insecure))
    except Exception as e:
        if debug:
            thread_safe_print(RED + ' error loading url: ' + url + ' ' + str(e) + ENDC)
        return None

    if res.is_redirect:
        location = res.headers['location']
        target_domain = urlparse(url).netloc
        redirect_domain = urlparse(location).netloc
        if target_domain == redirect_domain or 'www.' + target_domain == redirect_domain or accept_new_domain:
            return follow_url(location, timeout, allow_insecure, accept_new_domain, debug)
    else:
        return res.text


def handle_urls(urls, accept_new_domain, allow_insecure, timeout, debug):
    for url in urls:
        # The input may or may not already contain a scheme, add to ensure url beyond this point always contains schema
        url = url if url.startswith('http') else 'http://' + url

        text_response = follow_url(url, timeout, allow_insecure, accept_new_domain, debug)

        if text_response is None:
            if debug:
                thread_safe_print(RED + url + ENDC)
        elif not is_content_parked(text_response):
            thread_safe_print(GREEN + url + ENDC)
        elif debug:
            thread_safe_print(YELLOW + url + ' is parked' + ENDC)


def main():
    parser = argparse.ArgumentParser(description='Test description')
    parser.add_argument('-f', '--file', dest='source_file',
                        help='The source file containing a list domains/urls to scan')
    parser.add_argument('-u', '--url', dest='source_url',
                        help='The single domain or http url to scan')
    parser.add_argument('-t', '--threads', dest='thread_count', type=int, default=10,
                        help='Number of threads to use. Default 10')
    parser.add_argument('-k', '--insecure', dest='allow_insecure', action='store_true',
                        help='Allow insecure server connections when using SSL')
    parser.add_argument('-v', '--verbose', dest='debug', action='store_true',
                        help='Enable verbose mode and show error messages')
    parser.add_argument('-a', '--accept-new-domain', dest='accept_new_domain', type=bool,
                        default=True,
                        help='Show urls that redirect to new domain name (i.e., googleparkedurl.com -> google.com).'
                             'Disable this if your target redirects all parked host to a single domain. (Default true)')
    parser.add_argument('--timeout', dest='timeout', type=int, default=25,
                        help='Maximum timeout of each request. Default 25 seconds.')

    args = parser.parse_args()

    if args.source_url is None and args.source_file is None:
        parser.print_help()
        print('\nerror: please provide either a url or file containing urls to scan')
        exit(1)

    if args.thread_count < 1:
        parser.print_help()
        print('\nerror: invalid thread count')
        exit(2)

    if args.source_file is not None:
        with open(args.source_file, 'r') as target_file:
            urls = target_file.read().splitlines()
    else:
        urls = [args.source_url]

    if len(urls) < MIN_THREADING_INPUT_SIZE:
        handle_urls(urls, args.accept_new_domain, args.allow_insecure, args.timeout, args.debug)
    else:
        # Split array into smaller chunks for threads
        thread_count = max(len(urls), args.thread_count)
        chunk_size = math.ceil(len(urls) / thread_count)
        chunks = [urls[i:i + chunk_size] for i in range(0, len(urls), chunk_size)]
        threads = []

        for chunk in chunks:
            t = threading.Thread(target=handle_urls,
                                 args=(chunk, args.accept_new_domain, args.allow_insecure, args.timeout, args.debug))
            threads.append(t)
            t.start()

        [t.join() for t in threads]


if __name__ == '__main__':
    main()
