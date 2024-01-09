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
import Project1.graphing_functions.plotTrades as plotTrades
import Project1.graphing_functions.analyze_trades as analyzeTrades




strat_name = 'EMA Relative Slope Strategy'



# ^NSEI-1h 10-50-0.0003-0.0003



intervalTested = '1h'

signalBuy = 10
signalSell = 50

buyAbove = 0.0003
sellBelow = 0.0003

tickerName = "^NSEI"



data1 = getData.tickerData(symbol= tickerName, intervalTested = intervalTested)
data1.index = pd.to_datetime(data1.index, utc= True)

relDel = relativedelta(data1.index[-1], data1.index[0])
strat_years = float(relDel.years) + ( (float)(relDel.months)/12.0 ) +  (float)(relDel.days)/(365.25)
strat_years = round(strat_years, 3)
periodTested = str(strat_years)



print("\n\n")
print("Strategy %s applied on %s at interval of %s for %.3f years from %s to %s \n \n" %(strat_name, tickerName, intervalTested, strat_years, data1.index[0].date(), data1.index[-1].date()))




data1DMA = getIndicators.getDMA(data1)
data1EMA = getIndicators.getEMA(data1)
data1BB = getIndicators.getBB(data1)
data1RSI = getIndicators.getRSI(data1)
data1DMASlope = data1DMA.diff()
data1EMASlope = data1EMA.diff()
data1EMASlopeRel = pd.DataFrame()

for it in data1EMASlope.columns:
    data1EMASlopeRel[it] = data1EMASlope[it]/data1["Close"]



portfolio = pd.DataFrame(columns=['Value','AssetNum','Cash', 'bought', 'sold'], index= data1["Close"].index)

portfolio["bought"].fillna(0)
portfolio["sold"].fillna(0)

initialCash = (1.0)*(1e6)

currCash = (1.0)*(1e6)
currInvested = 0
assetNum = 0

feesFactor = 0.05

daysBought = np.array([])
daysSold = np.array([])


marketPortfolio = pd.DataFrame(columns=['Value', 'AssetNum'], index= data1["Close"].index)
marketPortfolio.set_index(data1.index)
marketNum = initialCash/data1["Close"].iloc[0]

profits =[]
losses = []

lastBought = None

#"""

for ind in data1.index:


    if(not pd.isna(data1EMA["%s" %(max(signalBuy, signalSell))].loc[ind])):

        buyPrice = data1["Close"].loc[ind]
        sellPrice = buyPrice
        buyRatioCash = 1.0
        sellRatioPort = 1.0
        
        bought = 0
        sold = 0

        if( data1EMASlopeRel["%s" %(signalBuy)].loc[ind] > buyAbove):
            
            numCanBuy = (buyRatioCash*currCash)/( buyPrice )
            currCash -= (numCanBuy*buyPrice) - min(30, (numCanBuy*(buyPrice)*feesFactor))
            assetNum += numCanBuy
            
            if( numCanBuy > 1 ):
                bought = 1
                lastBought = ind
            
        

        
        elif( data1EMASlopeRel["%s" %(signalSell)].loc[ind] < sellBelow):

            numCanSell = (assetNum)*(sellRatioPort)
            currCash += (numCanSell*(sellPrice)) - min(30, (numCanSell*(sellPrice))*feesFactor)
            assetNum -= numCanSell
            
            if( numCanSell > 1 ):
                
                sold = 1

                res = (data1["Close"].loc[ind] - data1["Close"].loc[lastBought])/(data1["Close"].loc[lastBought])
                lastBought = None

                if( res >= 0 ):
                    profits.append(res*100)
                else:
                    losses.append(res*100)

    

    portfolio.loc[ind] = [currCash + assetNum*(data1["Close"].loc[ind]), assetNum, currCash, bought, sold]
    marketPortfolio.loc[ind] = [marketNum*(data1["Close"].loc[ind]), marketNum]


#"""



#print(portfolio)
#print("\n")
#print(marketPortfolio)



analysis = pa.analytics(data1, tickerName, periodTested, intervalTested, portfolio, marketPortfolio, profits, losses)
totalReturns = analysis.portfolio_returns()
CAGRportfolio = analysis.CAGR()
marketDev = analysis.market_dev()
AUC = analysis.AUC_comp()
sharpeRatio = analysis.sharpe_ratio()
drawdown = analysis.drawdown()
profitsAndLosses = analysis.profits_and_losses()
alpha = analysis.alpha()



analysis.show_results()




#plotPortfolio.plot(data1, tickerName, periodTested, intervalTested, strat_name, portfolio, marketPortfolio)
analyzeTrades.plot(data1, tickerName, periodTested, intervalTested, strat_name, portfolio, marketPortfolio)
savePortfolio.save(data1, tickerName, periodTested, intervalTested, strat_name, portfolio, marketPortfolio)


#input("Done")
#code.interact(local=locals())
