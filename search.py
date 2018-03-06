#!/usr/bin/env python
import sys
import argparse

from hodlcore import api

# Main application entry point
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('token', help="The token to search for")
    parser.add_argument('--limit', metavar='num_results', help="Limit maximum search results", default=10)
    args = parser.parse_args()

    if not args.token:
        parser.print_help()
        return False

    tokens = api.search_tokens(args.token, args.limit)
    num_tokens = len(tokens)
    if num_tokens == 0:
        print("Search returned no results.")
    elif num_tokens == 1:
        token = tokens[0]
        print('Search result: {}, id={}'.format(token.name, token.id))
    else:
        print('Search returned {} results:'.format(num_tokens))
        for token in tokens:
            print('\t - {}, id={}'.format(token.name, token.id))

if __name__ == '__main__':
    sys.exit(main())
