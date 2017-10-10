# -*- coding: utf-8 -*-
"""
Created on Wed Sep 06 13:18:02 2017

@author: Menna.tarek
"""
from plotly.offline import  init_notebook_mode, plot
import plotly.graph_objs as go
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def readDataDates(path,skiprows,start,end):
   parse_date = lambda x: x.strftime('%Y/%m/%d')
   xls = pd.ExcelFile(path)
   stocks={}
   for sh in xls.sheet_names:
       if(sh!='Sheet'):
           stocks[sh]=pd.read_excel(xls,sh, index_col=None,skiprows=skiprows, converters={'Timestamp':parse_date})
           #print(stocks[sh]['Timestamp'])
           stocks[sh]['Timestamp']  = pd.to_datetime(stocks[sh]['Timestamp'])
           #print(stocks[sh]['Timestamp'])
           stocks[sh] = stocks[sh].loc[(stocks[sh]['Timestamp'] > start) & (stocks[sh]['Timestamp'] < end)]
           stocks[sh] = stocks[sh].reset_index(drop=True)
           #stocks[sh]=stocks[sh].iloc[::-1]
           #print(stocks[sh]['Timestamp'])
   return stocks
def readData(path,skiprows):
  parse_date = lambda x: x.strftime('%Y/%m/%d')
  xls = pd.ExcelFile(path)
  stocks={}
  for sh in xls.sheet_names:
      if(sh != 'Sheet'):
           stocks[sh]=pd.read_excel(xls,sh, index_col=None,skiprows=skiprows, converters={'Date (GMT)':parse_date})
  return stocks

'''function to add dates to a dataframe'''
def mergeDates(dates,stocks,index):
    stocksNew=dates.merge(stocks,how='left',left_on=index, right_on=index)
    return stocksNew

'''Returns a function that maps each index in 0, 1, ..., n-1 to a distinct 
    RGB color; the keyword argument name must be a standard mpl colormap name.'''
def get_cmap(n, name='hsv'):
    return plt.cm.get_cmap(name, n)

'''Default normalization function on all periods at once'''
def normalize(df):
    return df/df.ix[0,:]

'''normalize data on each period alone'''
def normalizePeriods(df):
    temp = df.copy()
   # print len(df.index)
    for i in range(0,len(df.index)) :
        if i != 0 :
            temp.loc[i] = df.loc[i]/df.loc[i-1]
    #print temp
        else:
            #print i
            temp.loc[i] = temp.loc[i]/temp.loc[i]
    #print df
    return temp
def rolMean(df,window):
    for column in df.columns.values:
        if (column != 'Date (GMT)' and column != 'Index') and column != 'Date' and column != 'Last':
            df[column]=pd.rolling_mean(df[column], window=20)
    return df

def drawValuesDf(df,index,stockPercentages):
    data=[]
    for column in df.columns.values:
        if(column!=index and column != 'Date (GMT)' and column != 'x'):
            if(column=='index'):
                trace_high = go.Scatter(
                                x=df[index],
                                y=df[column],
                                name = column,
                                line = dict(color = 'black'),
                                
                                opacity = 1)
            #print column
            else:
                string=" %s - Outperforming %s %% - Defensing %s %%"%(column,stockPercentages.loc[column,'PercOutPerforming']*100,stockPercentages.loc[column,'PercDefensive']*100)
                trace_high = go.Scatter(
                                x=df[index],
                                y=df[column],
                                name = column,
                                text=string,
                                visible = "legendonly",
                                opacity = 0.8)
            
            #print data
            data.append(trace_high)
    #print data
    layout = dict(
        title = "Index Vs Stocks"
        
    )
    
    fig = dict(data=data, layout=layout)
    plot(fig, filename = "Manually Set Range funtion",auto_open = True)
    return 0


''' Function that returns the highest high for a moving upwards index and lowest low 
     for the moving down index for each stock '''


