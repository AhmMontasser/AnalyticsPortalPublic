from plotly.offline import  init_notebook_mode, plot
import plotly.graph_objs as go
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
#import sys
import peakdetect as pDetect
from plotly import tools
import sys
sys.stdout = open('print.txt', 'w')

init_notebook_mode(connected=True)

'''function reading data from excel sheet adding it to a dictionary each one of them is a separate file '''
def readData(path,skiprows):
   parse_date = lambda x: x.strftime('%Y/%m/%d')
   xls = pd.ExcelFile(path)
   stocks={}
   for sh in xls.sheet_names:
       if(sh!='Sheet'):
           stocks[sh]=pd.read_excel(xls,sh, index_col=None,skiprows=skiprows, converters={'Timestamp':parse_date})
           #print(stocks[sh]['Timestamp'])
           stocks[sh]['Timestamp']  = pd.to_datetime(stocks[sh]['Timestamp'])
           #print(stocks[sh]['Timestamp'])
           stocks[sh] = stocks[sh].loc[(stocks[sh]['Timestamp'] > '2016/11/03') & (stocks[sh]['Timestamp'] < '2018/03/30')]
           stocks[sh] = stocks[sh].reset_index(drop=True)
           stocks[sh]=stocks[sh].iloc[::-1]
           #print(stocks[sh]['Timestamp'])
   return stocks
def readDataTimeRange(path,skiprows,start,end):
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
           stocks[sh]=stocks[sh].iloc[::-1]
           #print(stocks[sh]['Timestamp'])
   return stocks
def readStockNamesFile(path):
    xls = pd.ExcelFile(path)
    stockNames3=pd.read_excel(xls,'Sheet1', index_col=None)
    return stockNames3
'''function to add dates to a dataframe'''
def mergeDates(dates,stocks,index):
    stocksNew=dates.merge(stocks,how='left',left_on=index, right_on=index)
    return stocksNew

def get_cmap(n, name='hsv'):
    '''Returns a function that maps each index in 0, 1, ..., n-1 to a distinct 
    RGB color; the keyword argument name must be a standard mpl colormap name.'''
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
            temp.loc[i] = (df.loc[i]-df.loc[i-1])/df.loc[i-1]
    #print temp
        else:
            #print i
            temp.loc[i] = (temp.loc[i]-temp.loc[i])/temp.loc[i]
    #print df
    return temp
def drawAll(df,index,indices,indexData,stockPercentages):
   #start=indexData['Trade Close'].iloc[0]
   fig = tools.make_subplots(rows=3,cols=1,shared_xaxes=True)
   
   for name in indices:
        #weight=start/indices[name]['Trade Close'].iloc[0]
        startIndex=indices[name]['Trade Close'].iloc[0]
        endIndex=indices[name]['Trade Close'].iloc[-1]
        values=[0,(endIndex-startIndex)/startIndex]
        dates=[indices[name]['Timestamp'].iloc[0],indices[name]['Timestamp'].iloc[-1] ]
        '''
        trace_indices = go.Scatter(
                                x=indices[name][index],
                                y=indices[name]['Trade Close'],
                                name = name,
                                visible = "legendonly",
                                opacity = 0.8)
        fig.append_trace(trace_indices, 1, 1)
        '''
        #print (values)
        #print (dates)
        trace_indices = go.Scatter(
                                x=dates,
                                y=values,
                                name = name,
                                visible = "legendonly",
                                opacity = 0.8)
        fig.append_trace(trace_indices, 3, 1)
                #string=
   startIndex=indexData['Trade Close'].iloc[0]
   endIndex=indexData['Trade Close'].iloc[-1]
   values=[0,(endIndex-startIndex)/startIndex]
   dates=[indexData['Timestamp'].iloc[0],indexData['Timestamp'].iloc[-1] ]  
   '''          
   trace_indices = go.Scatter(
                    x=indexData[index],
                    y=indexData['Trade Close'],
                    name = 'EGX30',
                    line = dict(color = 'black'),
                    
                    opacity = 1)
   fig.append_trace(trace_indices, 1, 1)
   '''
   trace_indices = go.Scatter(
                                x=dates,
                                y=values,
                                name = 'EGX30',
                                visible = "legendonly",
                                opacity = 0.8)
   fig.append_trace(trace_indices, 3, 1)
   
   for column in df.columns.values:
        if(column!=index and column != 'Timestamp' and column != 'x'):
            if(column=='index'):
                #string=
                trace_high = go.Scatter(
                                x=df[index],
                                y=df[column],
                                name = 'EGX30',
                                line = dict(color = 'black'),
                                
                                opacity = 1)
                fig.append_trace(trace_high, 2, 1)
            #print column
            else:
                string=" %s - Outperforming %s %% ( %s %% better) - Defensing %s %% ( %s %% better) "%(column,stockPercentages.loc[column,'PercOutPerforming']*100,stockPercentages.loc[column,'PercBetterUp']*100,stockPercentages.loc[column,'PercDefensive']*100,stockPercentages.loc[column,'PercBetterDown']*100)
                trace_high = go.Scatter(
                                x=df[index],
                                y=df[column],
                                name = column,
                                text=string,
                                visible = "legendonly",
                                opacity = 0.8)
                fig.append_trace(trace_high, 2, 1)
            #print data
            
          
   plot(fig, filename='stacked-subplots')
