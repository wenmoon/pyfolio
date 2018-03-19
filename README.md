# Simple command line Crypto Portfolio tracker

## Dependencies
Required libraries are `prettytable` and `requests`, install with `easy_install` for Python 2 or `pip3` for Python 3.

The best way to run this is to use `watch`. For macOS install using `brew install watch` (if you don't have `brew` install with `/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"`).

## Configuring your portfolio
The configuration file is a simple JSON array with Dictionary pairs defining `token` and matching `balance`. The `token` is specified using the `id` found on www.coinmarketcap.com. See `p.json` as an example.

## Searching for coins
You can search for coins using `./search.py <searchstring>`, which can be a convenient way of finding the correct `id`s when configuring your portfolio.

## Running
To see your portfolio, defined in `p.json`, using USD as your base Fiat, run `$ ./hodlfolio.py -c USD p.json`.

To poll your portfolio, defined in `p.json`, every 30 seconds, using USD as your base Fiat, run `$ watch -n30 ./hodlfolio.py -c USD p.json`.
