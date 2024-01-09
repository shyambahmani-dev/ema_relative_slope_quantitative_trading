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







class parameterRes(object):

    def __init__(self, CAGR, CAGRExcess, AUCRatio, maxUp, maxDown, averageUp):
        
        self.CAGR = CAGR
        self.CAGRExcess = CAGRExcess
        self.AUCRatio = AUCRatio
        self.maxUp = maxUp
        self.maxDown = maxDown
        self.averageUp = averageUp




class train(object):

    def __init__(self, train1, tickerName, intervalTested, strat_name, testName):

        self.train1 = train1
        self.strat_name = strat_name
        self.tickerName = tickerName
        self.periodTested = '1.5y'
        self.intervalTested = intervalTested
        


        relDel = relativedelta(self.train1.index[-1],self.train1.index[0])
        self.strat_years = (float)(relDel.years) + ( (float)(relDel.months)/12.0 ) +  (float)(relDel.days)/(365.25)
        daysDelta = self.train1.index[-1] - self.train1.index[0]
        self.strat_days = daysDelta.days


        print("\n\n")
        print("Optimising %s strategy for %s at %s interval for period of %.3f years or %.3f days \n \n" %(self.strat_name, self.tickerName, self.intervalTested, self.strat_years, self.strat_days))



        self.dmaIntv = [3, 5, 10, 15, 20, 25, 50, 75, 100, 150, 200, 500]
        self.emaIntv = [3, 5, 10, 15, 20, 25, 50, 75, 100, 150, 200, 500]

        self.train1DMA = getIndicators.getDMA(self.train1, self.dmaIntv)
        self.train1EMA = getIndicators.getEMA(self.train1, self.emaIntv)
        self.train1BB = getIndicators.getBB(self.train1)
        self.train1RSI = getIndicators.getRSI(self.train1)
        self.train1DMAslope = self.train1DMA.diff()
        self.train1EMASlope = self.train1EMA.diff()

        self.train1EMASlopeRel = pd.DataFrame()

        for it in self.train1EMASlope.columns:
            self.train1EMASlopeRel[it] = self.train1EMASlope[it]/self.train1["Close"]


        self.initialCash = 1e6
        self.feesFactor = 0.05
        
        
        self.stratRes = {}
        self.CAGRExcessRes = []
        self.AUCRatioRes = []
        self.maxUpRes = []
        self.maxDownRes = []
        self.averageUpRes = []




        if os.path.isdir(r".\results\%s" %(tickerName) ) :
                
            pass

        else:

            os.mkdir(r".\results\%s" %(tickerName) )





        emaList = [5, 10, 15, 25, 50, 75, 100]



        slopeListBuy = np.arange( -0.0005, 0.0006, 0.0001 )
        slopeListSell = np.arange( -0.0005, 0.0006, 0.0001 )



        for signalBuy in emaList:

            for signalSell in emaList:

                #slopeMinBuy = (train1EMASlopeRel["%s" %(signalBuy)].min())
                #slopeMaxBuy = (train1EMASlopeRel["%s" %(signalBuy)].max())
                #slopeListBuy = np.arange( slopeMinBuy, slopeMaxBuy, ( (slopeMaxBuy - slopeMinBuy)/10 ))
                #slopeListBuy = slopeListBuy[5:]
                #slopeListBuy = slopeListBuy[:-5]

                #slopeMinSell = (train1EMASlopeRel["%s" %(signalSell)].min())
                #slopeMaxSell = (train1EMASlopeRel["%s" %(signalSell)].max())
                #slopeListSell = np.arange( slopeMinSell, slopeMaxSell, ( (slopeMaxSell - slopeMinSell)/10 ))
                #slopeListSell = slopeListSell[5:]
                #slopeListSell = slopeListSell[:-5]


                print("\nHere")
                print(slopeListBuy)
                print(slopeListSell)
                print("E.O.L. \n")

                for buyAbove in slopeListBuy:

                    for sellBelow in slopeListSell:

                        if( signalBuy <= signalSell):

                            print("Running strat for %s-%s-%s-%s" %(signalBuy, signalSell, buyAbove, sellBelow))
                            
                            self.stratRes = self.run(signalBuy, signalSell, buyAbove, sellBelow)
                                        
                            self.CAGRExcessRes.append( [self.stratRes.CAGRExcess , {"signalBuy":signalBuy, "signalSell":signalSell, "buyAbove":buyAbove, "sellBelow":sellBelow}] )
                            self.AUCRatioRes.append( [self.stratRes.AUCRatio , {"signalBuy":signalBuy, "signalSell":signalSell, "buyAbove":buyAbove, "sellBelow":sellBelow}] )
                            self.maxUpRes.append( [self.stratRes.maxUp , {"signalBuy":signalBuy, "signalSell":signalSell, "buyAbove":buyAbove, "sellBelow":sellBelow}] )
                            self.maxDownRes.append( [self.stratRes.maxDown , {"signalBuy":signalBuy, "signalSell":signalSell, "buyAbove":buyAbove, "sellBelow":sellBelow}] )
                            self.averageUpRes.append( [self.stratRes.averageUp , {"signalBuy":signalBuy, "signalSell":signalSell, "buyAbove":buyAbove, "sellBelow":sellBelow}] )

        self.CAGRExcessRes.sort(key=lambda x: x[0], reverse=True)
        self.AUCRatioRes.sort(key=lambda x: x[0], reverse=True)
        self.maxUpRes.sort(key=lambda x: x[0], reverse=True)
        self.maxDownRes.sort(key=lambda x: x[0], reverse=True)
        self.averageUpRes.sort(key=lambda x: x[0], reverse=True)


        self.CAGRExcessResDF = pd.DataFrame(self.CAGRExcessRes)
        self.CAGRExcessResDF.to_csv( r".\results\%s\CAGRExcessRes_%s-%s-%s%s.csv" %(tickerName, tickerName, intervalTested, strat_name, testName) )

        self.AUCRatioResDF = pd.DataFrame(self.AUCRatioRes)
        self.AUCRatioResDF.to_csv( r".\results\%s\AUCRatioRes_%s-%s-%s%s.csv" %(tickerName, tickerName, intervalTested, strat_name, testName) )

        self.maxUpResDF = pd.DataFrame(self.maxUpRes)
        self.maxUpResDF.to_csv( r".\results\%s\maxUpRes_%s-%s-%s%s.csv" %(tickerName, tickerName, intervalTested, strat_name, testName) )

        self.maxDownResDF = pd.DataFrame(self.maxDownRes)
        self.maxUpResDF.to_csv( r".\results\%s\maxDownRes_%s-%s-%s%s.csv" %(tickerName, tickerName, intervalTested, strat_name, testName) )

        self.averageUpResDF = pd.DataFrame(self.averageUpRes)
        self.maxUpResDF.to_csv( r".\results\%s\averageUpRes_%s-%s-%s%s.csv" %(tickerName, tickerName, intervalTested, strat_name, testName) )
        
                
    def return_res(self):
        return { "bestResCAGR": self.CAGRExcessRes[0][1], "bestResAUC": self.AUCRatioRes[0][1], "bestResAverageUp": self.averageUpRes[0][1] }






    def run(self, signalBuy, signalSell, buyAbove, sellBelow):

        portfolio = pd.DataFrame(columns=['Value','AssetNum','Cash'], index= self.train1["Close"].index)
        currCash = self.initialCash
        currInvested = 0
        assetNum = 0
        
        daysBought = np.array([])
        daysSold = np.array([])
        marketPortfolio = pd.DataFrame(columns=['Value', 'AssetNum'], index= self.train1["Close"].index)
        marketPortfolio.set_index(self.train1.index)
        marketNum = self.initialCash/self.train1["Close"].iloc[0]

        profits = []
        losses = []

        for ind in self.train1.index:


            if(not pd.isna(self.train1EMASlopeRel["%s" %(max(signalBuy, signalSell))].loc[ind])):

                buyPrice = self.train1["Close"].loc[ind]
                sellPrice = buyPrice
                buyRatioCash = 1
                sellRatioPort = 1

                if( self.train1EMASlopeRel["%s" %(signalBuy)].loc[ind] > buyAbove):
                    
                    numCanBuy = (buyRatioCash*currCash)/( buyPrice )
                    currCash -= (numCanBuy*buyPrice) - min(30, (numCanBuy*(buyPrice)*self.feesFactor))
                    assetNum += numCanBuy
                                        
                    if( numCanBuy > 1 ):
                        daysBought = np.append(daysBought, ind)

                

                
                elif( self.train1EMASlopeRel["%s" %(signalSell)].loc[ind] < sellBelow):

                    numCanSell = (assetNum)*(sellRatioPort)
                    currCash += (numCanSell*(sellPrice)) - min(30, (numCanSell*(sellPrice))*self.feesFactor)
                    assetNum -= numCanSell
                    
                    if( numCanSell > 1 ):
                        daysSold = np.append(daysSold, ind)

                        res = (self.train1["Close"].loc[ind] - self.train1["Close"].loc[daysBought[-1]])/(self.train1["Close"].loc[daysBought[-1]])

                        if( res >= 0 ):
                            profits.append(res*100)
                        else:
                            losses.append(res*100)


            portfolio.loc[ind] = [currCash + assetNum*(self.train1["Close"].loc[ind]), assetNum, currCash]
            marketPortfolio.loc[ind] = [marketNum*(self.train1["Close"].loc[ind]), marketNum]


            portfolio.loc[ind] = [currCash + assetNum*(self.train1["Close"].loc[ind]), assetNum, currCash]
            marketPortfolio.loc[ind] = [marketNum*(self.train1["Close"].loc[ind]), marketNum]


        analysis = pa.analytics(self.train1, self.tickerName, "1.5y", self.intervalTested, portfolio, marketPortfolio, daysBought, daysSold)
        CAGRportfolio = analysis.CAGR()
        AUC = analysis.AUC_comp()
        marketDev = analysis.market_dev()

        toRet = parameterRes(CAGRportfolio['CAGRPort'], CAGRportfolio['CAGRExcess'], AUC['AUCRatio'], marketDev['maxUp'], marketDev['maxDown'], marketDev['averageUp'])

        return toRet

