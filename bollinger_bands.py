# -*- coding: utf-8 -*-
"""
Created on Tue Sep 19 14:01:58 2017
@author: Menna.tarek
"""

import pandas as pd
import datetime
datetime.datetime.strptime
import numpy as np
import Package as PK
import matplotlib.pyplot as plt
from scipy.signal import argrelextrema
from sklearn.svm import SVR


def calculateBollingerBand(values,window):
    rm = values.rolling(window = window,center=False).mean()
    rstd = values.rolling(window= window,center=False).std()
        
    upper_band = rm + (rstd*2)
    lower_band = rm - (rstd*2)
    return upper_band,lower_band,rm

    
        

''' Bollinger Band '''
def get_bollinger_band(stocks,window,startDate,endDate):
    
    bollinger = dict()

    y = ['CloseHighAbove','HighAbove', 'CloseLowUnder', 'LowUnder']
    
    for i in y:
        bollinger[i] = pd.DataFrame(columns = ['stocks'])


    for key, value, in stocks.items():
        
        answer = stocks[key].iloc[::-1]
        
        if (startDate != 0 or endDate !=0):
            answer = answer[(answer['Timestamp'] > startDate) & (answer['Timestamp'] <= endDate)]
            
        upper_band,lower_band,rm = calculateBollingerBand(answer['Trade Close'],window)
        
        
        x = answer.iloc[-1,:]
        uppertoday=upper_band.iloc[-1]
        lowertoday=lower_band.iloc[-1]

        #print(x['Trade Close'])
        if (x['Trade Close'] > uppertoday): 

            bollinger['CloseHighAbove'].loc[len(bollinger['CloseHighAbove'])]=key

            
        elif (x['Trade High'] >uppertoday):
            bollinger['HighAbove'].loc[len(bollinger['HighAbove'])]=key
            
        if(x['Trade Close'] < lowertoday ):
            bollinger['CloseLowUnder'].loc[len(bollinger['CloseLowUnder'])]=key
            
            
        elif(x['Trade Low'] < lowertoday ):
            bollinger['LowUnder'].loc[len(bollinger['LowUnder'])]=key



    writer = pd.ExcelWriter('Bollinger Bands.xlsx')
    for name in bollinger:
        bollinger[name].to_excel(writer,name)

    writer.save()
    return bollinger






def BBW(stocks):
    #writer = pd.ExcelWriter('BBW.xlsx')
    writer2 =pd.ExcelWriter('Stocks Bollinger Band Width.xlsx')
    
    bbw = dict()
    l = []
    
    for key, value in stocks.items():
        stock = stocks[key]
        stock.set_index('Timestamp')
        stock = stock.head(60)
        
        stock = stock.iloc[::-1]
        
        upper_band,lower_band,rm = calculateBollingerBand(stock['Trade Close'],2)
        b = (upper_band-lower_band)/rm
        
        temp=pd.DataFrame({'Timestamp':stock['Timestamp'], 'BBW':b.copy()})
        temp.set_index('Timestamp')
        temp = temp.iloc[::-1]
        
        
        temp['peek'] = 0
        
        
        
        
        
        ''' Getting extrema '''
        
        minimum = np.array(argrelextrema(temp['BBW'].values,np.less,order=2))
        minimum = minimum[0]
        peeks = temp['BBW'].values[minimum]
        
        for i in range (0,len(minimum)-1):
            temp.set_value(minimum[i],['peek'],peeks[i])
        
        minimum = minimum.reshape(len(minimum),1)
        peeks = peeks.reshape(len(peeks),1)
        
        
        temp.iloc[::-1]
 
        '''Regression'''
        svr_rbf = SVR(kernel='rbf', C=10, gamma=0.1)
        y_rbf = svr_rbf.fit(minimum, peeks).predict(minimum)
        
        temp['y_rbf'] = y_rbf[0]
        
        
        ''' Validation '''
        temp['Flag']=0
        for index, row in temp.iterrows():
            if (row['BBW']<=row['y_rbf']):
                 temp.set_value(index, 'Flag', 1, takeable=False)

        '''
        print (key)
        plt.plot(temp['BBW'])
        plt.scatter(minimum,peeks,c='r')
        lw = 2
        plt.plot(minimum, y_rbf, color='navy', lw=lw, label='RBF model')
        plt.show()
        '''
        
       
        ''' Names of stocks going below thw BBW '''
        
        if(temp.iloc[0]['Flag'] == 1 ):
            l.append(key)
            
            

        bbw[key] = temp.copy()
        #bbw[key].to_excel(writer,key) 
        
    df1 = pd.DataFrame({'Stocks': l})
    df1.to_excel(writer2,'StocksBBW')
    
    
    writer2.save()

    return bbw,l



def BBP(stocks):
    writer = pd.ExcelWriter('Bollinger Bands Percentage.xlsx')
    
    df = pd.DataFrame(columns = ['Stock','Band Width Percentage'] )
    for key, value in stocks.items():
        l = [] 
        stock = stocks[key]
        stock = stocks[key].iloc[::-1]
        upper_band,lower_band,rm = calculateBollingerBand(stock['Trade Close'],20)
        B = (stock['Trade Close']  - lower_band) / (upper_band - lower_band)
        
        stock.loc[:, 'Band Width Percentage'] = B
        #stock['Band Width Percentage'] = B
        stock = stock.tail(1)
        stocks[key] = stock
        
        ''' Creating a dataframe holding only Stocks names and there BBP '''
        
        
     
        l.append(key)
        l.append(B.tail(1)[0])
        df.loc[len(df)]=[l[0],l[1]]
        
    df.to_excel(writer,'Bollinger Bands Percentage')
    writer.save()
        
    return df
        




