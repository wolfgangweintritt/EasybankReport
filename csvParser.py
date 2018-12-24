#!/usr/bin/env python3
# coding=utf-8
"""Get transactions from easybank csv and save them to csv data objects."""
import csv
import datetime
import re
from typing import List, Tuple

from transaction import Transaction

#### GLOBALS ####
ibanRegex = '[a-zA-Z]{2}[0-9]{2}[a-zA-Z0-9]{4}[0-9]{7}([a-zA-Z0-9]?){0,16}'
textRegex = []
knownIbans = []
silent = False


#### MAIN ####
def parseTransactions(staySilent: bool, csvFilepath: str) -> List[Transaction]:
    global silent
    global knownIbans
    global textRegex
    silent = staySilent

    knownIbans = loadCsvIntoTupleList('data/ibans.csv')
    textRegex = loadCsvIntoTupleList('data/text.csv')

    return getTransactions(csvFilepath)


def loadCsvIntoTupleList(filename: str) -> List[Tuple[str, str]]:
    tupleList = []
    with open(filename, newline='') as csvfile:
        csvReader = csv.reader(csvfile, delimiter=',')
        for row in csvReader:
            tupleList.append((row[0], row[1]))
    return tupleList


def getTransactions(csvFilepath: str) -> List[Transaction]:
    stack = []
    with open(csvFilepath, newline='', encoding='latin-1') as csvfile:
        csvReader = csv.reader(csvfile, delimiter=';')
        for row in csvReader:
            text = row[1]
            iban = re.search(ibanRegex, text)
            iban = '' if (iban is None) else iban.group(0)
            date = datetime.datetime.strptime(row[2], "%d.%m.%Y")
            amount = row[4].replace(".", "").replace(",", ".")  # transform GER seperator style string to US seperator style number
            category = getCategory(iban, text)
            transaction = Transaction(date, iban, amount, category, text)
            stack.append(transaction)

    log("saved " + str(len(stack)) + " transactions to stack.")
    return list(reversed(stack))


def getCategory(iban: str, text: str) -> str:
    for (tCategory, tIban) in knownIbans:
        if tIban == iban:
            return tCategory

    for (tCategory, tRegex) in textRegex:
        searchResult = re.search(tRegex, text)
        if searchResult is not None:
            return tCategory
    return ''


def log(msg: str) -> None:
    if not silent:
        print(msg)
