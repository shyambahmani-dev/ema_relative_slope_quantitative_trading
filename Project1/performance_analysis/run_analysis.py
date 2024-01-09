import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.widgets as mplw
from matplotlib.backends.backend_pdf import PdfPages, FigureCanvasPdf
import yfinance as yf
import datetime
import csv
import os
import code
import time
from dateutil.relativedelta import relativedelta
from pandas import ExcelWriter
import inline
import traceback

import sys
sys.path.append("..")

import Project1.data_functions.get_data as getData
import Project1.data_functions.get_indicators as getIndicators
import Project1.graphing_functions.plotPortfolio as plotPortfolio



try:

    class analytics(object):

        def __init__(self, data1, tickerName, periodTested, intervalTested, portfolio, marketPortfolio, profits = [], losses = []):

            self.data1 = data1
            self.data1.index = pd.to_datetime(self.data1.index)
            self.tickerName = tickerName
            self.periodTested = periodTested
            self.intervalTested = intervalTested
            self.portfolio = portfolio
            self.marketPortfolio = marketPortfolio
            self.initialCash = self.portfolio['Value'].iloc[0]
            self.niftyList = [ "ADANIENT.NS", "ADANIPORTS.NS", "APOLLOHOSP.NS", "ASIANPAINT.NS", "AXISBANK.NS", 
                               "BAJAJ-AUTO.NS", "BAJFINANCE.NS", "BAJAJFINSV.NS", "BPCL.NS", "BHARTIARTL.NS", 
                               "BRITANNIA.NS", "CIPLA.NS", "COALINDIA.NS", "DIVISLAB.NS", "DRREDDY.NS", "EICHERMOT.NS", 
                               "GRASIM.NS", "HCLTECH.NS", "HDFCBANK.NS", "HDFCLIFE.NS", "HEROMOTOCO.NS", "HINDALCO.NS", 
                               "HINDUNILVR.NS", "ICICIBANK.NS", "ITC.NS", "INDUSINDBK.NS", "INFY.NS", "JSWSTEEL.NS", 
                               "KOTAKBANK.NS", "LTIM.NS", "LT", "M&M.NS", "MARUTI.NS", "NTPC.NS", "NESTLEIND.NS", 
                               "ONGC.NS", "POWERGRID.NS", "RELIANCE.NS", "SBILIFE.NS", "SBIN.NS", "SUNPHARMA.NS", "TCS.NS", 
                               "TATACONSUM.NS", "TATAMOTORS.NS", "TATASTEEL.NS", "TECHM.NS", "TITAN.NS", "UPL.NS", "ULTRACEMCO.NS", "WIPRO.NS"]
            self.profits = profits
            self.losses = losses

            self.riskFreeRate = 0.05


            relDel = relativedelta(self.data1.index[-1],self.data1.index[0])
            self.strat_years = float(relDel.years) + ( (float)(relDel.months)/12.0 ) +  (float)(relDel.days)/(365.25)



        
        """
        
        ## As hourly only 720 day data is available, we use x% to find parameter and then the y% 310 to test on as test-train split. (70%-30%)
        ## This way we'll be able to see if parameters evaluated from one year data works well on the following period as well.
        ## Let's go.
        
        
        
        ## -- More metrics to integrate -- ##
        
        Sortino Ratio
        Calmer Ratio
        Capture Ratio
        Average Holding Period
        Rolling performance analysis
        Correlation Analysis
        Monte Carlo Simulation
        Maximum Adverse Excursion (MAE)
        Maximum Favorable Excursion (MFE)
        Portfolio Turnover
        
        #"""
        
        def alpha(self):
            
            
            cagrs = self.CAGR()
            
            CAGRPort = cagrs["CAGRPort"]
            CAGRMarket = cagrs["CAGRMarket"]
            
            covar = (float)(self.portfolio["Value"].cov(self.marketPortfolio["Value"]))
            
            varMarket  = (float)(self.marketPortfolio["Value"].var())
            
            beta = covar/varMarket
            
            alpha = CAGRPort - self.riskFreeRate*100 - beta*(CAGRMarket - self.riskFreeRate*100)
                        
            return alpha



        def daily_returns(self):

            dailyRets = np.array()

            for ind in self.portfolio:
                pass

            
            

        def portfolio_returns(self):

            portfolioReturns = (((float)(self.portfolio['Value'].iloc[-1] - self.initialCash))/(float)(self.initialCash))*100
            marketReturns = (((float)(self.data1["Close"].iloc[-1] - self.data1["Close"].iloc[0]))/((float)(self.data1["Close"].iloc[0])))*100
            
            return {'portfolioReturns':portfolioReturns, 'marketReturns':marketReturns, 'excessReturns':portfolioReturns - marketReturns}
        
        def CAGR(self):
            CAGRPort = (pow( (float)(((float)(self.portfolio['Value'].iloc[-1]))/((float)(self.initialCash))), 1.0/self.strat_years) - 1)*100
            CAGRMarket = (pow((((float)(self.data1["Close"].iloc[-1]))/((float)(self.data1["Close"].iloc[0]))), 1.0/self.strat_years) - 1)*100

            return {'CAGRPort':CAGRPort, 'CAGRMarket':CAGRMarket, 'CAGRExcess': CAGRPort - CAGRMarket}


        def sharpe_ratio(self):

            dailyReturnsPortfolio = np.array([])
            dailyReturnsMarket = np.array([])

            for ind in self.portfolio.index:
                    nxt = (ind + relativedelta(days = 1))
                    if( nxt in self.portfolio.index ):
                        dailyReturnsPortfolio = np.append(dailyReturnsPortfolio, (float)(self.portfolio["Value"].loc[nxt] - self.portfolio["Value"].loc[ind])/(float)(self.portfolio["Value"].loc[ind]) )
                        dailyReturnsMarket = np.append(dailyReturnsMarket, (float)(self.marketPortfolio["Value"].loc[nxt] - self.marketPortfolio["Value"].loc[ind])/(float)(self.marketPortfolio["Value"].loc[ind]) )

            meanPort = (1 + dailyReturnsPortfolio.mean())**252 - 1
            meanMarket = (1 + dailyReturnsMarket.mean())**252 - 1
            
            varPort = dailyReturnsPortfolio.var()*252
            varMarket = dailyReturnsMarket.var()*252
                        
            sharpeRatioPortfolio = (meanPort - self.riskFreeRate)/(varPort**0.5)
            sharpeRatioMarket = (meanMarket - self.riskFreeRate)/(varMarket**0.5)

            return {'sharpeRatioPortfolio':sharpeRatioPortfolio, 'sharpeRatioMarket':sharpeRatioMarket}




        def market_dev(self):

            averageUp = 0.0
            maxUp = 0
            maxDown = 0

            for ind in self.portfolio.index:
                averageUp += (float)((float)(self.portfolio["Value"].loc[ind] - self.marketPortfolio["Value"].loc[ind])/(float)(self.marketPortfolio["Value"].loc[ind]))
                maxUp = max( maxUp, (float)(self.portfolio["Value"].loc[ind] - self.marketPortfolio["Value"].loc[ind])/(float)(self.marketPortfolio["Value"].loc[ind]) )
                maxDown = min(maxDown, (float)(self.portfolio["Value"].loc[ind] - self.marketPortfolio["Value"].loc[ind])/(float)(self.marketPortfolio["Value"].loc[ind]) )

            averageUp = (float)(averageUp)/(float)(self.portfolio.index.size)
            
            maxUp *= 100
            maxDown *= 100
            averageUp *= 100
            
            return {'maxUp':maxUp, 'maxDown':maxDown, 'averageUp':averageUp}

        def AUC_comp(self):

            portfolioAUC = 0
            marketPortfolioAUC = 0

            for ind in self.portfolio.index:

                portfolioAUC += self.portfolio["Value"].loc[ind]
                marketPortfolioAUC += self.marketPortfolio["Value"].loc[ind]

            return {'portfolioAUC':portfolioAUC, 'marketPortfolioAUC':marketPortfolioAUC, 'AUCRatio':(float)((( float )( portfolioAUC ))/( (float)( marketPortfolioAUC ) ))  }
        
        def drawdown(self):

            maxYet = 0.0
            maxYetB = 0.0

            drawdownPortfolio = 0.0
            drawdownMarket = 0.0

            for ind in self.portfolio.index:

                if( self.portfolio["Value"].loc[ind] > maxYet ):
                    maxYet = self.portfolio["Value"].loc[ind]
                
                if( (float)(self.portfolio["Value"].loc[ind] - maxYet)/(float)(maxYet) < drawdownPortfolio ):
                    drawdownPortfolio = (float)(self.portfolio["Value"].loc[ind] - maxYet)/(float)(maxYet)


                if( self.marketPortfolio["Value"].loc[ind] > maxYetB ):
                    maxYetB = self.marketPortfolio["Value"].loc[ind]
                
                if( (float)(self.marketPortfolio["Value"].loc[ind] - maxYetB)/(float)(maxYetB) < drawdownMarket ):
                    drawdownMarket = (float)(self.marketPortfolio["Value"].loc[ind] - maxYetB)/(float)(maxYetB)


            return {'drawdownPortfolio': drawdownPortfolio*100, 'drawdownMarket':drawdownMarket*100}

        
        def profits_and_losses(self):

            if( len(self.profits) == 0 and len(self.losses) == 0 ):
                avgProfit = 0
                avgLoss = 0
                profLossRatio = 1e6
            
            elif( len(self.profits) == 0 or len(self.losses) == 0 ):
                
                if(len(self.profits) == 0):
                    avgProfit = 0
                else:
                    avgProfit = (((float)(sum(self.profits)))/( (float)(len(self.profits)) ))*100
                    profLossRatio = 1e6

                if(len(self.losses) == 0):
                    avgLoss = 0
                else:
                    avgLoss = (((float)(sum(self.losses)))/( (float)(len(self.losses)) ))*100
                    profLossRatio = -1*(1e6)
                

            else:
                avgProfit = (((float)(sum(self.profits)))/( (float)(len(self.profits)) ))*100
                avgLoss = (((float)(sum(self.losses)))/( (float)(len(self.losses)) ))*100

                profLossRatio = avgProfit/avgLoss
            
            return {"avgProfit":avgProfit, "avgLoss":avgLoss, "profLossRatio":profLossRatio, "numProfits":len(self.profits), "numLosses":len(self.losses)}
        

        def show_results(self):
            
            totalReturns = self.portfolio_returns()
            CAGRportfolio = self.CAGR()
            marketDev = self.market_dev()
            AUC = self.AUC_comp()
            sharpeRatio = self.sharpe_ratio()
            drawdown = self.drawdown()
            profitsAndLosses = self.profits_and_losses()
            alpha = self.alpha()

            print(":: Total Returns :: \n")
            print("Strategy : %.3f %%" %(totalReturns['portfolioReturns']))
            print("Market : %.3f %%" %(totalReturns['marketReturns']))
            print("Excess : %.3f %%" %(totalReturns['excessReturns']))

            print("\n\n")

            print(":: CAGR analysis :: \n")
            print("Strategy : %.3f %%" %(CAGRportfolio['CAGRPort']))
            print("Market : %.3f %%" %(CAGRportfolio['CAGRMarket']))
            print("Excess : %.3f %%" %(CAGRportfolio['CAGRExcess']))

            print("\n\n")

            print(":: AUC analysis :: \n")
            print("AUC ratio = %.3f" %(AUC['AUCRatio']) )

            print("\n\n")

            print(":: Profits and Losses :: \n")
            print("Average Profit per trade = %.3f" %(profitsAndLosses['avgProfit']))
            print("Number of profits = %.3f" %(profitsAndLosses['numProfits']))
            print("Average Loss per trade = %.3f" %(profitsAndLosses['avgLoss']))
            print("Number of losses = %.3f" %(profitsAndLosses['numLosses']))

            print("\n\n")

            print(":: Market deviation analysis :: \n")
            print("Max up from market = %.3f %%" %(marketDev['maxUp']) )
            print("Max Down from market = %.3f %%" %(marketDev['maxDown']) )
            print("Average Up from market = %.3f %%" %(marketDev['averageUp']) )

            print("\n\n")

            print(":: Sharpe Ratio analysis :: \n")
            print("Sharpe Ratio of Portfolio = %.3f" %(sharpeRatio['sharpeRatioPortfolio']))
            print("Sharpe Ratio of Market = %.3f" %(sharpeRatio['sharpeRatioMarket']))

            print("\n\n")

            print(":: Drawdown analysis :: \n")
            print("Max Drawdown of Portfolio = %.3f %%" %(drawdown['drawdownPortfolio']))
            print("Max Drawdown of Market = %.3f %%" %(drawdown['drawdownMarket']))
            
            print("\n\n")

            print(":: Alpha analysis :: \n")
            print("Alpha of Portfolio = %.3f %%" %(alpha))
            



            print("\n\n\n")


            

                                             




except Exception as exp:
    
    print(exp)
    input()

