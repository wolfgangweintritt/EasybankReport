#!/usr/bin/env python3
"""Draw Plots from csv."""
import os
import math
import datetime
import csv
import matplotlib.pyplot as plt
from matplotlib.dates import date2num
import matplotlib.cm as cm
import numpy as np
from transaction import Transaction


#### GLOBALS ####
dpi           = 96
figsize       = (1600/dpi, 800/dpi)
plotFolder    = None


def drawAllGraphs(dataFolder, skipFirstTransaction, year=None):
    global transactions
    transactions = []

    global plotFolder
    plotFolder = dataFolder + '/plots' + ('' if year is None else str(year)) + '/'
    os.makedirs(os.path.dirname(plotFolder), exist_ok=True)

    loadTransactions(dataFolder, year)

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
        categoricalIncome = getQuarterYearlyCategoricalCashflow(True)
        plotCategorical(categoricalIncome, True, True)

        categoricalExpenses = getQuarterYearlyCategoricalCashflow(False)
        plotCategorical(categoricalExpenses, False, True)

    printSummary(monthlyBalance, monthlyIO, categoricalIncome, categoricalExpenses)


def loadTransactions(dataFolder, year):
    with open(dataFolder + '/transactions.csv', newline='') as csvfile:
        csvReader = csv.reader(csvfile, delimiter=',')
        next(csvReader) # skip first line
        for row in csvReader:
            if year is None or row[0][6:] == str(year):
                transactions.append(Transaction(*row)) # unpack row

# calculate balance at the end of each month to an array, return it
# return an array containing tuples with date and balance for each month: [('01-01-2018', 100), ('01-02-2018', 222), ...]
def getMonthlyBalance():
    monthlyBalance = []
    balance        = 0
    lastTuple      = None

    for transaction in transactions:
        newDate = datetime.datetime.strptime(transaction.date, "%d.%m.%Y")
        if lastTuple is not None and lastTuple[0].month != newDate.month:
            monthlyBalance.append(lastTuple)
        balance += transaction.amount
        lastTuple = (newDate, balance)

    monthlyBalance.append(lastTuple)
    return monthlyBalance

# calculate earnings and expenses for each month, return it
# return an array with triple-arrays of date, income and expenses: [['2018-01-01', 100, 200], ['2018-02-01', 500, 222], ...]
def getMonthlyEarningsAndExpenses(skipFirstTransaction):
    monthlyIO = []
    io        = [0, 0]
    lastDate  = None
    skip      = skipFirstTransaction

    for transaction in transactions:
        if skip:
            skip = False
            continue
        newDate = datetime.datetime.strptime(transaction.date, "%d.%m.%Y")
        if lastDate is not None and lastDate.month != newDate.month:
            monthlyIO.append([datetime.date(lastDate.year, lastDate.month, 1)] + io)
            io = [0, 0]
        if transaction.amount > 0:
            io[0] += transaction.amount
        else:
            io[1] += transaction.amount*(-1)
        lastDate = newDate

    monthlyIO.append([datetime.date(lastDate.year, lastDate.month, 1)] + io)
    return monthlyIO

# return array of tuples [(2018, {'category1': 100, 'category2': 200, ...}), (2019, {}), ...]
def getYearlyCategoricalCashflow(skipFirstTransaction, income=True):
    yearlyIO            = []
    categoricalCashflow = {}
    lastDate            = None
    skip                = skipFirstTransaction

    for transaction in transactions:
        if skip:
            skip = False
            continue
        newDate = datetime.datetime.strptime(transaction.date, "%d.%m.%Y")
        if lastDate is not None and lastDate.year != newDate.year:
            yearlyIO.append((lastDate.year, categoricalCashflow))
            categoricalCashflow = {}
        category = transaction.category if transaction.category != '' else 'Uncategorized'
        if (income and transaction.amount > 0) or (not income and transaction.amount < 0):
            if category in categoricalCashflow:
                categoricalCashflow[category] += abs(transaction.amount)
            else:
                categoricalCashflow[category] = abs(transaction.amount)
        lastDate = newDate

    if lastDate is not None:
        yearlyIO.append((lastDate.year, categoricalCashflow))
    return yearlyIO

