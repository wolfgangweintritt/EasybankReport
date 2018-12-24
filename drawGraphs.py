#!/usr/bin/env python3
"""Draw Plots from csv."""
import os
import math
import datetime
from typing import List, Tuple, Dict, Any
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.dates import date2num
import matplotlib.cm as cm
import numpy as np
import enforce
from decimal import *
from transaction import Transaction

#### GLOBALS ####
dpi = 96
figsize = (1600 / dpi, 800 / dpi)
plotFolder = None


@enforce.runtime_validation
def drawAllGraphs(csvData: List[Transaction], dataFolder: str, skipFirstTransaction: bool, year: int = None) -> None:
    global transactions
    transactions = csvData

    global plotFolder
    plotFolder = dataFolder + '/plots' + ('' if year is None else str(year)) + '/'
    os.makedirs(os.path.dirname(plotFolder), exist_ok=True)

    monthlyBalance = getMonthlyBalance()
    plotMonthlyBalance(monthlyBalance)

    if year is not None:
        transactions = [t for t in transactions if t.date.year == year]
        startAmount = next(m for m in monthlyBalance if m[0].year == (year - 1) and m[0].month == 12)
        startAmount = Transaction(startAmount[0], '', startAmount[1], '', '')
        transactions = [startAmount] + transactions

        monthlyBalance = getMonthlyBalance()
        plotMonthlyBalance(monthlyBalance)

    monthlyIO = getMonthlyEarningsAndExpenses(skipFirstTransaction)
    plotMonthlyIO(monthlyIO)

    if year is None:
        categoricalIncome = getYearlyCategoricalCashflow(skipFirstTransaction, True)
        plotCategorical(categoricalIncome, True, False)

        categoricalExpenses = getYearlyCategoricalCashflow(skipFirstTransaction, False)
        plotCategorical(categoricalExpenses, False, False)
    else:
        categoricalIncome = getQuarterYearlyCategoricalCashflow(skipFirstTransaction, True)
        plotCategorical(categoricalIncome, True, True)

        categoricalExpenses = getQuarterYearlyCategoricalCashflow(skipFirstTransaction, False)
        plotCategorical(categoricalExpenses, False, True)

    printSummary(monthlyBalance, monthlyIO, categoricalIncome, categoricalExpenses)


# calculate balance at the end of each month to an array, return it
# return an array containing tuples with date and balance for each month: [('01-01-2018', 100), ('01-02-2018', 222), ...]
@enforce.runtime_validation
def getMonthlyBalance() -> List[Tuple[datetime.datetime, Decimal]]:
    monthlyBalance = []
    balance = 0
    lastTuple = None

    for transaction in transactions:
        if lastTuple is not None and lastTuple[0].month != transaction.date.month:
            monthlyBalance.append(lastTuple)
        balance += transaction.amount
        lastTuple = (transaction.date, balance)

    monthlyBalance.append(lastTuple)
    return monthlyBalance


# calculate earnings and expenses for each month, return it
# return an array with triple-arrays of date, income and expenses: [['2018-01-01', 100, 200], ['2018-02-01', 500, 222], ...]
@enforce.runtime_validation
def getMonthlyEarningsAndExpenses(skipFirstTransaction: bool) -> List[List[Any]]:
    monthlyIO = []
    io = [0, 0]
    lastDate = None
    skip = skipFirstTransaction

    for transaction in transactions:
        if skip:
            skip = False
            continue
        if lastDate is not None and lastDate.month != transaction.date.month:
            monthlyIO.append([datetime.date(lastDate.year, lastDate.month, 1)] + io)
            io = [0, 0]
        if transaction.amount > 0:
            io[0] += transaction.amount
        else:
            io[1] += transaction.amount * (-1)
        lastDate = transaction.date

    monthlyIO.append([datetime.date(lastDate.year, lastDate.month, 1)] + io)
    return monthlyIO


# return array of tuples [(2018, {'category1': 100, 'category2': 200, ...}), (2019, {}), ...]
@enforce.runtime_validation
def getYearlyCategoricalCashflow(skipFirstTransaction: bool, income: bool = True) -> List[Tuple[float, Dict]]:
    yearlyIO = []
    categoricalCashflow = {}
    lastDate = None
    skip = skipFirstTransaction

    for transaction in transactions:
        if skip:
            skip = False
            continue
        if lastDate is not None and lastDate.year != transaction.date.year:
            yearlyIO.append((float(lastDate.year), categoricalCashflow))
            categoricalCashflow = {}
        category = transaction.category if transaction.category != '' else 'Uncategorized'
        if (income and transaction.amount > 0) or (not income and transaction.amount < 0):
            if category in categoricalCashflow:
                categoricalCashflow[category] += abs(transaction.amount)
            else:
                categoricalCashflow[category] = abs(transaction.amount)
        lastDate = transaction.date

    if lastDate is not None:
        yearlyIO.append((float(lastDate.year), categoricalCashflow))
    return yearlyIO


