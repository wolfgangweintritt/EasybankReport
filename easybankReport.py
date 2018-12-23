#!/usr/bin/python3
from datetime import datetime
import csvParser
import drawGraphs
import argparse

# TODO doc, type hinting
if __name__ == '__main__':
    # set up the argument parser
    parser = argparse.ArgumentParser(description='Gets transactions from csv file, and creates plots.')
    parser.add_argument('csv_file_path', type=str, help='Path to the CSV file with the transactions')
    parser.add_argument('--silent', '-s', action='store_true', default=False,
                        help='Show no logging output.')
    parser.add_argument('--year', '-y', type=int,
                        help='Only create graphs for a certain year.')
    parser.add_argument('--skip-first-transaction', '-f', action='store_true', default=False,
                        help='Skips the first transaction')

    # do the argument parsing and initialize options
    args = parser.parse_args()

    # 1. get all the transactions
    csvData = csvParser.parseTransactions(args.silent, args.csv_file_path)

    # 2. draw the graphs
    plotFolder = datetime.now().strftime('output%Y%m%d-%H%M%S')
    drawGraphs.drawAllGraphs(csvData, plotFolder, args.skip_first_transaction)
    if args.year:
        drawGraphs.drawAllGraphs(csvData, plotFolder, True, args.year)
