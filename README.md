# Chameleon Crawler

Browser automation for [Chameleon](https://github.com/ghostwords/chameleon).


## Setup

- Install Chromium, chromedriver, python3 and xvfb. On Ubuntu:
```
sudo apt-get install chromium-browser chromium-chromedriver python3 xvfb
```

- Install the project's Python dependencies (documented in [requirements.txt](requirements.txt)). You might do this with `virtualenv` and `pip`, or maybe Docker. Note this is a Python 3 project.

- Make sure `chromedriver` is in your $PATH. It's not on Ubuntu, so we have to fix that:
```
sudo ln -s /usr/lib/chromium-browser/chromedriver /usr/local/bin/chromedriver
```

- If using Ubuntu 14.04, [fix chromedriver's shared libraries error](http://stackoverflow.com/questions/25695299/chromedriver-on-ubuntu-14-04-error-while-loading-shared-libraries-libui-base):
```
echo "/usr/lib/chromium-browser/libs" | sudo tee --append /etc/ld.so.conf.d/chrome_lib.conf >/dev/null
sudo ldconfig
```

- Finally, generate a Chameleon CRX package [by following development setup steps 1 and 4 in Chameleon's checkout](https://github.com/ghostwords/chameleon#development-setup).


## Usage

Run `./crawl.py /path/to/chameleon.crx` to perform a crawl, or `./crawl.py -h` to see the optional arguments:

```
usage: crawl.py [-h] [--headless | --no-headless] [-n {1,2,3,4,5,6,7,8}] [-q]
                [-t SECONDS] [--urls URL_FILE_PATH]
                CHAMELEON_CRX_FILE_PATH

positional arguments:
  CHAMELEON_CRX_FILE_PATH
                        path to Chameleon CRX package

optional arguments:
  -h, --help            show this help message and exit
  --headless            use a virtual display (default)
  --no-headless
  -n {1,2,3,4,5,6,7,8}  how many browsers to use in parallel (default: 4)
  -q, --quiet           turn off standard output
  -t SECONDS, --timeout SECONDS
                        how many seconds to wait for pages to finish loading
                        before timing out (default: 20)
  --urls URL_FILE_PATH  path to URL list file (default: urls.txt)
```

Run `./view.py` and visit the displayed URL to review crawl results.


## Roadmap

1. Crawl Alexa Global Top 1,000,000 Sites: http://s3.amazonaws.com/alexa-static/top-1m.csv.zip
2. Analyze results:
	- Discover fingerprinters
	- Confirm detection of known fingerprinters
3. Tweak the heuristic to minimize false negatives/positives.
4. Create minisite to chart (the growth of?) fingerprinting across the Web.


## Code license

Mozilla Public License Version 2.0
