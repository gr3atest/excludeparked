# excludeparked.py

A lightweight Python 3 script that filters out parked HTTP domains from a list of domains. Useful when pulling a list of domains from a reverse WHOIS lookup service (from a tool such as [WHOXY](https://www.whoxy.com/reverse-whois/)).

This was tested on a list of 100k parked domains but it's subject to improvement as this tool is intended to be a rough method of filtering down thousands of domains in the recon phase of a pentest. If you'd like to improve the parked domain pattern matching regex, please create a pull request or create an issue and I'll get to it ASAP :)

![example](https://user-images.githubusercontent.com/5277742/136683862-973cdb0a-8481-4a78-a3d2-70a18023b314.png)

## Install

Clone and install the repo:

```bash
git pull git@github.com:gr3atest/excludeparked.git
cd excludeparked
pip install -r requirements.txt
python3 ./excludeparked.py -h
```

This script has been developed to run in Python 3. There is a little more (almost trivial) amount of work required to
make it backwards compatible with Python 2. This change will come soon.

## Usage

Short Form    | Long Form     | Description
------------- | ------------- |-------------
-f            | --file        | The source file containing a list domains/urls to scan
-u            | --url         | The single domain or http url to scan
-v            | --verbose     | Enable verbose mode and show error messages
-t            | --threads     | Number of threads to use. Default 10
-k            | --allow-insecure | Allow insecure server connections when using SSL
&nbsp;            | --timeout      | Maximum timeout of each request. Default 25 seconds.
-a            | --accept-new-domain | Show urls that redirect to new domain name (i.e., googleparkedurl.com -> google.com). Disable this if your target redirects all parked host to a single domain. (Default true)
-h            | --help        | show the help message and exit

![usage](https://user-images.githubusercontent.com/5277742/136683803-5d3944a0-4022-4d54-aaa3-40bc1bbaae4f.png)

## Docker

Build the docker image:

```bash
docker build . -t excludeparked
```

Run the image:

```bash
docker run excludeparked --help
```
