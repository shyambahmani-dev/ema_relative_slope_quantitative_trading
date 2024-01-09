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



tickerName = "^NSEI"
periodTested = "10y"
strat_name = "ema_rel_slope"
intervalTested = '1h'
testName = "rel_slope_test"
if(testName != ""):
    testName = '-' + testName




data1 = getData.tickerData(symbol= tickerName, periodTested = periodTested, intervalTested= intervalTested)

dmaIntv = [3, 5, 10, 15, 20, 25, 50, 75, 100, 150, 200, 500]
emaIntv = [3, 5, 10, 15, 20, 25, 50, 75, 100, 150, 200, 500]

data1DMA = getIndicators.getDMA(data1, dmaIntv)
data1EMA = getIndicators.getEMA(data1, emaIntv)
data1BB = getIndicators.getBB(data1)
data1RSI = getIndicators.getRSI(data1)
data1DMASlope = data1DMA.diff()
data1EMASlope = data1EMA.diff()
data1EMASlopeRel = pd.DataFrame()

for it in data1EMASlope.columns:
    data1EMASlopeRel[it] = data1EMASlope[it]/data1["Close"]





class parameterRes(object):

    def __init__(self, CAGR, CAGRExcess, AUCRatio, maxUp, maxDown, averageUp):
        
        self.CAGR = CAGR
        self.CAGRExcess = CAGRExcess
        self.AUCRatio = AUCRatio
        self.maxUp = maxUp
        self.maxDown = maxDown
        self.averageUp = averageUp




class run_strat(object):

    def __init__(self, strat_name, tickerName, periodTested, intervalTested):

        self.strat_name = strat_name
        self.tickerName = tickerName
        self.periodTested = periodTested
        self.intervalTested = intervalTested
        

        if( os.path.isfile( r".\database\%s-%s-%s-%s.csv" %(self.tickerName, self.periodTested, (str)(datetime.datetime.today().date()), self.intervalTested ) ) ):
            self.data1 = pd.read_csv( r".\database\%s-%s-%s-%s.csv" %(self.tickerName, self.periodTested, (str)(datetime.datetime.today().date()), self.intervalTested ), index_col = [0] )
            self.data1.index = pd.to_datetime(self.data1.index)
        else:
            self.data1 = getData.tickerData(symbol= self.tickerName, periodTested= self.periodTested, intervalTested= self.intervalTested)
            self.data1.to_csv( r".\database\%s-%s-%s-%s.csv" %(self.tickerName, self.periodTested, (str)(datetime.datetime.today().date()), self.intervalTested  ) )


        relDel = relativedelta(self.data1.index[-1],self.data1.index[0])
        self.strat_years = (float)(relDel.years) + ( (float)(relDel.months)/12.0 ) +  (float)(relDel.days)/(365.25)
        daysDelta = self.data1.index[-1] - self.data1.index[0]
        self.strat_days = daysDelta.days


        print("\n\n")
        print("Optimising %s strategy for %s at %s interval for period of %.3f years or %.3f days \n \n" %(self.strat_name, self.tickerName, self.intervalTested, self.strat_years, self.strat_days))



        self.dmaIntv = [3, 5, 10, 15, 20, 25, 50, 75, 100, 150, 200, 500]
        self.emaIntv = [3, 5, 10, 15, 20, 25, 50, 75, 100, 150, 200, 500]

        self.data1DMA = getIndicators.getDMA(self.data1, self.dmaIntv)
        self.data1EMA = getIndicators.getEMA(self.data1, self.emaIntv)
        self.data1BB = getIndicators.getBB(self.data1)
        self.data1RSI = getIndicators.getRSI(self.data1)
        self.data1DMAslope = self.data1DMA.diff()
        self.data1EMASlope = self.data1EMA.diff()

        self.data1EMASlopeRel = pd.DataFrame()

        for it in self.data1EMASlope.columns:
            self.data1EMASlopeRel[it] = self.data1EMASlope[it]/self.data1["Close"]


        self.initialCash = 1e6
        self.feesFactor = 0.05




    def run(self, signalBuy, signalSell, buyAbove, sellBelow):

        portfolio = pd.DataFrame(columns=['Value','AssetNum','Cash'], index= self.data1["Close"].index)
        currCash = self.initialCash
        currInvested = 0
        assetNum = 0
        
        daysBought = np.array([])
        daysSold = np.array([])
        marketPortfolio = pd.DataFrame(columns=['Value', 'AssetNum'], index= self.data1["Close"].index)
        marketPortfolio.set_index(self.data1.index)
        marketNum = self.initialCash/self.data1["Close"].iloc[0]

        profits = []
        losses = []

        for ind in self.data1.index:


            if(not pd.isna(self.data1EMASlopeRel["%s" %(max(signalBuy, signalSell))].loc[ind])):

                buyPrice = self.data1["Close"].loc[ind]
                sellPrice = buyPrice
                buyRatioCash = 1
                sellRatioPort = 1

                if( self.data1EMASlopeRel["%s" %(signalBuy)].loc[ind] > buyAbove):
                    
                    numCanBuy = (buyRatioCash*currCash)/( buyPrice )
                    currCash -= (numCanBuy*buyPrice) - min(30, (numCanBuy*(buyPrice)*self.feesFactor))
                    assetNum += numCanBuy
                                        
                    if( numCanBuy > 1 ):
                        daysBought = np.append(daysBought, ind)

                

                
                elif( self.data1EMASlopeRel["%s" %(signalSell)].loc[ind] < sellBelow):

                    numCanSell = (assetNum)*(sellRatioPort)
                    currCash += (numCanSell*(sellPrice)) - min(30, (numCanSell*(sellPrice))*self.feesFactor)
                    assetNum -= numCanSell
                    
                    if( numCanSell > 1 ):
                        daysSold = np.append(daysSold, ind)

                        res = (self.data1["Close"].loc[ind] - self.data1["Close"].loc[daysBought[-1]])/(self.data1["Close"].loc[daysBought[-1]])

                        if( res >= 0 ):
                            profits.append(res*100)
                        else:
                            losses.append(res*100)


            portfolio.loc[ind] = [currCash + assetNum*(self.data1["Close"].loc[ind]), assetNum, currCash]
            marketPortfolio.loc[ind] = [marketNum*(self.data1["Close"].loc[ind]), marketNum]


            portfolio.loc[ind] = [currCash + assetNum*(self.data1["Close"].loc[ind]), assetNum, currCash]
            marketPortfolio.loc[ind] = [marketNum*(self.data1["Close"].loc[ind]), marketNum]




        analysis = pa.analytics(self.data1, self.tickerName, self.periodTested, self.intervalTested, portfolio, marketPortfolio, daysBought, daysSold)
        CAGRportfolio = analysis.CAGR()
        AUC = analysis.AUC_comp()
        marketDev = analysis.market_dev()

        toRet = parameterRes(CAGRportfolio['CAGRPort'], CAGRportfolio['CAGRExcess'], AUC['AUCRatio'], marketDev['maxUp'], marketDev['maxDown'], marketDev['averageUp'])

        return toRet

    






