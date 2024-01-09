import numpy as np
import pandas as pd
import scipy as sp
import scipy.stats as stats
import math
import sklearn as sk
import time
import datetime
from dateutil.relativedelta import relativedelta
import csv
import os
import code

import yfinance as yf

import traceback
import warnings
warnings.filterwarnings("ignore")

import sys
sys.path.append("..")

from sklearn import datasets, linear_model
from sklearn.metrics import mean_squared_error, r2_score

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.widgets as mplw
import matplotlib.figure as mplf
import matplotlib.animation as mplani
from matplotlib.backends.backend_pdf import PdfPages, FigureCanvasPdf
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from dateutil.relativedelta import relativedelta

from pandas import ExcelWriter


import Project1.data_functions.get_data as getData
import Project1.data_functions.get_indicators as getIndicators
import Project1.performance_analysis.run_analysis as pa
import Project1.graphing_functions.plotPortfolio as plotPortfolio
#import Project1.graphing_functions.savePlots as savePlot







class plot(object):

    #"""
    
    def __init__(self, data1, tickerName, periodTested, intervalTested, strat_name, portfolio, marketPortfolio):
        
        self.data1 = data1
        self.tickerName = tickerName
        self.periodTested = periodTested
        self.intervalTested = intervalTested
        self.portfolio = portfolio
        self.strat_name = strat_name
        self.marketPortfolio = marketPortfolio
        
        self.data1DMA = getIndicators.getDMA(data1)
        self.data1EMA = getIndicators.getEMA(data1)
        self.data1BB = getIndicators.getBB(data1)
        self.data1RSI = getIndicators.getRSI(data1)
        self.data1DMASlope = self.data1DMA.diff()
        self.data1EMASlope = self.data1EMA.diff()
        self.data1EMASlopeRel = pd.DataFrame()
        
        for it in self.data1EMASlope.columns:
            self.data1EMASlopeRel[it] = self.data1EMASlope[it]/data1["Close"]


        
        #### -- OHLC DataFrame -- ####
        
        self.data1ohlc = pd.DataFrame()
        self.data1ohlc["OmC"] = self.data1["Open"].copy()
        self.data1ohlc["CmO"] = self.data1["Close"].copy()
        self.data1ohlc["HmO"] = self.data1["High"].copy()
        self.data1ohlc["LlC"] = self.data1["Low"].copy()
        self.data1ohlc["HmC"] = self.data1["High"].copy()
        self.data1ohlc["LlO"] = self.data1["Low"].copy()
        
            
        for i in self.data1.index:

            if self.data1["Open"].loc[i] >= self.data1["Close"].loc[i]:

                self.data1ohlc["OmC"].loc[i] = self.data1["Open"].loc[i] - self.data1["Close"].loc[i]
                self.data1ohlc["HmO"].loc[i] = self.data1["High"].loc[i] - self.data1["Open"].loc[i]
                self.data1ohlc["LlC"].loc[i] = self.data1["Close"].loc[i] - self.data1["Low"].loc[i]
                self.data1ohlc["CmO"].loc[i] = int(0)
                self.data1ohlc["HmC"].loc[i] = int(0)
                self.data1ohlc["LlO"].loc[i] = int(0)
                
            elif self.data1["Close"].loc[i] >= self.data1["Open"].loc[i]:

                self.data1ohlc["CmO"].loc[i] = self.data1["Close"].loc[i] - self.data1["Open"].loc[i]
                self.data1ohlc["HmC"].loc[i] = self.data1["High"].loc[i] - self.data1["Close"].loc[i]
                self.data1ohlc["LlO"].loc[i] = self.data1["Open"].loc[i] - self.data1["Low"].loc[i]
                self.data1ohlc["OmC"].loc[i] = int(0)
                self.data1ohlc["HmO"].loc[i] = int(0)
                self.data1ohlc["LlC"].loc[i] = int(0)
        
        #### -- EODF -- ####
        
        
        
        
        self.colorList = ["teal", "goldenrod", "brown", "darkolivegreen", "cadetblue", "slategray", "darkslategray"]
    
        trade_plot_object = self.show_trades()
    
        
    def show_trades(self):
        
        figColor = "lavender"
        axesColor = "white"
        
        
        
        
        #### -- Normal OHLC -- ####
        
        print("Loading OHLC Chart")
        
        self.fig1 = plt.figure(figsize = (12,12), facecolor=figColor)
        self.gs = self.fig1.add_gridspec(4,4)
        
        self.ax101 = self.fig1.add_subplot(self.gs[0:1,0:3], facecolor= axesColor)        
        self.ax102 = self.fig1.add_subplot(self.gs[1:4,0:3], sharex= self.ax101, facecolor= axesColor)
        
        self.portfolio_plot(self.ax101, self.fig1)
        self.ohlc_plot(self.ax102, self.fig1)
                        
        self.fig1.tight_layout()
        
        self.fig1.canvas.manager.set_window_title("OHLC Chart")
        
        #plotkarde101 = Drawer(self.ax102,self.fig1)
        mcursor1 = mplw.MultiCursor(self.fig1.canvas , [self.ax101, self.ax102] , horizOn= True , color = "lightskyblue" , linewidth = 1)
        
        print("OHLC Chart Loaded")
        
        #### -- EO Normal OHLC -- ####
        
        
        
        
        
        
        #### -- EMA OHLC -- ####
        
        print("Loading EMA Chart")
        
        self.fig2 = plt.figure(figsize = (12,12), facecolor=figColor)
        self.gs = self.fig2.add_gridspec(4,4)
        
        self.ax201 = self.fig2.add_subplot(self.gs[0:1,0:3], facecolor= axesColor)        
        self.ax202 = self.fig2.add_subplot(self.gs[1:4,0:3], sharex= self.ax201, facecolor= axesColor)
        
        self.portfolio_plot(self.ax201, self.fig2)
        self.ema_ohlc_plot(self.ax202, self.fig2)
            
        self.fig2.tight_layout()
        
        self.fig2.canvas.manager.set_window_title("EMA Chart")
        
        #plotkarde201 = Drawer(self.ax202,self.fig2)
        mcursor2 = mplw.MultiCursor(self.fig2.canvas , [self.ax201, self.ax202] , horizOn= True , color = "lightskyblue" , linewidth = 1)

        print("EMA Chart Loaded")

        #### -- EO EMA OHLC -- ####
        
        
        
        
        
        #### -- Relative EMA Slope -- ####
        
        
        
        
        
        
        
        
        
        
        
        
        
        plt.show()
    
    
    def ema_ohlc_plot(self, ax, fig, emaList = ["5", "10", "25", "50", "100", "200", "500"]):
        
        self.ohlc_plot(ax, fig)
        
        colInd = 0
        
        for it in emaList:
            ax.plot(range(0, self.data1EMA.index.size), self.data1EMA[it], label = ("EMA %s" %(it)), color= self.colorList[colInd])
            colInd += 1
    
        
        
    def portfolio_plot(self, ax, fig):
        
        ax.plot( range(0, self.portfolio.index.size), self.portfolio["Value"], color= "darkgreen", linewidth= 1)
        ax.plot( range(0, self.marketPortfolio.index.size), self.marketPortfolio["Value"], color= "brown", linewidth= 1)
        ax.set_ylim( min(self.portfolio["Value"].min(), self.marketPortfolio["Value"].min()) - self.portfolio["Value"].std(), max( self.portfolio["Value"].max(), self.marketPortfolio["Value"].max() ) + self.portfolio["Value"].std() )
        
        #"""
        for it in range(0,self.portfolio.index.size):
            if( self.portfolio["bought"].iloc[it] == 1 ):
                ax.axvline(it, color = 'green', alpha = 0.2)
            
            elif( self.portfolio["sold"].iloc[it] == 1 ):
                ax.axvline(it, color = 'red', alpha = 0.2)
        #"""




    def ohlc_plot(self, ax, fig):
        
        ax.bar(range(0,self.data1.index.size) , self.data1ohlc["OmC"] , bottom = self.data1["Close"] , color = "red" , width = 0.8)
        ax.bar(range(0,self.data1.index.size) , self.data1ohlc["CmO"] , bottom = self.data1["Open"] , color = "green" , width = 0.8)
        
        ax.bar(range(0,self.data1.index.size) , self.data1ohlc["HmO"] , bottom = self.data1["Open"] , color = "red" , width = 0.3)
        ax.bar(range(0,self.data1.index.size) , self.data1ohlc["HmC"] , bottom = self.data1["Close"] , color = "green" , width = 0.3)
        ax.bar(range(0,self.data1.index.size) , self.data1ohlc["LlC"] , bottom = self.data1["Low"] , color = "red" , width = 0.3)
        ax.bar(range(0,self.data1.index.size) , self.data1ohlc["LlO"] , bottom = self.data1["Low"] , color = "green" , width = 0.3)
        
        #"""
        for it in range(0,self.portfolio.index.size):
            if( self.portfolio["bought"].iloc[it] == 1 ):
                ax.axvline(it, color = 'green', alpha = 0.2)
            
            elif( self.portfolio["sold"].iloc[it] == 1 ):
                ax.axvline(it, color = 'red', alpha = 0.2)
        #"""












    
