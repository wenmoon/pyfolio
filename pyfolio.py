#!/usr/bin/env python
import requests
import prettytable
import sys
import argparse
import json

from common import api
from common import model

def is_bitcoin(symbol):
    return symbol.lower() == 'btc'


def build_table(currency, sort_by, decimals, reverse, tokens):
    # table headers
    headers = {
        'rank': 'Rank #',
        'coin': 'Coin/token',
        'amount': 'Amount',
        'price': 'Price (%s)' % currency.upper(),
        'value': 'Value (%s)' % currency.upper(),
        'pct': '% 1h',
        'pct_day': '% day',
        'pct_week': '% week',
    }
    
    # table instance
    table = prettytable.PrettyTable()
    table.field_names = [
        headers['rank'], 
        headers['coin'], 
        headers['amount'], 
        headers['price'],
        headers['value'], 
        headers['pct'], 
        headers['pct_day'], 
        headers['pct_week']
    ]
    table.align[headers['rank']]  = 'r'
    table.align[headers['coin']]  = 'l'
    table.align[headers['amount']]  = 'r'
    table.align[headers['price']] = 'r'
    table.align[headers['value']] = 'r'
    table.align[headers['pct']] = 'r'
    table.align[headers['pct_day']] = 'r'
    table.align[headers['pct_week']] = 'r'
    table.sortby = headers[sort_by]
    table.float_format = '.%s' % decimals
    table.reversesort = not reverse
    
    # build table
    def token_table_row(token):
        if is_bitcoin(token.symbol):
            return [ 
                token.rank,
                token.name_str,
                token.balance,
                token.price_btc,
                token.value_btc,
                token.percent_change_1h,
                token.percent_change_24h,
                token.percent_change_7d
            ]
        else:
            return [
                token.rank,
                token.name_str,
                token.balance,
                token.price,
                token.value,
                token.percent_change_1h,
                token.percent_change_24h,
                token.percent_change_7d
            ]
    for token in tokens:
        table.add_row(token_table_row(token))

    return table


# Main application entry point
def main():
    sort_by = ['value', 'price', 'amount', 'coin', 'rank', 'pct', 'pct_day', 'pct_week']
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--sort-by', help="Sort by: %s" % ', '.join(sorted(sort_by)), default='value')
    parser.add_argument('-r', '--reverse', help="Reverse sort, by lowest value first", action='store_true', default=False)
    parser.add_argument('-d', '--decimals', help="Decimals for USD values", default=2)
    parser.add_argument('-c', '--currency', help="Currency to use (default: USD)", default='USD')
    parser.add_argument('portfolio', help="Portfolio file (in JSON)", action='store', metavar='PORTFOLIO')
    args = parser.parse_args()

    # Require portfolio file
    if not args.portfolio:
        parser.print_help()
        return False

    # BTC uses 8 decimals
    if is_bitcoin(args.currency):
        args.decimals = 8

    # Parse portfolio config, and fetch remote portfolio data
    with open(args.portfolio, 'r') as file:
        portfolio_config = json.load(file)
    portfolio = api.get_portfolio(portfolio_config, args.currency.lower())
    mcap = api.get_mcap()

    # Build the table
    table = build_table(args.currency, args.sort_by, args.decimals, args.reverse, portfolio.tokens)

    # Print output    
    print('Total mcap: $%d, 24h volume: %d' % (mcap.mcap_usd, mcap.volume_usd_24h))
    print(table)
    print('')
    if not is_bitcoin(args.currency):
        print('Total %s: %.4f' % (args.currency.upper(), portfolio.value))
    print('Total BTC: %.8f' % portfolio.value_btc)


if __name__ == '__main__':
    sys.exit(main())
