#!/usr/bin/env python3
"""Draw Plots from csv."""

import datetime
import csv
import matplotlib.pyplot as plt
from matplotlib.dates import date2num
import matplotlib.cm as cm
import numpy as np
from transaction import Transaction


#### GLOBALS ####
transactions  = []
dpi           = 96
figsize       = (1600/dpi, 800/dpi)


def loadTransactions(filename):
    with open(filename, newline='') as csvfile:
        csvReader = csv.reader(csvfile, delimiter=',')
        next(csvReader) # skip first line
        for row in csvReader:
            transactions.append(Transaction(*row)) # unpack row

# calculate balance at the end of each month to an array, return it
def getMonthlyBalance():
    monthlyBalance = []
    balance = 0
    lastTuple = None

    for transaction in transactions:
        newDate = datetime.datetime.strptime(transaction.date, "%d.%m.%Y")
        if lastTuple != None and lastTuple[0].month != newDate.month:
            monthlyBalance.append(lastTuple)
        balance += transaction.amount
        lastTuple = (newDate, balance)

    monthlyBalance.append(lastTuple)
    return monthlyBalance

# calculate earnings and expenses for each month, return it
def getMonthlyEarningsAndExpenses():
    monthlyIO = []
    io = [0, 0]
    lastDate = None
    skipFirstTransaction = True

    for transaction in transactions:
        if skipFirstTransaction:
            skipFirstTransaction = False
            continue
        newDate = datetime.datetime.strptime(transaction.date, "%d.%m.%Y")
        if lastDate != None and lastDate.month != newDate.month:
            monthlyIO.append([datetime.date(lastDate.year, lastDate.month, 1)] + io)
            io = [0, 0]
        if transaction.amount > 0:
            io[0] += transaction.amount
        else:
            io[1] += transaction.amount*(-1)
        lastDate = newDate

    monthlyIO.append([datetime.date(lastDate.year, lastDate.month, 1)] + io)
    return monthlyIO

def getYearlyCategoricalCashflow(income=True):
    yearlyIO = []
    categoricalCashflow = {}
    lastDate = None
    skipFirstTransaction = True

    for transaction in transactions:
        if skipFirstTransaction:
            skipFirstTransaction = False
            continue
        newDate = datetime.datetime.strptime(transaction.date, "%d.%m.%Y")
        if lastDate != None and lastDate.year != newDate.year:
            yearlyIO.append((lastDate.year, categoricalCashflow))
            categoricalCashflow = {}
        category = transaction.category if transaction.category != '' else 'Uncategorized'
        if (income and transaction.amount > 0) or (not income and transaction.amount < 0):
            if category in categoricalCashflow:
                categoricalCashflow[category] += abs(transaction.amount)
            else:
                categoricalCashflow[category] = abs(transaction.amount)
        lastDate = newDate

    if lastDate != None:
        yearlyIO.append((lastDate.year, categoricalCashflow))
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
    incomeBar   = ax.bar(x-(w/2), [x[1] for x in monthlyIO], width=w, color='b', align='center', label='Income')
    expensesBar = ax.bar(x+(w/2), [x[2] for x in monthlyIO], width=w, color='g', align='center', label='Expenses')
    ax.xaxis_date()
    ax.autoscale(tight=True)

    plt.legend(handles=[incomeBar, expensesBar])
    labelAxisAndSavePlot('date', 'income and expenses', 'monhtlyIncomeAndExpenses.png')

def plotYearlyCategorical(yearlyCategorical, income=True):
    # get all categories first
    categories = []
    for year in yearlyCategorical:
        for category, amount in year[1].items():
            if category not in categories:
                categories.append(category)

    plt.figure(figsize=figsize)

    # all bars take 0.6, 0.4 space between the years.
    w = 0.6/len(categories)
    xAxis = [x[0] for x in yearlyCategorical]

    # get different color for each category
    # https://stackoverflow.com/questions/12236566/setting-different-color-for-each-series-in-scatter-plot-on-matplotlib
    x = np.arange(len(categories))
    ys = [i+x+(i*x)**2 for i in range(len(categories))]
    colors = cm.rainbow(np.linspace(0, 1, len(ys)))
    ax = plt.subplot(111)

    bars = []
    for idx, category in enumerate(categories):
        categoryList = [(yearCategories[1][category] if category in yearCategories[1] else 0) for yearCategories in yearlyCategorical]
        bars.append(ax.bar([xVal - (idx * w) + 0.3 for xVal in xAxis], categoryList, width=w, color=colors[idx], align='center', label=category))
    ax.autoscale(tight=True)

    plt.legend(handles=bars)
    yLabel = 'categorical income' if income else 'categorical expenses'
    fileName = 'yearlyCategoricalIncome.png' if income else 'yearlyCategoricalExpenses.png'
    labelAxisAndSavePlot('year', yLabel, fileName)


def labelAxisAndSavePlot(xLabel, yLabel, fileName):
    plt.ylabel(xLabel)
    plt.xlabel(yLabel)
    plt.savefig('plots/' + fileName)

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


#### MAIN ####
loadTransactions('transactions.csv')

monthlyBalance = getMonthlyBalance()
monthlyIO = getMonthlyEarningsAndExpenses()
yearlyIncome = getYearlyCategoricalCashflow(True)
yearlyExpenses = getYearlyCategoricalCashflow(False)
printSummary(monthlyBalance, monthlyIO, yearlyIncome, yearlyExpenses)

plotMonthlyBalance(monthlyBalance)
plotMonthlyIO(monthlyIO)
plotYearlyCategorical(yearlyIncome, True)
plotYearlyCategorical(yearlyExpenses, False)