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
import Project1.performance_analysis.run_analysis as pa
import Project1.graphing_functions.plotPortfolio as plotPortfolio
import Project1.graphing_functions.plotTrades as plotTrades

import Project1.backtest.ema_rel_slope_L_strat_tt_split_func as train_func


strat_name = 'EMA Relative Slope Strategy'






intervalTested = '1h'

tickerName = "^NSEI"
periodTested = "10y"



data1 = getData.tickerDataLive(symbol= tickerName, periodTested = periodTested, intervalTested = intervalTested)
data1.index = pd.to_datetime(data1.index, utc= True)

print("data1\n")
print(data1)
print("\n\n")

train_test_ratio = 0.5

trainNum = (int)(train_test_ratio*(data1.index.size))
testNum = (int)(data1.index.size - trainNum)

print("Train data = %d : %d-%d" %( trainNum , 0, trainNum ) )
print("Test data = %d : %d-%d" %( testNum, testNum, (data1.index.size) - testNum ) )

train1 = data1.iloc[ 0 : trainNum ]
test1 = data1.iloc[ trainNum : (data1.index.size) ]

print("train1 \n")
print(train1)

print("test1 \n")
print(test1)


testName = "TT_Split_EMA"







train_object = train_func.train(train1, tickerName, intervalTested, strat_name, testName)
trainRes = train_object.return_res()

metric = "bestResCAGR"

signalBuy = trainRes[metric]["signalBuy"]
signalSell = trainRes[metric]["signalSell"]

buyAbove = trainRes[metric]["buyAbove"]
sellBelow = trainRes[metric]["sellBelow"]









relDel = relativedelta(test1.index[-1], test1.index[0])
strat_years = float(relDel.years) + ( (float)(relDel.months)/12.0 ) +  (float)(relDel.days)/(365.25)

print("\n\n")
print("Strategy %s applied on %s at interval of %s for %.3f years from %s to %s \n \n" %(strat_name, tickerName, intervalTested, strat_years, test1.index[0].date(), test1.index[-1].date()))



dmaIntv = [3, 5, 10, 15, 25, 50, 75, 100, 150, 200, 500]
emaIntv = [3, 5, 10, 15, 25, 50, 75, 100, 150, 200, 500]

test1DMA = getIndicators.getDMA(test1, dmaIntv)
test1EMA = getIndicators.getEMA(test1, emaIntv)
test1BB = getIndicators.getBB(test1)
test1RSI = getIndicators.getRSI(test1)
test1DMASlope = test1DMA.diff()
test1EMASlope = test1EMA.diff()
test1EMASlopeRel = pd.DataFrame()

for it in test1EMASlope.columns:
    test1EMASlopeRel[it] = test1EMASlope[it]/test1["Close"]



portfolio = pd.DataFrame(columns=['Value','AssetNum','Cash'], index= test1["Close"].index)

initialCash = (1.0)*(1e6)

currCash = (1.0)*(1e6)
currInvested = 0
assetNum = 0

feesFactor = 0.05

daysBought = np.array([])
daysSold = np.array([])


marketPortfolio = pd.DataFrame(columns=['Value', 'AssetNum'], index= test1["Close"].index)
marketPortfolio.set_index(test1.index)
marketNum = initialCash/test1["Close"].iloc[0]


profits = []
losses = []


#"""

for ind in test1.index:


    if(not pd.isna(test1EMA["%s" %(max(signalBuy, signalSell))].loc[ind])):

        buyPrice = test1["Close"].loc[ind]
        sellPrice = buyPrice
        buyRatioCash = 1.0
        sellRatioPort = 1.0

        if( test1EMASlopeRel["%s" %(signalBuy)].loc[ind] > buyAbove):
            
            numCanBuy = (buyRatioCash*currCash)/( buyPrice )
            currCash -= (numCanBuy*buyPrice) - min(30, (numCanBuy*(buyPrice)*feesFactor))
            assetNum += numCanBuy
            
            if( numCanBuy > 1 ):
                daysBought = np.append(daysBought, ind)
            
        

        
        elif( test1EMASlopeRel["%s" %(signalSell)].loc[ind] < sellBelow):

            numCanSell = (assetNum)*(sellRatioPort)
            currCash += (numCanSell*(sellPrice)) - min(30, (numCanSell*(sellPrice))*feesFactor)
            assetNum -= numCanSell
            
            if( numCanSell > 1 ):
                daysSold = np.append(daysSold, ind)

                res = (test1["Close"].loc[ind] - test1["Close"].loc[daysBought[-1]])/(test1["Close"].loc[daysBought[-1]])

                if( res >= 0 ):
                    profits.append(res*100)
                else:
                    losses.append(res*100)

    
    

    portfolio.loc[ind] = [currCash + assetNum*(test1["Close"].loc[ind]), assetNum, currCash]
    marketPortfolio.loc[ind] = [marketNum*(test1["Close"].loc[ind]), marketNum]


#"""



#print(portfolio)
#print("\n")
#print(marketPortfolio)



analysis = pa.analytics(test1, tickerName, periodTested, intervalTested, portfolio, marketPortfolio, daysBought, daysSold, profits, losses)
totalReturns = analysis.portfolio_returns()
CAGRportfolio = analysis.CAGR()
marketDev = analysis.market_dev()
AUC = analysis.AUC_comp()
sharpeRatio = analysis.sharpe_ratio()
drawdown = analysis.drawdown()
profitsAndLosses = analysis.profits_and_losses()


analysis.show_results()




plotPortfolio.plot(test1, tickerName, periodTested, intervalTested, portfolio, strat_name, daysBought, daysSold, marketPortfolio)
#plotTrades.plot(test1, tickerName, periodTested, portfolio, strat_name, daysBought, daysSold, marketPortfolio)



input("Done Bro")
code.interact(local=locals())
