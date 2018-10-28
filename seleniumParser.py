#!/usr/bin/env python3
# coding=utf-8
"""Get transactions from easybank.at via selenium, save them to csv."""
import os
import csv
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import getpass
from transaction import Transaction


#### GLOBALS ####
loginURL   = 'https://ebanking.easybank.at/InternetBanking/InternetBanking?d=login&svc=EASYBANK&ui=html&lang=de'
ibanRegex  = '[a-zA-Z]{2}[0-9]{2}[a-zA-Z0-9]{4}[0-9]{7}([a-zA-Z0-9]?){0,16}'
stack      = []
textRegex  = []
knownIbans = []
silent     = False
driver     = None

#### MAIN ####
def parseTransactions(staySilent, headless, dataFolder):
    global silent
    silent = staySilent

    # prompt for username and password
    user     = input('Username: ')
    password = getpass.getpass('Password: ')

    loadCsvIntoTupleList('data/ibans.csv', knownIbans)
    loadCsvIntoTupleList('data/text.csv', textRegex)

    chrome_options = Options()
    if headless:
        chrome_options.add_argument('--headless')
    chrome_options.add_argument('--window-size=1920x1080')
    global driver
    driver = webdriver.Chrome(chrome_options=chrome_options)

    login(user, password)
    navigateToTransactionsPage()
    getTransactions()
    #for transaction in stack:
        #print(transaction)
    saveCsv(dataFolder)

    driver.close()

def loadCsvIntoTupleList(filename, tupleList):
    with open(filename, newline='') as csvfile:
        csvReader = csv.reader(csvfile, delimiter=',')
        for row in csvReader:
            tupleList.append((row[0], row[1]))

def login(user, password):
    driver.get(loginURL)
    usernameField = driver.find_element_by_css_selector("#login #lof5")
    usernameField.clear()
    usernameField.send_keys(user)
    passwordField = driver.find_element_by_css_selector("#login #lof9")
    passwordField.clear()
    passwordField.send_keys(password)
    passwordField.send_keys(Keys.RETURN)
    log("tried to log in.")

def navigateToTransactionsPage():
    try:
        transactionsButton = driver.find_element_by_link_text('Umsätze')
    except NoSuchElementException:
        transactionsButton = driver.find_element_by_link_text('Transactions')
    transactionsButton.click()

def getTransactions():
    # todo improve performance

    tableRows = driver.find_elements_by_css_selector('#sales-detail tbody tr')
    for row in tableRows:
        rowCells = row.find_elements_by_tag_name('td')

        date = rowCells[1].text
        amount = rowCells[9].text
        # transform GER seperator style string to US seperator style number
        amount = amount.replace(".", "").replace(",", ".")
        text = rowCells[3].text
        iban = re.search(ibanRegex, text)
        iban = '' if (iban is None) else iban.group(0)
        category = getCategory(iban, text)

        transaction = Transaction(date, iban, amount, category, text)
        stack.append(transaction)
    log("saved " + str(len(tableRows)) + " transactions to stack.")

    # navigate to next page
    try:
        nextPageButton = driver.find_element_by_link_text('weiter')
    except NoSuchElementException:
        nextPageButton = driver.find_element_by_link_text('Forward')
    # if the button is not disabled => click it
    if nextPageButton.get_attribute('class').find('disabled') == -1:
        nextPageButton.click()
        getTransactions()

def getCategory(iban, text):
    for (tCategory, tIban) in knownIbans:
        if tIban == iban:
            return tCategory

    for (tCategory, tRegex) in textRegex:
        searchResult = re.search(tRegex, text)
        if searchResult is not None:
            return tCategory
    return ''

def saveCsv(dataFolder):
    csvContent = "date,IBAN,amount,category,text\n"
    while len(stack) > 0:
        csvContent += stack.pop().toCsvRow()
    csvPath = dataFolder + '/transactions.csv'
    os.makedirs(os.path.dirname(csvPath), exist_ok=True)
    f = open(csvPath, 'w')
    f.write(csvContent)
    f.close()
    log("saved transactions to transactions.csv!")

def log(msg):
    if not silent:
        print(msg)
