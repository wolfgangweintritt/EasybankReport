# Easybank.at parser

## Description

Parses csv file from easybank.at and generates some useful plots, which their ebanking-site really lacks.

## Run
`python3 easybankReport.py <path-to-csv-file>`

Show parameter help: `python3 easybankReport.py --help` 

## Short description of python files
`csvParser.py`: Parses easybank csv file and returns all transactions. Also categorizes the transactions via IBAN or Regex. Configureable via `data/iban.csv` and `data/text.csv`.

`drawGraphs.py`: Uses data from the csv to generate some plots. E.g. Balance over time, Categorical spendings/income per year, Income/Spendings per month.

## Requirements

* python3-tk
* numpy via pip3
* matplotlib via pip3
