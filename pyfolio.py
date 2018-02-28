#!/usr/bin/env python
import requests
import prettytable
import sys
import argparse
import json


def is_bitcoin(token_id):
    return token_id.lower() == 'btc'


def build_table(percents, currency, sort_by, decimals, reverse, portfolio):
    # table headers
    headers = {
        'rank': 'Rank #',
        'coin': 'Coin/token',
        'percents': 'Percents',
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
        headers['percents'], 
        headers['amount'], 
        headers['price'],
        headers['value'], 
        headers['pct'], 
        headers['pct_day'], 
        headers['pct_week']
    ]

    if percents:
        # remove amount and value
        table.field_names.remove(headers['amount'])
        table.field_names.remove(headers['value'])
    else:
        table.align[headers['amount']]  = 'r'
        table.align[headers['value']] = 'r'

    table.align[headers['rank']]  = 'r'
    table.align[headers['coin']]  = 'l'
    table.align[headers['percents']]  = 'r'
    table.align[headers['price']] = 'r'
    table.align[headers['pct']] = 'r'
    table.align[headers['pct_day']] = 'r'
    table.align[headers['pct_week']] = 'r'
    table.sortby = headers[sort_by]
    table.float_format = '.%s' % decimals
    table.reversesort = not reverse
    
    # build table
    for token in portfolio.tokens:
        row = token.as_row()

        # add percents
        row.insert(2, token.value * 100 / portfolio.value)

        # remove amount/value from rows
        if percents:
            del row[3]
            del row[4]
        table.add_row(row)

    return table


class API(object):
    endpoint_token = 'https://api.coinmarketcap.com/v1/ticker/%s/?convert=%s'
    endpoint_mcap = 'https://api.coinmarketcap.com/v1/global/'

    def get_mcap(self):
        return requests.get(self.endpoint_mcap).json()['total_market_cap_usd']

    def get_portfolio(self, portfolio_config, currency): 
        tokens = []
        # get stats for each coin
        for item in portfolio_config:
            name = item[0]
            balance = item[1]
            r_token = requests.get(self.endpoint_token % (name, currency)).json()[0]
            name = r_token['name']
            symbol = r_token['symbol']
            rank = r_token['rank']
            price = float(r_token['price_%s' % currency])
            price_btc = float(r_token['price_btc'])
            pct_1h = float(r_token['percent_change_1h'])
            pct_24h = float(r_token['percent_change_24h'])
            pct_7d = float(r_token['percent_change_7d'])
            token = Token(name, symbol, price, price_btc, balance, rank, pct_1h, pct_24h, pct_7d)
            tokens.append(token)
        return Portfolio(tokens)


class Token(object):
    def __init__(self, name, symbol, price, price_btc, balance, rank, pct_1h, pct_24h, pct_7d):
        self.name = name
        self.symbol = symbol
        self.name_str = '%s (%s)' % (name, symbol)
        self.price = price
        self.price_btc = price_btc
        self.balance = balance
        self.value = price * balance
        self.value_btc = price_btc * balance
        self.rank = rank
        self.pct_1h = pct_1h
        self.pct_24h = pct_24h
        self.pct_7d = pct_7d

    def as_row(self):
        return [self.rank, self.name_str, self.balance, self.price, self.value, self.pct_1h, self.pct_24h, self.pct_7d]


class Portfolio(object):
    def __init__(self, tokens):
        self.tokens = tokens
        self.value = 0
        self.value_btc = 0
        for token in tokens:
            self.value += token.value
            self.value_btc += token.value_btc


# Main application entry point
def main():
    sort_by = ['percents', 'value', 'price', 'amount', 'coin', 'rank', 'pct', 'pct_day', 'pct_week']
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

    # API
    api = API()

    # Parse portfolio config, and fetch remote portfolio data
    with open(args.portfolio, 'r') as file:
        portfolio_config = json.load(file)
    portfolio = api.get_portfolio(portfolio_config, args.currency.lower())

    # Replace default sort_by if -p/--percents
    if args.sort_by == 'value' and args.percents:
        args.sort_by = 'percents'

    # Build the table
    table = build_table(
        args.percents, args.currency, args.sort_by, args.decimals, args.reverse, portfolio
    )

    # Print output
    print('Total mcap: $%d' % api.get_mcap())
    print(table)
    print('')
    if not is_bitcoin(args.currency):
        print('Total %s: %.4f' % (args.currency.upper(), portfolio.value))
    print('Total BTC: %.8f' % portfolio.value_btc)


if __name__ == '__main__':
    sys.exit(main())
