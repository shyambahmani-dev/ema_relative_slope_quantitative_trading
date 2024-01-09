import numpy as np
import pandas as pd
import yfinance as yf
import datetime
import csv
import os
import code
from dateutil.relativedelta import relativedelta
import traceback

import sys
sys.path.append("..")


import Project1.data_functions.get_data as getData
import Project1.data_functions.get_indicators as getIndicators

import Project1.performance_analysis.run_analysis as pa



from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton

from lightweight_charts.widgets import QtChart

class plot(object):

    #"""
    
    def __init__(self, data1, tickerName, periodTested, intervalTested, strat_name, portfolio, marketPortfolio):

        self.data1 = data1
        self.tickerName = tickerName
        self.periodTested = periodTested
        self.intervalTested = intervalTested
        self.strat_name = strat_name
        self.portfolio = portfolio
        self.marketPortfolio = marketPortfolio
        
        app = QApplication([])
        window = QMainWindow()
        layout = QVBoxLayout()
        widget = QWidget()
        widget.setLayout(layout)

        window.resize(800, 500)
        layout.setContentsMargins(0, 0, 0, 0)



        chart = QtChart(widget, toolbox=False, inner_height=0.6)


        portVal = self.portfolio.copy()
        portVal.rename(columns = {'Value':'Strategy Portfolio'}, inplace = True)
        portfolioLine = chart.create_line("Strategy Portfolio", color= 'darkgreen')
        portfolioLine.set(portVal)



        marketVal = self.marketPortfolio.copy()
        marketVal.rename(columns = {'Value':'Benchmark Portfolio'}, inplace = True)
        marketPortfolioLine = chart.create_line("Benchmark Portfolio", color= 'sienna')
        marketPortfolioLine.set(marketVal)

        chart.legend(visible=True, text= "%s  -  %s" %(tickerName, strat_name))

        chart2 = chart.create_subchart(toolbox=True, position='bottom', width=1, height=0.4, sync= True)
        chart2.set(self.data1)
        chart2.legend(visible=True, text= "%s  -  OHLC Chart" %(tickerName))





        layout.addWidget(chart.get_webview())
        window.setCentralWidget(widget)

        window.show()

        app.exec_()

        relDel = relativedelta(self.data1.index[-1],self.data1.index[0])
        self.strat_years = (float)(relDel.years) + ( (float)(relDel.months)/12.0 ) +  (float)(relDel.days)/(365.25)
        daysDelta = self.data1.index[-1] - self.data1.index[0]
        self.strat_days = daysDelta.days

        if not (os.path.isdir(r".\results\%s" %(tickerName))):
        
            os.makedirs(r".\results\%s" %(tickerName))
        
        self.portfolio.to_csv(r".\results\%s\Portfolio-%s-%s-%s-%s-%s.csv" %(tickerName, tickerName, intervalTested, data1.index[0].date(), self.strat_days, strat_name))
        


