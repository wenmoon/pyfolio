#!/usr/bin/env python
import prettytable
import sys
import argparse
import json

from hodlcore import api
from hodlcore import model
from hodlcore import stringformat

def is_bitcoin(symbol):
    return symbol.lower() == 'btc'


def build_table(percents, currency, sort_by, decimals, reverse, portfolio):
    # table headers
    headers = {
        'rank': 'Rank #',
        'coin': 'Coin/token',
        'amount': 'Amount',
        'price': 'Price ({})'.format(currency),
        'value': 'Value ({})'.format(currency),
        'volume': '24h vol',
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
        headers['value'], 
        headers['price'],
        headers['volume'], 
        headers['pct'],
        headers['pct_day'], 
        headers['pct_week']
    ]
    if percents:
        table.field_names.remove(headers['value'])
        sort_by = 'amount'
    else:
        table.align[headers['value']] = 'r'
    
    table.align[headers['rank']]  = 'r'
    table.align[headers['coin']]  = 'l'
    table.align[headers['amount']]  = 'r'
    table.align[headers['price']] = 'r'
    table.align[headers['volume']] = 'r'
    table.align[headers['pct']] = 'r'
    table.align[headers['pct_day']] = 'r'
    table.align[headers['pct_week']] = 'r'
    table.sortby = headers[sort_by]
    table.float_format = '.%s' % decimals
    table.reversesort = not reverse
    
    # build table
    def token_table_row(token, percent = -1):
        row = []
        row.append(token.rank)
        row.append(token.name_str)
        if percent > 0:
            row.append('{:.2f}%'.format(percent))
        else:
            row.append(token.balance)
            row.append(token.value)
        row.append(token.price)
        row.append(stringformat.large_number(token.volume_24h))
        row.append(stringformat.sh_color(token.percent_change_1h))
        row.append(stringformat.sh_color(token.percent_change_24h))
        row.append(stringformat.sh_color(token.percent_change_7d))
        return row

    for token in portfolio.tokens:
        if percents:
            table.add_row(token_table_row(token, token.value * 100 / portfolio.value))
        else:
            table.add_row(token_table_row(token))

    return table


# Main application entry point
def main():
    sort_by = ['percents', 'value', 'price', 'volume', 'amount', 'coin', 'rank', 'pct', 'pct_day', 'pct_week']
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--sort-by', help="sort by: %s" % ', '.join(sorted(sort_by)), default='value')
    parser.add_argument('-r', '--reverse', help="reverse sort, by lowest value first", action='store_true', default=False)
    parser.add_argument('-p', '--percents', help="show percents only (hide values)", action='store_true', default=False)
    parser.add_argument('-d', '--decimals', help="decimals for USD values", default=2)
    parser.add_argument('-c', '--currency', help="currency to use (default: USD)", default='USD')
    parser.add_argument('portfolio', help="portfolio file (in JSON)", action='store', metavar='PORTFOLIO')
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
    table = build_table(args.percents, args.currency, args.sort_by, args.decimals, args.reverse, portfolio)

    # Print output
    print('Total mcap: $%s, 24h volume: %s' % (stringformat.large_number(mcap.mcap_usd), stringformat.large_number(mcap.volume_usd_24h)))
    print(table)
    print('')
    if not is_bitcoin(args.currency):
        print('Total %s: %.4f' % (args.currency.upper(), portfolio.value))
    print('Total BTC: %.8f' % portfolio.value_btc)


if __name__ == '__main__':
    sys.exit(main())
