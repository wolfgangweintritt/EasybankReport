#!/usr/bin/python3
from datetime import datetime
import seleniumParser
import drawGraphs
import argparse


# TODO doc, profiling, type hinting
# TODO year report start @ XXX => so save all transactions and calculate the money at the beginning of the year
if __name__ == '__main__':
    # set up the argument parser
    parser = argparse.ArgumentParser(description='Get transactions from easybank.at via selenium, save them to csv.')
    parser.add_argument('--silent', '-s', action='store_true', default=False,
                        help='Show no logging output.')
    parser.add_argument('--headless', '-hl', action='store_true', default=False,
                        help='Use headless browser (no browser window shown).')
    parser.add_argument('--year', '-y', type=int,
                        help='Only create graphs for a certain year.')
    parser.add_argument('--skip-first-transaction', '-f', action='store_true', default=False,
                        help='Skips the first transaction')

    # do the argument parsing and initialize options
    args = parser.parse_args()

    # 1. get all the transactions
    plotFolder = datetime.now().strftime('output%Y%m%d-%H%M%S')
    seleniumParser.parseTransactions(args.silent, args.headless, plotFolder)

    # 2. draw the graphs
    drawGraphs.drawAllGraphs(plotFolder, args.skip_first_transaction)
    if args.year:
        drawGraphs.drawAllGraphs(plotFolder, False, args.year) # do not skip the first transaction when just looking at the year
