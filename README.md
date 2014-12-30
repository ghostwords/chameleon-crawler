# Chameleon Crawler

Browser automation for [Chameleon](https://github.com/ghostwords/chameleon).


## Setup

Install Chromium, chromedriver, python3, xvfb, and then pip and virtualenvwrapper.

For example, on Ubuntu:
```
sudo apt-get install chromium-browser chromium-chromedriver python3 xvfb
sudo easy_install pip
sudo pip install virtualenvwrapper
```

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

Run `npm run dist` in Chameleon's checkout to produce a CRX build. Place the CRX build in chameleon-crawler's checkout. Run `run.sh` to perform a crawl.


## Roadmap

1. Save results to SQLite.
2. Compile list of URLs.
3. Crawl URLs, manually analyze results to flag fingerprinters.
4. Tweak the heuristic to minimize false negatives/positives.


## Code license

Mozilla Public License Version 2.0