def drawValuesDf(df,index,stockPercentages):
    data=[]
    for column in df.columns.values:
        if(column!=index and column != 'Timestamp' and column != 'x'):
            if(column=='index'):
                #string=
                trace_high = go.Scatter(
                                x=df[index],
                                y=df[column],
                                name = column,
                                line = dict(color = 'black'),
                                
                                opacity = 1)
            #print column
            else:
                string=" %s - Outperforming %s %% ( %s %% better) - Defensing %s %% ( %s %% better) "%(column,stockPercentages.loc[column,'PercOutPerforming']*100,stockPercentages.loc[column,'PercBetterUp']*100,stockPercentages.loc[column,'PercDefensive']*100,stockPercentages.loc[column,'PercBetterDown']*100)
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
    plot(fig, filename = "Manually Set Range funtion")
    return 0

''' Function that returns the highest high for a moving upwards index and lowest low 
     for the moving down index for each stock '''
def HighAndLow(indexPeeks,indexBottoms,indexData,stocks):
    highPeeks = pd.DataFrame(indexPeeks['Timestamp'])
    lowPeeks= pd.DataFrame(indexBottoms['Timestamp'])
    
    highPeeksDates=mergeDates(highPeeks,indexData,'Timestamp')
    highPeeksDates = highPeeksDates.drop(['Trade Open','Trade Low','Trade Close'],axis=1)
    
    
    lowPeeksDates=mergeDates(lowPeeks,indexData,'Timestamp')
    lowPeeksDates = lowPeeksDates.drop(['Trade Open','Trade Close','Trade High'],axis=1)
    

    highPeeks = highPeeksDates.rename(columns = {'Trade High':'index'})
    lowPeeks = lowPeeksDates.rename(columns = {'Trade Low':'index'})
    
    
    for name in stocks:
        if('stocks' in stocks[name].columns):
            del stocks[name]['stocks']
        highPeeksDates=mergeDates(highPeeks,stocks[name],'Timestamp')
        highPeeksDates = highPeeksDates.drop(['Trade Open','Trade Low','Trade Close'],axis=1)
        #print('------------')
        #print(highPeeksDates)
        lowPeeksDates=mergeDates(lowPeeks,stocks[name],'Timestamp')
        lowPeeksDates = lowPeeksDates.drop(['Trade Open','Trade Close','Trade High'],axis=1)
        #print(';;;;;;;')
        #print(lowPeeksDates)
        highPeeks = highPeeksDates.rename(columns = {'Trade High':name})
        lowPeeks = lowPeeksDates.rename(columns = {'Trade Low':name})

    
    frames=[highPeeks,lowPeeks]
    answer = pd.concat(frames)
    answer = answer.sort_values(by='Timestamp',ascending=True)
    answer = answer.reset_index(drop=True)
    return answer 
def HighAndLowSectors(indexPeeks,indexBottoms,indexData,stocksNames,stocks):
    highPeeks = pd.DataFrame(indexPeeks['Timestamp'])
    lowPeeks= pd.DataFrame(indexBottoms['Timestamp'])
        
       
    highPeeksDates=mergeDates(highPeeks,indexData,'Timestamp')
    highPeeksDates = highPeeksDates.drop(['Trade Open','Trade Low','Trade Close'],axis=1)
    
    
    
    lowPeeksDates=mergeDates(lowPeeks,indexData,'Timestamp')
    lowPeeksDates = lowPeeksDates.drop(['Trade Open','Trade Close','Trade High'],axis=1)
    

    highPeeks = highPeeksDates.rename(columns = {'Trade High':'index'})
    lowPeeks = lowPeeksDates.rename(columns = {'Trade Low':'index'})
            
    
    
    for name in stocks:
        highPeeksDates=mergeDates(highPeeks,stocks[name],'Timestamp')
        highPeeksDates = highPeeksDates.drop(['Trade Open','Trade Low','Trade Close'],axis=1)
        
        lowPeeksDates=mergeDates(lowPeeks,stocks[name],'Timestamp')
        lowPeeksDates = lowPeeksDates.drop(['Trade Open','Trade Close','Trade High'],axis=1)
        
        highPeeks = highPeeksDates.rename(columns = {'Trade High':name})
        lowPeeks = lowPeeksDates.rename(columns = {'Trade Low':name})

    #print(highPeeks)
    #print(lowPeeks)
    frames=[highPeeks,lowPeeks]
    answer = pd.concat(frames)
    #print(answer)
    answer = answer.sort_values(by='Timestamp',ascending=True)
    answer = answer.reset_index(drop=True)
    return answer 