try:

    class Drawer(object):


        def __init__(self,ax,fig):
            
            
            self.ax = ax
            self.fig = fig
            
            self.check_button_line_drawer = mplw.CheckButtons( plt.axes([0.76,0.867,0.10,0.1]) , labels = [" Line Drawer"," Horizontal Line"," Vertical Line"] )
            self.check_button_rect_drawer = mplw.CheckButtons( plt.axes([0.76,0.817,0.10,0.05]) , labels = [" Rectangle\n Drawer"] )
            self.check_button_long_n_short_drawer = mplw.CheckButtons( plt.axes([0.76,0.717,0.10,0.1]) , labels = [" Long Position" , " Short Position"] )
            self.check_button_fib_retrac_drawer = mplw.CheckButtons( plt.axes([0.76,0.667,0.10,0.05]) , labels = [" Fibonacci\n Retracement"] )
            self.check_button_select_regression_points = mplw.CheckButtons( plt.axes([0.76,0.617,0.10,0.05]) , labels = [" Regression Points"] )
            
            self.click_button_draw_regresseion_line = mplw.Button( plt.axes([0.76,0.567,0.10,0.05]) , label= "Draw Regression Line")
            self.click_button_draw_regresseion_line.on_clicked(self.draw_regression_line)                        
            self.rxs = np.array([])
            self.rys = np.array([])
            

            self.cid_pick = self.fig.canvas.mpl_connect('pick_event', self.on_pick)
            self.cid_key = self.fig.canvas.mpl_connect('key_press_event', self.on_key)
            
            self.cid_mouse_click_linedrawer = self.fig.canvas.mpl_connect('button_press_event', self.line_drawer)
            self.cid_mouse_click_hori_linedrawer = self.fig.canvas.mpl_connect('button_press_event', self.hori_line_drawer)
            self.cid_mouse_click_veri_linedrawer = self.fig.canvas.mpl_connect('button_press_event', self.veri_line_drawer)
            self.cid_mouse_click_rect_drawer = self.fig.canvas.mpl_connect('button_press_event', self.rect_drawer)
            self.cid_mouse_click_long_posi_drawer = self.fig.canvas.mpl_connect('button_press_event', self.long_posi_drawer)
            self.cid_mouse_click_short_posi_drawer = self.fig.canvas.mpl_connect('button_press_event', self.short_posi_drawer)
            self.cid_mouse_click_fib_retrac_drawer = self.fig.canvas.mpl_connect('button_press_event', self.fib_retrac_drawer)
            self.cid_mouse_click_regression_points = self.fig.canvas.mpl_connect('button_press_event', self.select_regression_point)
            
            #self.cid_mouse_click = self.fig.canvas.mpl_connect('button_press_event', self.get_mouse_click)
            #self.cid_mouse_release = self.fig.canvas.mpl_connect('button_release_event', self.get_mouse_release)
            #self.cid_mouse_move = self.fig.canvas.mpl_connect('motion_notify_event', self.get_mouse_move)
            #self.cid_get_key_press = self.fig.canvas.mpl_connect('key_press_event', self.get_key_press)
            #self.cid_get_key_release = self.fig.canvas.mpl_connect('key_press_event', self.get_key_release)
            #self.cid_mouse_enter_axis = self.fig.canvas.mpl_connect('axes_enter_event', self.draw_line)



        
        def select_regression_point(self,event):

            if self.check_button_select_regression_points.get_status()[0]:
                
                if event.dblclick:
                    
                    if event.button == 1:
                        
                        print("Getting data : \n")
                        
                        self.rxs = np.append( self.rxs , event.xdata )
                        self.rys = np.append( self.rys , event.ydata )
                        
                        print(self.rxs,"\n",self.rys)




        def draw_regression_line(self,event):
            
            if self.rxs.size != 0:
            
                regr = linear_model.LinearRegression()
                
                self.rxs = np.reshape(self.rxs, (len(self.rxs),1))
                #self.rys = np.reshape(self.rys, (len(self.rys),1))
                
                regr.fit(self.rxs,self.rys)
                
                print(self.rxs,"\n",self.rys)
                print(regr.coef_)
                print(regr.intercept_)
                
                
                pred_rys = regr.predict(self.rxs)
                
                regr_line, = self.ax.plot(self.rxs , pred_rys , picker=True , pickradius = 5 , color = "blue" , linewidth = 0.8)
                regr_line.figure.canvas.draw()
                
                self.rxs = [[]]
                self.rys = [[]]




        
        def line_drawer(self,event):
                    
            
            if self.check_button_line_drawer.get_status()[0]:
                    
                if event.dblclick:
                    
                    if event.button == 1:
                        
                        self.xs = event.xdata
                        self.ys = event.ydata

                        self.cid_mouse_move_line_drawer = self.fig.canvas.mpl_connect('motion_notify_event', self.mouse_move_line_drawer)
                        
                        while True:
                            
                            try:
                                xy = plt.ginput(1)
                                break
                            except:
                                pass
                        
                        self.fig.canvas.mpl_disconnect(self.cid_mouse_move_line_drawer)
                        
                        x = [event.xdata,xy[0][0]]
                        y = [event.ydata,xy[0][1]]
                        line, = self.ax.plot(x , y , picker=True , pickradius = 5 , color = "blue" , linewidth = 0.8)
                        line.figure.canvas.draw()
                    
                        
        def mouse_move_line_drawer(self,event):
            
            if event.inaxes:
                
                line, = self.ax.plot([self.xs , event.xdata], [self.ys , event.ydata], 'r' , linewidth = 0.1 , alpha = 0.7)
                line.figure.canvas.draw()
                self.ax.lines.pop()



        def hori_line_drawer(self,event):
            
            
            if self.check_button_line_drawer.get_status()[1]:

                if event.dblclick:
            
                    line = self.ax.axhline(event.ydata , picker = True , pickradius = 5 , color = "violet" , alpha = 0.5)

                    #mpl.backend_bases.NavigationToolbar2(self.fig.canvas).push_current()
                        
                    self.ax.figure.canvas.draw()
                        
                    if mpl.backend_bases.NavigationToolbar2(self.fig.canvas) is None:
                        pass
                    else:
                        mpl.backend_bases.NavigationToolbar2(self.fig.canvas).back()
        
                else:
                    
                    pass
                
            else:
                    
                pass



        def veri_line_drawer(self,event):
        
            
            if self.check_button_line_drawer.get_status()[2]:

                if event.dblclick:
                    
                    line = self.ax.axvline(event.xdata , picker = True , pickradius = 5 , color = "sienna" , alpha = 0.5)
                    
                    self.ax.figure.canvas.draw()
                else:
                    
                    pass
            else:
                    
                pass
            
            


        def rect_drawer(self,event):
            

            if self.check_button_rect_drawer.get_status()[0]:
                
                if event.dblclick:
                
                    self.xs = event.xdata
                    self.ys = event.ydata
                    
                    self.cid_mouse_move_rect = self.fig.canvas.mpl_connect('motion_notify_event', self.mouse_move_rect_drawer)
                    
                    while True:
                    
                        try:
                            xy = plt.ginput(1)
                            break
                        except:
                            pass
                    
                    self.fig.canvas.mpl_disconnect(self.cid_mouse_move_rect)
                    
                    rectadd = mpl.patches.Rectangle( (min(event.xdata,xy[0][0]) , min(event.ydata,xy[0][1]) ) , 
                                                            np.abs(event.xdata - xy[0][0]) , np.abs(event.ydata - xy[0][1]) ,
                                                            angle = 0.0 , color = "skyblue" , alpha = 0.3 , picker = True)
                    
                    self.ax.add_patch(rectadd)
                    self.ax.figure.canvas.draw()

                    mpl.backend_bases.NavigationToolbar2(self.fig.canvas).push_current()                
                    mpl.backend_bases.NavigationToolbar2(self.fig.canvas).back()

                else:
                    
                    pass
            
            else:
                    
                pass
            
        
        
        def mouse_move_rect_drawer(self,event):
            
            if event.inaxes:
                            
                rect = mpl.patches.Rectangle( ( min( event.xdata , self.xs ) , min( event.ydata , self.ys ) ) , 
                                                        np.abs(event.xdata - self.xs ) , np.abs(event.ydata - self.ys ) ,
                                                        angle = 0.0 , color = "skyblue" , alpha = 0.3 )
                
                self.ax.add_patch(rect)
                self.ax.figure.canvas.draw()
                
                self.ax.patches.pop()




        def long_posi_drawer(self,event):
            
            
            if self.check_button_long_n_short_drawer.get_status()[0]:
            
                if event.dblclick:
            
                    self.xs = event.xdata
                    self.ys = event.ydata
                    
                    self.ratio = 0.333333333333
                    
                    self.cid_mouse_move_long_posi = self.fig.canvas.mpl_connect('motion_notify_event', self.mouse_move_long_posi_drawer)
                
                    xy = plt.ginput(1)

                    self.fig.canvas.mpl_disconnect(self.cid_mouse_move_long_posi)
                                                        
                    rkrwrectprofper = mpl.patches.Rectangle( ( min( event.xdata , xy[0][0] ) , min( event.ydata , xy[0][1] ) ) , 
                                                            np.abs( event.xdata - xy[0][0] ) , np.abs( event.ydata - xy[0][1] ) ,
                                                            angle = 0.0 , color = "lightgreen" , alpha = 0.3 , picker = True )
                    
                    rkrwrectlossper = mpl.patches.Rectangle( ( min( event.xdata , xy[0][0] ) , min( event.ydata , xy[0][1] ) ) , 
                                                            np.abs( event.xdata - xy[0][0] ) , (-self.ratio)*( np.abs( event.ydata - xy[0][1] ) ) ,
                                                            angle = 0.0 , color = "lightcoral" , alpha = 0.3 , picker = True )
                        
                    self.ax.add_patch(rkrwrectprofper)
                    self.ax.add_patch(rkrwrectlossper)

                    self.ax.figure.canvas.draw()
                    
                    mpl.backend_bases.NavigationToolbar2(self.fig.canvas).push_current()                
                    mpl.backend_bases.NavigationToolbar2(self.fig.canvas).back()
                
                else:
                    
                    pass

            else:
                    
                pass
        
        
        def mouse_move_long_posi_drawer(self,event):
            
            if event.inaxes:
             
                rkrwrectprof = mpl.patches.Rectangle( ( min( event.xdata , self.xs ) , min( event.ydata , self.ys ) ) , 
                                                        np.abs(event.xdata - self.xs ) , np.abs(event.ydata - self.ys ) ,
                                                        angle = 0.0 , color = "lightgreen" , alpha = 0.3 )
                
                rkrwrectloss = mpl.patches.Rectangle( ( min( event.xdata , self.xs ) , min( event.ydata , self.ys ) ) , 
                                                        np.abs(event.xdata - self.xs ) , (-self.ratio)*( np.abs( event.ydata - self.ys ) ) ,
                                                        angle = 0.0 , color = "lightcoral" , alpha = 0.3 )
                
                self.ax.add_patch(rkrwrectprof)
                self.ax.add_patch(rkrwrectloss)
                
                self.ax.figure.canvas.draw()
                self.ax.figure.canvas.draw()

                self.ax.patches.pop()
                self.ax.patches.pop()
        


        def short_posi_drawer(self,event):
        
            
            if self.check_button_long_n_short_drawer.get_status()[1]:
        
                if event.dblclick:
                            
                    self.xs = event.xdata
                    self.ys = event.ydata
                    
                    self.ratio = 0.333333333333
                    
                    
                    self.cid_mouse_move_short_posi = self.fig.canvas.mpl_connect('motion_notify_event', self.mouse_move_short_posi_drawer)

                    xy = plt.ginput(1)

                    self.fig.canvas.mpl_disconnect(self.cid_mouse_move_short_posi)       
                    
                    rkrwrectprofper = mpl.patches.Rectangle( ( min( event.xdata , xy[0][0] ) , min( event.ydata , xy[0][1] ) ) , 
                                                            np.abs( event.xdata - xy[0][0] ) , np.abs( event.ydata - xy[0][1] ) ,
                                                            angle = 0.0 , color = "lightgreen" , alpha = 0.3 , picker = True )
                    
                    rkrwrectlossper = mpl.patches.Rectangle( ( min( event.xdata , xy[0][0] ) , max( event.ydata , xy[0][1] ) ) , 
                                                            np.abs( event.xdata - xy[0][0] ) , (self.ratio)*( np.abs( event.ydata - xy[0][1] ) ) , 
                                                            angle = 0.0 , color = "lightcoral" , alpha = 0.3 , picker = True )
                    
                    self.ax.add_patch(rkrwrectprofper)
                    self.ax.add_patch(rkrwrectlossper)

                    self.ax.figure.canvas.draw()
                    
                    mpl.backend_bases.NavigationToolbar2(self.fig.canvas).push_current()
                    mpl.backend_bases.NavigationToolbar2(self.fig.canvas).back()
                
                
                else:
                    
                    pass

            else:
                    
                pass
        


        def mouse_move_short_posi_drawer(self,event):
            
            if event.inaxes:
                
                rkrwrectprof = mpl.patches.Rectangle( ( min( event.xdata , self.xs) , min( event.ydata , self.ys ) ) , 
                                                        np.abs(event.xdata - self.xs ) , np.abs(event.ydata - self.ys) ,
                                                        angle = 0.0 , color = "lightgreen" , alpha = 0.3 )
                
                rkrwrectloss = mpl.patches.Rectangle( ( min( event.xdata , self.xs ) , max( event.ydata , self.ys ) ) , 
                                                        np.abs(event.xdata - self.xs) , (self.ratio)*( np.abs(event.ydata - self.ys) ) ,
                                                        angle = 0.0 , color = "lightcoral" , alpha = 0.3 )
                
                self.ax.add_patch(rkrwrectprof)
                self.ax.add_patch(rkrwrectloss)
                
                self.ax.figure.canvas.draw()
                self.ax.figure.canvas.draw()

                self.ax.patches.pop()
                self.ax.patches.pop()




        
        def fib_retrac_drawer(self,event):
            
            if self.check_button_fib_retrac_drawer.get_status()[0]:
                
                if event.dblclick:
                    
                    
                    self.xs = event.xdata
                    self.ys = event.ydata
                    
                    self.cid_mouse_move_fib_retrac_drawer = self.fig.canvas.mpl_connect('motion_notify_event', self.mouse_move_fib_retrac_drawer)
                    
                    xy = plt.ginput(1)
                    
                    self.fig.canvas.mpl_disconnect(self.cid_mouse_move_fib_retrac_drawer)
                    
                    self.ax.axhline( min(event.ydata,xy[0][1]) , picker = True , pickradius = 5 )
                    self.ax.axhline( min(event.ydata,xy[0][1]) + 0.146*( max(event.ydata,xy[0][1]) - min(event.ydata,xy[0][1]) ) , picker = True , pickradius = 5 )
                    self.ax.axhline( min(event.ydata,xy[0][1]) + 0.236*( max(event.ydata,xy[0][1]) - min(event.ydata,xy[0][1]) ) , picker = True , pickradius = 5 )
                    self.ax.axhline( min(event.ydata,xy[0][1]) + 0.382*( max(event.ydata,xy[0][1]) - min(event.ydata,xy[0][1]) ) , picker = True , pickradius = 5 )
                    self.ax.axhline( min(event.ydata,xy[0][1]) + 0.618*( max(event.ydata,xy[0][1]) - min(event.ydata,xy[0][1]) ) , picker = True , pickradius = 5 )
                    self.ax.axhline( max(event.ydata,xy[0][1]) , picker = True , pickradius = 5 )
                    self.ax.axhline( min(event.ydata,xy[0][1]) + 1.618*( max(event.ydata,xy[0][1]) - min(event.ydata,xy[0][1]) ) , picker = True , pickradius = 5 )
                    
                    self.ax.text( min(event.xdata,xy[0][0]) + 2*( max(event.xdata,xy[0][0]) - min(event.xdata,xy[0][0]) ) , min(event.ydata,xy[0][1]) , "0" , fontsize=10 , picker = True )
                    self.ax.text( min(event.xdata,xy[0][0]) + 2*( max(event.xdata,xy[0][0]) - min(event.xdata,xy[0][0]) ) , min(event.ydata,xy[0][1]) + 0.146*( max(event.ydata,xy[0][1]) - min(event.ydata,xy[0][1]) ) , "0.146" , fontsize=10 , picker = True )
                    self.ax.text( min(event.xdata,xy[0][0]) + 2*( max(event.xdata,xy[0][0]) - min(event.xdata,xy[0][0]) ) , min(event.ydata,xy[0][1]) + 0.236*( max(event.ydata,xy[0][1]) - min(event.ydata,xy[0][1]) ) , "0.236" , fontsize=10 , picker = True )
                    self.ax.text( min(event.xdata,xy[0][0]) + 2*( max(event.xdata,xy[0][0]) - min(event.xdata,xy[0][0]) ) , min(event.ydata,xy[0][1]) + 0.382*( max(event.ydata,xy[0][1]) - min(event.ydata,xy[0][1]) ) , "0.382" , fontsize=10 , picker = True )
                    self.ax.text( min(event.xdata,xy[0][0]) + 2*( max(event.xdata,xy[0][0]) - min(event.xdata,xy[0][0]) ) , min(event.ydata,xy[0][1]) + 0.618*( max(event.ydata,xy[0][1]) - min(event.ydata,xy[0][1]) ) , "0.618" , fontsize=10 , picker = True )
                    self.ax.text( min(event.xdata,xy[0][0]) + 2*( max(event.xdata,xy[0][0]) - min(event.xdata,xy[0][0]) ) , max(event.ydata,xy[0][1]) , "1" , fontsize=10 , picker = True )
                    self.ax.text( min(event.xdata,xy[0][0]) + 2*( max(event.xdata,xy[0][0]) - min(event.xdata,xy[0][0]) ) , min(event.ydata,xy[0][1]) + 1.618*( max(event.ydata,xy[0][1]) - min(event.ydata,xy[0][1]) ) , "1.618" , fontsize=10 , picker = True )
                    
                    self.ax.figure.canvas.draw()
                    
                    pass
            
                else:
                    
                    pass
                
            else:
                    
                pass
            



        def mouse_move_fib_retrac_drawer(self,event):
            
            if event.inaxes:

                self.ax.axhline( min(event.ydata,self.ys) , picker = True , pickradius = 5 )
                self.ax.axhline( min(event.ydata,self.ys) + 0.146*( max(event.ydata,self.ys) - min(event.ydata,self.ys) ) , picker = True , pickradius = 5 )
                self.ax.axhline( min(event.ydata,self.ys) + 0.236*( max(event.ydata,self.ys) - min(event.ydata,self.ys) ) , picker = True , pickradius = 5 )
                self.ax.axhline( min(event.ydata,self.ys) + 0.382*( max(event.ydata,self.ys) - min(event.ydata,self.ys) ) , picker = True , pickradius = 5 )
                self.ax.axhline( min(event.ydata,self.ys) + 0.618*( max(event.ydata,self.ys) - min(event.ydata,self.ys) ) , picker = True , pickradius = 5 )
                self.ax.axhline( max(event.ydata,self.ys) , picker = True , pickradius = 5 )
                self.ax.axhline( min(event.ydata,self.ys) + 1.618*( max(event.ydata,self.ys) - min(event.ydata,self.ys) ) , picker = True , pickradius = 5 )
                
                self.ax.figure.canvas.draw()
                self.ax.lines.pop()
                self.ax.lines.pop()
                self.ax.lines.pop()
                self.ax.lines.pop()
                self.ax.lines.pop()
                self.ax.lines.pop()
                self.ax.lines.pop()
                
                pass
                        
            pass





        def on_pick(self,event):

            # the picked object is available as event.artist
            this_artist = event.artist
            
            self.ax.picked_object = this_artist

        


        def on_key(self,event):
                        
            if event.key == u'delete':
                
                if self.ax.picked_object:

                    self.ax.picked_object.remove()
                    self.ax.picked_object = None
                    self.ax.figure.canvas.draw()

except Exception as exp:
    
    print(exp)
    input()