# return array of tuples [(2018.25, {'category1': 100, 'category2': 200, ...}), (2018.50: {}), ...]
def getQuarterYearlyCategoricalCashflow(income=True):
    yearlyIO             = []
    categoricalCashflow  = {}
    lastDate             = None

    for transaction in transactions:
        newDate = datetime.datetime.strptime(transaction.date, "%d.%m.%Y")
        if lastDate is not None and math.ceil(lastDate.month / 3) != math.ceil(newDate.month / 3):
            yearlyIO.append((lastDate.year + (math.ceil(lastDate.month / 3) / 4), categoricalCashflow))
            categoricalCashflow = {}
        category = transaction.category if transaction.category != '' else 'Uncategorized'
        if (income and transaction.amount > 0) or (not income and transaction.amount < 0):
            if category in categoricalCashflow:
                categoricalCashflow[category] += abs(transaction.amount)
            else:
                categoricalCashflow[category] = abs(transaction.amount)
        lastDate = newDate

    if lastDate is not None:
        yearlyIO.append((lastDate.year + (math.ceil(lastDate.month / 3) / 4), categoricalCashflow))
    return yearlyIO

def plotMonthlyBalance(monthlyBalance):
    plt.figure(figsize=figsize)
    plt.plot([x[0] for x in monthlyBalance], [x[1] for x in monthlyBalance])

    labelAxisAndSavePlot('date', 'balance', 'monthlyBalance.png')

def plotMonthlyIO(monthlyIO):
    plt.figure(figsize=figsize)

    w = 12 # width = 12 days
    x = date2num([x[0] for x in monthlyIO])
    ax = plt.subplot(111)
    incomeBar   = ax.bar(x-(w/2), [x[1] for x in monthlyIO], width=w, color='#67a9cf', align='center', label='Income')
    expensesBar = ax.bar(x+(w/2), [x[2] for x in monthlyIO], width=w, color='#ef8a62', align='center', label='Expenses')
    ax.xaxis_date()
    ax.autoscale(tight=True)

    plt.legend(handles=[incomeBar, expensesBar])
    labelAxisAndSavePlot('date', 'income and expenses', 'monthlyIncomeAndExpenses.png')

def plotCategorical(yearlyCategorical, income=True, quarters=False):
    categories = getCategoriesFromMap(yearlyCategorical)
    plt.figure(figsize=figsize)

    # all bars take 0.6, 0.4 space between the years.
    w = 0.6/len(categories)
    if quarters:
        w = w/4
    xAxis = [x[0] for x in yearlyCategorical]

    colors = getColorsForCategories(categories)
    ax = plt.subplot(111)

    bars = []
    for idx, category in enumerate(categories):
        categoryList = [(yearCategories[1][category] if category in yearCategories[1] else 0) for yearCategories in yearlyCategorical]
        bars.append(ax.bar([xVal - (idx * w) + w/2 for xVal in xAxis], categoryList, width=w, color=colors[idx], align='center', label=category))
    ax.autoscale(tight=True)

    if quarters:
        plt.xticks(xAxis, ['Q1', 'Q2', 'Q3', 'Q4'])

    plt.legend(handles=bars)
    yLabel = 'categorical income' if income else 'categorical expenses'
    fileName = 'CategoricalIncome.png' if income else 'CategoricalExpenses.png'
    labelAxisAndSavePlot('year', yLabel, fileName)

def getCategoriesFromMap(yearlyCategorical):
    # get all categories first
    categories = []
    for year in yearlyCategorical:
        for category, amount in year[1].items():
            if category not in categories:
                categories.append(category)
    return categories

def getColorsForCategories(categories):
    # get different color for each category
    # https://stackoverflow.com/questions/12236566/setting-different-color-for-each-series-in-scatter-plot-on-matplotlib
    x = np.arange(len(categories))
    ys = [i + x + (i * x) ** 2 for i in range(len(categories))]
    return cm.rainbow(np.linspace(0, 1, len(ys)))

def labelAxisAndSavePlot(xLabel, yLabel, fileName):
    plt.ylabel(xLabel)
    plt.xlabel(yLabel)
    plt.savefig(plotFolder + fileName)

def printSummary(monthlyBalance, monthlyIO, yearlyIncome, yearlyExpenses):
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