def performance(stocksPeeks,periodsIndex):
    #copy stocksPeeks in temp to add the value col to it
    temp = stocksPeeks.copy()
    #print(temp)
    #concatenate the value column to temp dataframe
    temp = pd.concat([temp, periodsIndex['value'].astype(int)], axis=1)
    #temp['value'] = (temp['value']).astype(int)
    #temp.drop('Timestamp', axis=1)
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
    #print (temp)
    for column in temp.columns.values:
        s = pd.Series()
        
        if(column != 'value' and column != 'index' and column != 'Timestamp' and column != 'Trade Volume'):
            upProfit= 0
            downProfit=0
            totalPositive=0
            totalNegative=0
            #print (column)
            for index,row in temp.iterrows():
                
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
                #print(prev)
                #print(prevIndex)
                #print('----------------')
                #print(column)
                #print(index)
                #print(current)
                if(pd.notnull(current) and pd.notnull(prev)):
                    #stockProfit=(current-prev)/prev
                    #indexProfit=(currentIndex-prevIndex)/prevIndex
                    
                    #print (current) 
                    #print(currentIndex)
                    #print (value)
                    if (value==1.0):
                        #print ('hereeeeeee')
                        totalPositive+=1
                        if(current>currentIndex):
                            #print(stockProfit)
                            #print(indexProfit)
                            #print ('hereeeeeee')
                            
                            s['PercOutPerforming']= s['PercOutPerforming']+1
                            #print(index)
                            result=current-currentIndex
                            #print(s['PercOutPerforming'])
                            upProfit+=result
                            
                    elif (value==-1):
                        totalNegative+=1
                        if(current>currentIndex):
                            #print ('hereeeeeee2')
                            s['PercDefensive']=s['PercDefensive']+1
                            downProfit+=(current-currentIndex)
                        
            
            if(s['PercDefensive']!=0):
                s['PercBetterDown']=downProfit/s['PercDefensive']
            else:
                s['PercBetterDown']=0
                
            if(s['PercOutPerforming']!=0):
                s['PercBetterUp']=upProfit/s['PercOutPerforming']
            else:
                s['PercBetterUp']=0    
                
            #print(totalPositive)
            #print(totalNegative)
            #print(s['PercOutPerforming'])
            #print(s['PercDefensive'])
            s['PercOutPerforming']= s['PercOutPerforming']/totalPositive
            s['PercDefensive']= s['PercDefensive']/totalNegative
            #print(s['PercOutPerforming'])
            #print(s['PercDefensive'])
            perf.loc[column]=s.copy()
            #print (perf)
            s = pd.Series()
            
    return perf 
   
def getPeeksandBottoms(indexData,lookahead,delta,stocks):
    positive, negative = pDetect.peakdetect(indexData['Trade High'], x_axis = indexData.index.values , lookahead=lookahead, delta=delta)
    x, y = zip(*positive)
    positive, negative = pDetect.peakdetect(indexData['Trade Low'], x_axis = indexData.index.values ,  lookahead=lookahead, delta=delta)
    xmin, ymin = zip(*negative)
    
    
    ''' Getting peaks from index data in a new data frame indexPeeks '''
    indexPeeks=indexData[indexData.index.isin(x)]
    indexPeeks['value']=1
    indexPeeks['real']=indexPeeks.index
    
    
    ''' Getting Buttoms from index data in a new data frame indexBottoms '''
    indexBottoms=indexData[indexData.index.isin(xmin)]
    indexBottoms['value']=-1
    indexBottoms['real']=indexBottoms.index
    #print(indexBottoms)
    
    
    stocksPeeks= HighAndLow(indexPeeks,indexBottoms,indexData,stocks)
    
    #print(stocksPeeks)
    ''' merging indexPeeks and indexBottoms into periodsIndex DataFrame  '''
    periodsIndex=pd.merge(indexPeeks,indexBottoms,how='outer',sort=True)
    #print(periodsIndex)
    #periodsIndex=periodsIndex.iloc[::-1]
    periodsIndex=periodsIndex.reset_index(drop=True)
    #print(periodsIndex)
    return [periodsIndex,stocksPeeks]
            
