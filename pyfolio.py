#!/usr/bin/env python
import requests
import prettytable
import sys
import argparse
import json

# cmc coin api
cmc_api = 'https://api.coinmarketcap.com/v1/ticker/%s/?convert=%s'

def main():

    sort_by = ['value', 'price', 'amount', 'coin', 'rank', 'pct', 'pct_day', 'pct_week']
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--sort-by', help="sort by: %s" % ', '.join(sorted(sort_by)), default='value')
    parser.add_argument('-r', '--reverse', help="reverse sort, by lowest value first", action='store_true', default=False)
    parser.add_argument('-d', '--decimals', help="decimals for USD values", default=2)
    parser.add_argument('-c', '--currency', help="currency to use (default: USD)", default='USD')
    parser.add_argument('portfolio', help="portfolio file (in JSON)", action='store', metavar='PORTFOLIO')
    args = parser.parse_args()

    headers = {
        'rank': 'Rank #',
        'coin': 'Coin/token',
        'amount': 'Amount',
        'price': 'Price (%s)' % args.currency.upper(),
        'value': 'Value (%s)' % args.currency.upper(),
        'pct': '% 1h',
        'pct_day': '% day',
        'pct_week': '% week',
    }
    
    # portfolio file
    if not args.portfolio:
        parser.print_help()
        return False

    # check sort_by
    if not args.sort_by in sort_by:
        print('invalid sort by: %s' % args.sort_by)
        parser.print_help()
        return False

    # if btc, use 8 decimals
    if args.currency.lower() == 'btc':
        args.decimals = 8

    # portfolio file should be json
    with open(args.portfolio, 'r') as f:
        portfolio = json.load(f)
   
    # get the total mcap also
    mcap = requests.get('https://api.coinmarketcap.com/v1/global/').json()['total_market_cap_usd']

    # prettytable instance
    table = prettytable.PrettyTable()

    table.field_names = [
        headers['rank'], headers['coin'], headers['amount'], headers['price'],
        headers['value'], headers['pct'], headers['pct_day'], headers['pct_week']
    ]
    table.align[headers['rank']]  = 'r'
    table.align[headers['coin']]  = 'l'
    table.align[headers['amount']]  = 'r'
    table.align[headers['price']] = 'r'
    table.align[headers['value']] = 'r'
    table.align[headers['pct']] = 'r'
    table.align[headers['pct_day']] = 'r'
    table.align[headers['pct_week']] = 'r'
    table.sortby = headers[args.sort_by]
    table.float_format = '.%s' % args.decimals
    table.reversesort = not args.reverse

    total = 0
    total_btc = 0
    # get stats for each coin
    for coin in portfolio:
        r = requests.get(cmc_api % (coin[0], args.currency.upper()))
        rank = r.json()[0]['rank']
        name_str = '%s (%s)' % (r.json()[0]['name'], r.json()[0]['symbol'])
        price_str = 'price_%s' % args.currency.lower()
        price = float(r.json()[0][price_str])
        price_btc = float(r.json()[0]['price_btc'])
        value = price * coin[1]
        value_btc = price_btc * coin[1]
        total += value
        total_btc += value_btc
        pct_1h = float(r.json()[0]['percent_change_1h'])
        pct_24h = float(r.json()[0]['percent_change_24h'])
        pct_7d = float(r.json()[0]['percent_change_7d'])
        if args.currency.lower() == 'btc':
            table.add_row([rank, name_str, coin[1], price_btc, value_btc, pct_1h, pct_24h, pct_7d])
        else:
            table.add_row([rank, name_str, coin[1], price, value, pct_1h, pct_24h, pct_7d])

    print('Total Market Cap: $%d' % mcap)
    print(table)
    print('')
    if args.currency.lower() == 'btc':
        print('Total value (%s): %.8f' % (args.currency.upper(), total))
    else:
        print('Total value (%s): %.4f' % (args.currency.upper(), total))
        print('Total value (BTC): B%.8f' % total_btc)


if __name__ == '__main__':
    sys.exit(main())