stratRes = {}
CAGRExcessRes = []
AUCRatioRes = []
maxUpRes = []
maxDownRes = []
averageUpRes = []




if os.path.isdir(r".\results\%s" %(tickerName) ) :
        
    pass

else:

    os.mkdir(r".\results\%s" %(tickerName) )





emaList = [5, 10, 25, 50, 75, 100, 200]



strat_object = run_strat(strat_name, tickerName, periodTested, intervalTested)
#slopeListBuy = np.arange( -0.0005, 0.0006, 0.0001 )
#slopeListSell = np.arange( -0.0005, 0.0006, 0.0001 )



for signalBuy in emaList:

    for signalSell in emaList:

        slopeMinBuy = (data1EMASlopeRel["%s" %(signalBuy)].mean() - 2*data1EMASlopeRel["%s" %(signalBuy)].std())
        slopeMaxBuy = (data1EMASlopeRel["%s" %(signalBuy)].mean() + 2*data1EMASlopeRel["%s" %(signalBuy)].std())
        slopeListBuy = np.arange( slopeMinBuy, slopeMaxBuy, ( (slopeMaxBuy - slopeMinBuy)/10 ))

        slopeMinSell = (data1EMASlopeRel["%s" %(signalSell)].mean() - 2*data1EMASlopeRel["%s" %(signalSell)].std)
        slopeMaxSell = (data1EMASlopeRel["%s" %(signalSell)].mean() + 2*data1EMASlopeRel["%s" %(signalSell)].std)
        slopeListSell = np.arange( slopeMinSell, slopeMaxSell, ( (slopeMaxSell - slopeMinSell)/10 ))


        print("\nHere")
        print(slopeListBuy)
        print(slopeListSell)
        print("E.O.L. \n")

        for buyAbove in slopeListBuy:

            for sellBelow in slopeListSell:

                if( signalBuy <= signalSell):

                    print("Running strat for %s-%s-%s-%s" %(signalBuy, signalSell, buyAbove, sellBelow))
                    
                    stratRes = strat_object.run(signalBuy, signalSell, buyAbove, sellBelow)
                                
                    CAGRExcessRes.append( [stratRes.CAGRExcess , "%s-%s-%s-%s" %(signalBuy, signalSell, buyAbove, sellBelow)] )
                    AUCRatioRes.append( [stratRes.AUCRatio , "%s-%s-%s-%s" %(signalBuy, signalSell, buyAbove, sellBelow)] )
                    maxUpRes.append( [stratRes.maxUp , "%s-%s-%s-%s" %(signalBuy, signalSell, buyAbove, sellBelow)] )
                    maxDownRes.append( [stratRes.maxDown , "%s-%s-%s-%s" %(signalBuy, signalSell, buyAbove, sellBelow)] )
                    averageUpRes.append( [stratRes.averageUp , "%s-%s-%s-%s" %(signalBuy, signalSell, buyAbove, sellBelow)] )

CAGRExcessRes.sort(reverse=True)
AUCRatioRes.sort(reverse=True)
maxUpRes.sort(reverse=True)
maxDownRes.sort(reverse=True)
averageUpRes.sort(reverse=True)


CAGRExcessResDF = pd.DataFrame(CAGRExcessRes)
CAGRExcessResDF.to_csv( r".\results\%s\CAGRExcessRes_%s-%s-%s%s.csv" %(tickerName, tickerName, intervalTested, strat_name, testName) )

AUCRatioResDF = pd.DataFrame(AUCRatioRes)
AUCRatioResDF.to_csv( r".\results\%s\AUCRatioRes_%s-%s-%s%s.csv" %(tickerName, tickerName, intervalTested, strat_name, testName) )

maxUpResDF = pd.DataFrame(maxUpRes)
maxUpResDF.to_csv( r".\results\%s\maxUpRes_%s-%s-%s%s.csv" %(tickerName, tickerName, intervalTested, strat_name, testName) )

maxDownResDF = pd.DataFrame(maxDownRes)
maxUpResDF.to_csv( r".\results\%s\maxDownRes_%s-%s-%s%s.csv" %(tickerName, tickerName, intervalTested, strat_name, testName) )

averageUpResDF = pd.DataFrame(averageUpRes)
maxUpResDF.to_csv( r".\results\%s\averageUpRes_%s-%s-%s%s.csv" %(tickerName, tickerName, intervalTested, strat_name, testName) )






code.interact(local=locals())