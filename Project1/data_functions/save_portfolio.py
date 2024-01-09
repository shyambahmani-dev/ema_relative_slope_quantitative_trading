import numpy as np
import pandas as pd
import yfinance as yf
import sklearn as sk
import datetime
import csv
import os
import code
from dateutil.relativedelta import relativedelta
import traceback
import warnings
warnings.filterwarnings("ignore")

import sys
sys.path.append("..")



import Project1.data_functions.get_data as getData
import Project1.data_functions.get_indicators as getIndicators
import Project1.data_functions.save_portfolio as savePortfolio

import Project1.performance_analysis.run_analysis as pa

import Project1.graphing_functions.plotPortfolio as plotPortfolio
import Project1.graphing_functions.analyze_trades as analyzeTrades



class save(object):
    
    def __init__(self, data1, tickerName, periodTested, intervalTested, strat_name, portfolio, marketPortfolio) -> None:
        
        self.data1 = data1
        self.tickerName = tickerName
        self.periodTested = periodTested
        self.intervalTested = intervalTested
        self.portfolio = portfolio
        self.strat_name = strat_name
        self.marketPortfolio = marketPortfolio
        
        if not (os.path.isdir(r".\results\%s" %(tickerName))):
        
            os.makedirs(r".\results\%s" %(tickerName))


        self.portfolio.to_csv("results\%s\%s-%s-%s-%s.csv" %(tickerName, tickerName, periodTested, intervalTested, strat_name) )
        self.marketPortfolio.to_csv("results\%s\%s-benchmark-%s-%s-%s.csv" %(tickerName, tickerName, periodTested, intervalTested, strat_name) )
        