def performance(stocksPeeks,periodsIndex):
    #copy stocksPeeks in temp to add the value col to it
    temp = stocksPeeks.copy()
    
    #concatenate the value column to temp dataframe
    temp = pd.concat([temp, periodsIndex['value'].astype(int)], axis=1)
    #temp['value'] = (temp['value']).astype(int)
    #temp.drop('Date (GMT)', axis=1)
    #returns a list of the stock names (header names) 
    x = list(temp)
    #x = x[:-1]
    #x.pop(0)
    perf =  pd.DataFrame(index=x,columns = ['PercOutPerforming','PercDefensive','PercBetterUp','PercBetterDown'],dtype=float)
    perf = perf.fillna(0)
    
    #problems from here
    '''
    for index,row in temp.iterrows():
        value = temp.iloc[index]['value']
        if (value==1):
    '''
    for column in temp.columns.values:
        s = pd.Series()
        if(column != 'value'):
            upProfit= 0
            downProfit=0
            total =0
            for index,row in temp.iterrows():
                total+=1
                value = row['value']
                current=temp.iloc[index][column]
                
                currentIndex=temp.iloc[index]['index']
                
               
                if (index != 0):
                    prev=temp.iloc[index-1][column]
                    prevIndex=temp.iloc[index-1]['index']
                elif(index == 0):
                    prev=0
                    prevIndex=0
                    s['PercOutPerforming']=0.0
                    s['PercBetterUp']=0.0
                    s['PercBetterDown']=0.0
                    s['PercDefensive']=0.0
                    #s.astype(float)
                    
                stockProfit=current-prev
                indexProfit=currentIndex-prevIndex
                
                if (value==1):
                    if(stockProfit>indexProfit):
                        s['PercOutPerforming']= s['PercOutPerforming']+1
                        result=stockProfit-indexProfit
                        upProfit+=result
                        
                elif (value==-1):
                    if(stockProfit>indexProfit):
                        s['PercDefensive']=s['PercDefensive']+1
                        downProfit+=(stockProfit-indexProfit)
                        
            
            if(s['PercDefensive']!=0):
                s['PercBetterDown']=downProfit/s['PercDefensive']
            else:
                s['PercBetterDown']=0
                
            if(s['PercOutPerforming']!=0):
                s['PercBetterUp']=upProfit/s['PercOutPerforming']
            else:
                s['PercBetterUp']=0    
                
                
            s['PercOutPerforming']= s['PercOutPerforming']/total
            s['PercDefensive']= s['PercDefensive']/total
            
            perf.loc[column]=s.copy()
            print( perf)
            s = pd.Series()
            
    return perf 
   


def prepareDrawing(stocksPeeks):
    
    dates=stocksPeeks['Date (GMT)']
    stocksPeeks=stocksPeeks.drop(['Date (GMT)'],axis=1)
    
    normalizedStocks=normalizePeriods(stocksPeeks)
    stocksPeeks['Date (GMT)']=dates  
    middleValuesStocks=normalizedStocks
    normalizedStocks=normalizedStocks.loc[np.repeat(normalizedStocks.index.values,3)]
    dates=dates.loc[np.repeat(dates.index.values,3)]
    dates=dates.reset_index(drop=True)
    dates=dates.drop(dates.index[0])
    
    normalizedStocks=normalizedStocks.reset_index(drop=True)
    normalizedStocks=normalizedStocks.drop(normalizedStocks.index[0])
    normalizedStocks=normalizedStocks.drop(normalizedStocks.index[0])
    normalizedStocks['x']=normalizedStocks.index;
    
    ''' add zeros and nulls to zraw  '''
    for i in range(5,len(normalizedStocks.index),3):
        normalizedStocks.loc[i] =1
        row=normalizedStocks.loc[i]
        row['x']=normalizedStocks.loc[i-2,'x']+0.01
        normalizedStocks.loc[i]=row
        
    for i in range(3,len(normalizedStocks.index),3):
        row=normalizedStocks.loc[i]
        row['x']=i
        normalizedStocks.loc[i]=row
    for i in range(4,len(normalizedStocks.index),3):
    
        normalizedStocks.loc[i]=None
        row=normalizedStocks.loc[i]
        row['x']=i-1
        normalizedStocks.loc[i]=row
    
    normalizedStocks['Date (GMT)']=dates
    return  [normalizedStocks,middleValuesStocks]


