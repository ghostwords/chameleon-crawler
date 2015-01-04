# Chameleon Crawler

Browser automation for [Chameleon](https://github.com/ghostwords/chameleon).


## Setup

Install Chromium, chromedriver, python3 and xvfb.

On Ubuntu:
```
sudo apt-get install chromium-browser chromium-chromedriver python3 xvfb
```

Then install the project's Python dependencies (documented in [requirements.txt](requirements.txt)). You might do this with `virtualenv` and `pip`, or maybe Docker. Note this is a Python 3 project.

Make sure `chromedriver` is in your $PATH. It's not on Ubuntu, so we have to fix that:
```
sudo ln -s /usr/lib/chromium-browser/chromedriver /usr/local/bin/chromedriver
```

If using Ubuntu 14.04, [fix chromedriver's shared libraries error](http://stackoverflow.com/questions/25695299/chromedriver-on-ubuntu-14-04-error-while-loading-shared-libraries-libui-base):
```
echo "/usr/lib/chromium-browser/libs" | sudo tee --append /etc/ld.so.conf.d/chrome_lib.conf >/dev/null
sudo ldconfig
```


## Usage

Run `npm run dist` in Chameleon's checkout to produce a CRX package.

Run `./src/run.py /path/to/chameleon.crx` to perform a crawl, or `./src/run.py -h` to see all optional arguments.


## Roadmap

1. Save results to SQLite.
2. Compile list of URLs.
3. Crawl URLs, manually analyze results to flag fingerprinters.
4. Tweak the heuristic to minimize false negatives/positives.


## Code license

Mozilla Public License Version 2.0