# return array of tuples [(2018.25, {'category1': 100, 'category2': 200, ...}), (2018.50: {}), ...]
@enforce.runtime_validation
def getQuarterYearlyCategoricalCashflow(skipFirstTransaction: bool, income: bool = True) -> List[Tuple[float, Dict]]:
    yearlyIO = []
    categoricalCashflow = {}
    lastDate = None
    skip = skipFirstTransaction

    for transaction in transactions:
        if skip:
            skip = False
            continue
        if lastDate is not None and math.ceil(lastDate.month / 3) != math.ceil(transaction.date.month / 3):
            yearlyIO.append((lastDate.year + (math.ceil(lastDate.month / 3) / 4), categoricalCashflow))
            categoricalCashflow = {}
        category = transaction.category if transaction.category != '' else 'Uncategorized'
        if (income and transaction.amount > 0) or (not income and transaction.amount < 0):
            if category in categoricalCashflow:
                categoricalCashflow[category] += abs(transaction.amount)
            else:
                categoricalCashflow[category] = abs(transaction.amount)
        lastDate = transaction.date

    if lastDate is not None:
        yearlyIO.append((lastDate.year + (math.ceil(lastDate.month / 3) / 4), categoricalCashflow))
    return yearlyIO


@enforce.runtime_validation
def plotMonthlyBalance(monthlyBalance: List[Tuple[datetime.datetime, Decimal]]) -> None:
    plt.figure(figsize=figsize)
    plt.plot([x[0] for x in monthlyBalance], [x[1] for x in monthlyBalance])

    labelAxisAndSavePlot('date', 'balance', 'monthlyBalance.png')


@enforce.runtime_validation
def plotMonthlyIO(monthlyIO: List[List[Any]]) -> None:
    plt.figure(figsize=figsize)

    w = 12  # width = 12 days
    x = date2num([x[0] for x in monthlyIO])
    ax: Axes = plt.subplot(111)
    incomeBar = ax.bar(x - (w / 2), [x[1] for x in monthlyIO], width=w, color='#67a9cf', align='center', label='Income')
    expensesBar = ax.bar(x + (w / 2), [x[2] for x in monthlyIO], width=w, color='#ef8a62', align='center', label='Expenses')
    ax.xaxis_date()
    ax.autoscale(tight=True)

    plt.legend(handles=[incomeBar, expensesBar])
    labelAxisAndSavePlot('date', 'income and expenses', 'monthlyIncomeAndExpenses.png')


@enforce.runtime_validation
def plotCategorical(yearlyCategorical: List[Tuple[float, Dict]], income: bool = True, quarters: bool = False) -> None:
    categories = getCategoriesFromMap(yearlyCategorical)
    plt.figure(figsize=figsize)

    # all bars take 0.6, 0.4 space between the years.
    w = 0.6 / len(categories)
    if quarters:
        w = w / 4
    xAxis = [x[0] for x in yearlyCategorical]

    colors = getColorsForCategories(categories)
    ax: Axes = plt.subplot(111)

    bars = []
    for idx, category in enumerate(categories):
        categoryList = [(yearCategories[1][category] if category in yearCategories[1] else 0) for yearCategories in yearlyCategorical]
        bars.append(ax.bar([xVal - (idx * w) + w / 2 for xVal in xAxis], categoryList, width=w, color=colors[idx], align='center', label=category))
    ax.autoscale(tight=True)

    if quarters:
        plt.xticks(xAxis, ['Q1', 'Q2', 'Q3', 'Q4'])

    plt.legend(handles=bars)
    yLabel = 'categorical income' if income else 'categorical expenses'
    fileName = 'CategoricalIncome.png' if income else 'CategoricalExpenses.png'
    labelAxisAndSavePlot('year', yLabel, fileName)


@enforce.runtime_validation
def getCategoriesFromMap(yearlyCategorical: List[Tuple[float, Dict]]) -> List[str]:
    # get all categories first
    categories = []
    for year in yearlyCategorical:
        for category, amount in year[1].items():
            if category not in categories:
                categories.append(category)
    return categories


@enforce.runtime_validation
def getColorsForCategories(categories: List[str]) -> np.ndarray:
    # get different color for each category
    # https://stackoverflow.com/questions/12236566/setting-different-color-for-each-series-in-scatter-plot-on-matplotlib
    x = np.arange(len(categories))
    ys = [i + x + (i * x) ** 2 for i in range(len(categories))]
    return cm.rainbow(np.linspace(0, 1, len(ys)))


@enforce.runtime_validation
def labelAxisAndSavePlot(xLabel: str, yLabel: str, fileName: str) -> None:
    plt.ylabel(xLabel)
    plt.xlabel(yLabel)
    plt.savefig(plotFolder + fileName)


@enforce.runtime_validation
def printSummary(
        monthlyBalance: List[Tuple[datetime.datetime, Decimal]],
        monthlyIO: List[List[Any]],
        yearlyIncome: List[Tuple[float, Dict]],
        yearlyExpenses: List[Tuple[float, Dict]]
) -> None:
    for mb in monthlyBalance:
        print(mb)
    print()

    for mb in monthlyIO:
        print(mb)
    print()

    for (year, ydict) in yearlyIncome:
        print(year)
        for key, val in ydict.items():
            print(key + " " + str(val))
    print()

    for (year, ydict) in yearlyExpenses:
        print(year)
        for key, val in ydict.items():
            print(key + " " + str(val))
    print()