def minimizeStocks(datesMain,stocks):
    ''' for loop to minimize stocks to only the value of peeks and bottoms of the index   '''
    for name in stocks:
        stocks[name]=mergeDates(datesMain,stocks[name],'Timestamp')
        stocks[name].fillna(method='ffill',inplace=True)

def stockProfitPeriod(periodsIndex,stocks,periods):
    ''' for loop to calculate stock profit in each period  '''   
    #print (stocks)
    for index,row in periodsIndex.iterrows():
        if(index==0):
            start=row['Timestamp']
            startReal=periodsIndex.at[index,'real']
            #print(startReal)
            startIndex=index
        else:
            end=row['Timestamp']
            endIndex=index
            endReal=periodsIndex.at[index,'real']
            if(periodsIndex.at[endIndex,'value']==-1):
                percentage=(periodsIndex.at[endIndex,'Trade Low']-periodsIndex.at[startIndex,'Trade High'])/periodsIndex.at[startIndex,'Trade High']
            else:
                percentage=(periodsIndex.at[endIndex,'Trade High']-periodsIndex.at[startIndex,'Trade Low'])/periodsIndex.at[startIndex,'Trade Low']
    
            name= "%s-%s(%s)"%(start,end,percentage*100)
            columns = ['stock-profit','better']
            indexNames=stocks.keys()
            period= pd.DataFrame(index=indexNames, columns=columns)
            #print(stocks)
            for stockName in stocks:
                
                
                #print(stockName)
                high=stocks[stockName].at[startReal,'Trade High']
                low=stocks[stockName].at[startReal,'Trade Low']
                #print(startReal)
                #print(endReal+1)
                for i in range(startReal,endReal+1):
                    #print(i)
                    if stocks[stockName].at[i,'Trade High']>high:high=stocks[stockName].at[i,'Trade High']
                    if stocks[stockName].at[i,'Trade Low']<low:low=stocks[stockName].at[i,'Trade Low']
          
                stockPercentage=((high-low)/high)*100
                period.at[stockName,'stock-profit']=stockPercentage
                
                if(percentage*100 > stockPercentage):
                    period.at[stockName,'better']=-1
                else:
                    period.at[stockName,'better']=1
                
            periods[name]=period   
            start=row['Timestamp']
            startIndex=endIndex
            startReal=endReal

def prepareDrawing(stocksPeeks):
    
    dates=pd.DataFrame(stocksPeeks['Timestamp'])
    #print(stocksPeeks['Timestamp'])
    stocksPeeks=stocksPeeks.drop(['Timestamp'],axis=1)
    
    normalizedStocks=normalizePeriods(stocksPeeks)
    
    stocksPeeks['Timestamp']=dates['Timestamp']  
    middleValuesStocks=normalizedStocks.copy()
    normalizedStocks=normalizedStocks.loc[np.repeat(normalizedStocks.index.values,3)]
    dates=dates.loc[np.repeat(dates.index.values,3)]
    dates=dates.reset_index(drop=True)
    dates=dates.drop(dates.index[0])
    #print(normalizedStocks)
    normalizedStocks=normalizedStocks.reset_index(drop=True)
    normalizedStocks=normalizedStocks.drop(normalizedStocks.index[0])
    normalizedStocks=normalizedStocks.drop(normalizedStocks.index[0])
    #normalizedStocks['x']=normalizedStocks.index;
    #middleValuesStocks=normalizedStocks.copy()
    normalizedStocks['Timestamp']=dates['Timestamp']
    #middleValuesStocks=normalizedStocks.copy()
    ''' add zeros and nulls to zraw  '''
    for i in range(5,len(normalizedStocks.index),3):
        normalizedStocks.ix[i, normalizedStocks.columns != 'Timestamp']=0
        
        old_date=normalizedStocks.ix[i, normalizedStocks.columns == 'Timestamp']
        date = pd.to_datetime(old_date, format="%Y/%m/%d")
        #print (date)
        modified_date = date + timedelta(days=1)
        #print(modified_date)
        
        #dt_obj = datetime.strptime(modified_date,"%Y/%m/%d")
        normalizedStocks.ix[i, normalizedStocks.columns == 'Timestamp']=modified_date
        #print(row)
        #normalizedStocks.loc[i]=row
        
    for i in range(3,len(normalizedStocks.index),3):
        row=normalizedStocks.loc[i]
        #row['x']=i
        normalizedStocks.loc[i]=row
    for i in range(4,len(normalizedStocks.index),3):
    
        normalizedStocks.ix[i, normalizedStocks.columns != 'Timestamp']=None
        
        row=normalizedStocks.loc[i]
        #row['x']=i-1
        #row['Timestamp']=normalizedStocks.at[i,'Timestamp']
        normalizedStocks.loc[i]=row
    
    
    return  [normalizedStocks,middleValuesStocks]



        

        

                 