def getStockValue(sectors,stocks,dates,indexData,indexType,writer,sharesdata):
    data=[]
    #indexData=indexData.iloc[::-1]
    indexStartClose=indexData.iloc[-1, indexData.columns.get_loc('Trade Close')]
    #print(indexData)
    indexStartOpen=indexData.iloc[-1, indexData.columns.get_loc('Trade Open')]
    indexStartLow=indexData.iloc[-1, indexData.columns.get_loc('Trade Low')]
    indexStartHigh=indexData.iloc[-1, indexData.columns.get_loc('Trade High')]
    indices={}
    for name in sectors:
        tempClose=pd.DataFrame(dates['Timestamp'])
        tempOpen=pd.DataFrame(dates['Timestamp'])
        tempHigh=pd.DataFrame(dates['Timestamp'])
        tempLow=pd.DataFrame(dates['Timestamp'])
        if(indexType==3):
            tempCap=pd.DataFrame(dates['Timestamp'])
        nSTocks=len(sectors[name])
        nameSTocks=pd.DataFrame(sectors[name]['stocks'])
        
        #print(nSTocks)
        for i,row in sectors[name].iterrows():
          stockName=row['stocks']
          if stockName in stocks:
              stock=stocks[stockName].copy()
              #print( type(stock['Date (GMT)']))
              stock['Timestamp'] = pd.to_datetime(stock['Timestamp']) 
              
              stock=mergeDates(dates,stock,'Timestamp')
              stock=stock.fillna(method='ffill')
              stock=stock.fillna(method='bfill')
              stock=stock.reset_index(drop=True)
              #print(stock)
              if(indexType==3):
                      shares=sharesdata.loc[sharesdata['.EGX100'] == stockName, 'Company Shares'].item()
                      #print('shares--------------------------')
                      #print(shares)
                      tempCap[stockName]=stock['Trade Close'].map(lambda x: x*pd.to_numeric(shares))
                      #print('tempCap--------------------------')
                      #print(tempCap)
              tempClose[stockName]=stock['Trade Close']
              tempLow[stockName]=stock['Trade Low']
              tempOpen[stockName]=stock['Trade Open']
              tempHigh[stockName]=stock['Trade High']
        if(indexType!=2):          
            tempClose['totalPrice']=tempClose.sum(axis=1)
            tempLow['totalPrice']=tempLow.sum(axis=1)
            tempOpen['totalPrice']=tempOpen.sum(axis=1)
            tempHigh['totalPrice']=tempHigh.sum(axis=1)
        
        if(indexType==3):
            tempCap['totalCap']=tempCap.sum(axis=1)
        #print(tempClose.iloc[-1, tempClose.columns.get_loc('totalPrice')])
        #print(indexStartClose)
        if(indexType==1):
            index=pd.DataFrame(dates['Timestamp'])
            index['Trade Close']=(tempClose['totalPrice']/nSTocks)
            index['old Close']=index['Trade Close']
            #print(name)
            #print(index.iloc[-1, index.columns.get_loc('Trade Close')])
            index['Trade Close']=(index['Trade Close']/index.iloc[-1, index.columns.get_loc('Trade Close')])*indexStartClose
            close=index['Trade Close']
            
            index['Trade Open']=(tempOpen['totalPrice']/nSTocks)
            index['Trade Open']=(index['Trade Close']*index['Trade Open'])/index['old Close']
            index['Trade High']=(tempHigh['totalPrice']/nSTocks)
            index['Trade High']=(index['Trade Close']*index['Trade High'])/index['old Close']
            index['Trade Low']=(tempLow['totalPrice']/nSTocks)
            index['Trade Low']=(index['Trade Close']*index['Trade Low'])/index['old Close']
            del index['Trade Close']
            del index['old Close']
            index['Trade Close']=close
            index['stocks']=nameSTocks['stocks']
        elif(indexType==2):
            index=pd.DataFrame(dates['Timestamp'])
            index['Trade open'] =0
            index['Trade High'] =0
            index['Trade Low'] =0
            index['Trade Close'] =0
            for column in tempClose:
                
                index['Trade open'] += tempOpen[column]/nSTocks
                index['Trade High'] += tempHigh[column]/nSTocks
                index['Trade Low'] += tempLow[column]/nSTocks
                index['Trade Close'] += tempClose[column]/nSTocks
            #index['Trade Close']=tempClose['totalPrice']
            #index['old Close']=index['Trade Close']
            #print(name)
            #print(index.iloc[-1, index.columns.get_loc('Trade Close')])
            index['Trade Close']=(index['Trade Close']/index.iloc[-1, index.columns.get_loc('Trade Close')])*indexStartClose
            index['Trade Open']=(index['Trade Open']/index.iloc[-1, index.columns.get_loc('Trade Close')])*indexStartClose
            index['Trade High']=(index['Trade Close']/index.iloc[-1, index.columns.get_loc('Trade Close')])*indexStartClose
            index['Trade Low']=(index['Trade Close']/index.iloc[-1, index.columns.get_loc('Trade Close')])*indexStartClose
            
            index['stocks']=nameSTocks['stocks']
        elif(indexType==3):
            
            index=pd.DataFrame(dates['Timestamp'])
            totalCap=tempCap.pop('totalCap')
            timestamp=tempCap.pop('Timestamp')
            #print('totalCap--------------------------')
            
            tempCap=tempCap.div(totalCap, axis=0)
            tempCap['Timestamp']=timestamp
            #print(tempCap)
            for column in tempCap:
                if(column!='Timestamp'):
                    #tempCap[column]/=tempCap['totalCap']
                    tempClose[column]=tempClose[column]*tempCap[column]
                    tempLow[column]=tempLow[column]*tempCap[column]
                    tempHigh[column]=tempHigh[column]*tempCap[column]
                    tempOpen[column]=tempOpen[column]*tempCap[column]
            #print(tempCap)
            index['Trade Open']= tempOpen.sum(axis=1)
            index['Trade High']= tempHigh.sum(axis=1)
            index['Trade Low']= tempLow.sum(axis=1)
            index['Trade Close']= tempClose.sum(axis=1)
            
            percentage=index.iloc[-1, index.columns.get_loc('Trade Close')]/indexStartClose
            index['Trade Open']= index['Trade Open'].map(lambda x: x/percentage)
            index['Trade High']= index['Trade High'].map(lambda x: x/percentage)
            index['Trade Low']= index['Trade Low'].map(lambda x: x/percentage)
            index['Trade Close']= index['Trade Close'].map(lambda x: x/percentage)
            
        #print(indexStartClose)
        #print(indexStartHigh)
        indices[name]=index
        print(name)
        print(index)
        indices[name].to_excel(writer,name)
        trace_high = go.Scatter(
                                x=indices[name]['Timestamp'],
                                y=indices[name]['Trade Close'],
                                name = name,
                                visible = "legendonly",
                                opacity = 0.8)   
        data.append(trace_high)
        #return tempClose,tempHigh,tempLow,tempOpen
    indexData.to_excel(writer,'EGX30')
    trace_high = go.Scatter(
                                    x=indexData['Timestamp'],
                                    y=indexData['Trade Close'],
                                    name = 'Index',
                                    #visible = "legendonly",
                                    opacity = 0.8)   
    data.append(trace_high)
    layout = dict(
            title = "Index Vs Indices"
            
        )
    #sectors.to_excel(writer,'stocks of sectors')    
    fig = dict(data=data, layout=layout)
    plot(fig, filename = "Index Vs Indices")    
    return indices
        
 
