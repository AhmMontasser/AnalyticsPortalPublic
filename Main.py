import flask
from flask import Flask
from flask import request
from flask import render_template

from plotly.offline import  plot
import plotly.graph_objs as go
import pandas as pd
import datetime
datetime.datetime.strptime
from plotly import tools
import Package as PK
import sys
import DataComposition as tc
import indexReader as ir 

app = Flask(__name__)





def readStocks(path,skiprows):
   #parse_date = lambda x: x.strftime('%Y/%m/%d')
   xls = pd.ExcelFile(path)
   stocks={}
   for sh in xls.sheet_names:
       if(sh!='Sheet'):
           stocks[sh]=pd.read_excel(xls,sh, index_col=None,skiprows=skiprows)
           #print(stocks[sh]['Timestamp'])
   return stocks



''' Home page '''
def mergeDates(dates,stocks,index):
    stocksNew=dates.merge(stocks,how='left',left_on=index, right_on=index)
    return stocksNew

''' Index '''
@app.route("/", methods=['GET'])
def Index():
    return render_template("Index.html")

    


''' Page for Composition Data '''
@app.route("/DataComposition", methods=['POST','GET'])
def DataComposition():
    if request.method == 'GET':
        return render_template("DataComposition.html")
    
    else:
        startDate = request.form['start_date']
        endDate = request.form['end_date']
        indexFile = PK.readData('indexLiveUpdate.xlsx',2)
        indexData=indexFile['.EGX30']
        indexData.rename(columns={'Timestamp': 'Date (GMT)'} , inplace=True)
        indexData['Date (GMT)'] = pd.to_datetime(indexData['Date (GMT)'], format="%Y/%m/%d")
        
        
        CompositionData = tc.dataProcessing ('Trading Flow.csv', startDate,endDate)
        CompositionData = pd.merge(indexData, CompositionData, left_on = 'Date (GMT)' ,right_on = 'Date')
        CompositionData = CompositionData.iloc[::-1]

        tc.draw(CompositionData)
     
        
        
        
        
        
        
        return render_template("DataComposition.html")
    




@app.route("/Performance")
def Performance():
        return render_template("Performance.html")










@app.route("/SectorPerformance", methods=['POST','GET'])
def SectorPerformance():
    if request.method == 'GET':
        
        stocks = ir.readData('sectorIndices.xlsx',0)
        sectors = stocks.keys()
        return render_template("SectorPerformance.html",sectors=sectors)
    
    else:
        startDate = request.form['start_date']
        endDate = request.form['end_date']
        names = request.form.getlist('names')
        
        periods = {}
 
        
        ''' reading Index data base in indexData and  '''
        indexFile = ir.readData('/home/pharos/python_projects/data/indexLiveUpdate.xlsx',2)
        stocks = ir.readData('sectorIndices.xlsx',0)
        
        indexData=indexFile['.EGX30']
        del indexData['Trade Volume']
        indexData = indexData[(indexData['Timestamp'] > startDate) & (indexData['Timestamp'] <= endDate)]
        
        stocks = {key: stocks[key] for key in stocks if key in names}
        
        #Getting desired peeks and bottoms  
        periodsIndex,stocksPeeks=ir.getPeeksandBottoms(indexData,3,15,stocks)
        
        dates=pd.DataFrame(indexData['Timestamp'])
        ir.minimizeStocks(dates,stocks) 
        dates=pd.DataFrame(periodsIndex['Timestamp'])
        
        
        
        
        ir.stockProfitPeriod(periodsIndex,stocks,periods)
        
        drawingStocks,normalizedStocks=ir.prepareDrawing(stocksPeeks)
        
        stockPercentages=ir.performance(normalizedStocks,periodsIndex)
    

        ir.drawAll(drawingStocks,'Timestamp',stocks,indexData,stockPercentages)
        
        
        
        
        ''' Savimg in an excel file '''
        writer = pd.ExcelWriter('output.xlsx')
        indexData.to_excel(writer,'EGX30')
        
        for key in stocks:
            stocks[key].to_excel(writer,key)
        
        
        
        
        
        
        return render_template("SectorPerformance.html")
        
        
        
        

        
        
    

@app.route("/StockPerformance", methods=['POST','GET'])
def StockPerformance():
    if request.method == 'GET':
        stocks = ir.readData('stockLiveUpdate.xlsx',2)
        sectors = stocks.keys()
        return render_template("StockPerformance.html",sectors=sectors)
    
    else:
        startDate = request.form['start_date']
        endDate = request.form['end_date']
        names = request.form.getlist('names')
        

        periods = {}        
        ''' reading Index data base in indexData and  '''
        stocks = ir.readData('/home/pharos/python_projects/data/stockLiveUpdate.xlsx',2)
        indexFile = ir.readData('/home/pharos/python_projects/data/indexLiveUpdate.xlsx',2)
        
        #print(indexFile)
        indexData=indexFile['.EGX30']
        indexData = indexData[(indexData['Timestamp'] > startDate) & (indexData['Timestamp'] <= endDate)]
        stocks = {key: stocks[key] for key in stocks if key  in names}
        #indexStart=(indexData['Trade Close']/index.iloc[-1, index.columns.get_loc('Trade Close')])*indexStartClose
        #Getting desired peeks and bottoms  
        periodsIndex,stocksPeeks=ir.getPeeksandBottoms(indexData,3,15,stocks)
        dates=pd.DataFrame(indexData['Timestamp'])
        ir.minimizeStocks(dates,stocks) 
        dates=pd.DataFrame(periodsIndex['Timestamp']) 
        ir.stockProfitPeriod(periodsIndex,stocks,periods)
        drawingStocks,normalizedStocks=ir.prepareDrawing(stocksPeeks)
        stockPercentages=ir.performance(normalizedStocks,periodsIndex)
 
        ir.drawAll(drawingStocks,'Timestamp',stocks,indexData,stockPercentages)
  
        
        
        
        
        ''' Savimg in an excel file '''
        writer = pd.ExcelWriter('output.xlsx')
        indexData.to_excel(writer,'EGX30')
        
        for key in stocks:
            stocks[key].to_excel(writer,key)
        
        
        
        
        
        return render_template("StockPerformance.html")
        


@app.route("/SectorIndices", methods=['POST','GET'])
def SectorIndices():
    if request.method == 'GET':
        return render_template("SectorIndices.html")
    
    else:
        #startDate = request.form['start_date']
        #endDate = request.form['end_date']
        sectorName = request.form['SectorName']
        #stocks = request.form.getlist('SectorStocks')
        temp = pd.DataFrame({'stocks':request.form.getlist('SectorStocks')})
        sectors[sectorName]=temp
        writer = pd.ExcelWriter('sectorStocks.xlsx')  
        for name in sectors:
            sectors[name].to_excel(writer,name)
        writer.save() 
        '''
        indexData.rename(columns={'Timestamp': 'Date (GMT)'} , inplace=True)
        indexData['Date (GMT)'] = pd.to_datetime(indexData['Date (GMT)'], format="%Y/%m/%d")
        CompositionData = tc.dataProcessing ('Trading Flow.csv', startDate,endDate)
        CompositionData = pd.merge(indexData, CompositionData, left_on = 'Date (GMT)' ,right_on = 'Date')
        CompositionData = PK.rolMean(CompositionData,20)
        tc.draw(CompositionData)
        #writing to wxcel file 
        writer = pd.ExcelWriter('output.xlsx')
        CompositionData.to_excel(writer,'DataComposition')
        writer.save()
        return render_template("DataComposition.html")
        '''
        return render_template("SectorIndices.html")



@app.route("/AllSectors", methods=['POST','GET'])
def AllSectors():
    sectors = readStocks('sectorStocks.xlsx',0)
    if request.method == 'GET':
        #sectors = readStocks('sectorStocks.xlsx',0)
        larger=0
        for name in sectors:
            if(larger<sectors[name].count().max()):
                larger=sectors[name].count().max()
        nColumns=len(sectors.keys())
        sectorstemp=pd.DataFrame(pd.np.empty((larger,nColumns))* 0,columns=sectors.keys()) 
        for name in sectors:
            sectorstemp[name]=sectors[name]['stocks']
        sectorstemp.fillna(0, inplace=True)
        return render_template("AllSectors.html",sectors=sectorstemp)
    
    else:
        sectors2={}
        
        writer = pd.ExcelWriter('sectorStocks.xlsx')  
        for name in sectors:
            temp = pd.DataFrame({'stocks':request.form.getlist(name)})
            #temp.rename('0':'stocks')
            sectors2[name]=temp
            print(request.form.getlist(name))
            sectors2[name].to_excel(writer,name)
        writer.save() 
        sectors = readStocks('sectorStocks.xlsx',0)
        larger=0
        for name in sectors:
            if(larger<sectors[name].count().max()):
                larger=sectors[name].count().max()
        nColumns=len(sectors.keys())
        sectorstemp=pd.DataFrame(pd.np.empty((larger,nColumns))* 0,columns=sectors.keys()) 
        for name in sectors:
            sectorstemp[name]=sectors[name]['stocks']
        sectorstemp.fillna(0, inplace=True)
        #startDate = request.form['start_date']
        #endDate = request.form['end_date']
        #sectorName = request.form['SectorName']
        #stocks = request.form.getlist('SectorStocks')

        #print(stocks, file=sys.stderr)
        '''
        indexData.rename(columns={'Timestamp': 'Date (GMT)'} , inplace=True)
        indexData['Date (GMT)'] = pd.to_datetime(indexData['Date (GMT)'], format="%Y/%m/%d")
        CompositionData = tc.dataProcessing ('Trading Flow.csv', startDate,endDate)
        CompositionData = pd.merge(indexData, CompositionData, left_on = 'Date (GMT)' ,right_on = 'Date')
        CompositionData = PK.rolMean(CompositionData,20)
        tc.draw(CompositionData)
        #writing to wxcel file 
        writer = pd.ExcelWriter('output.xlsx')
        CompositionData.to_excel(writer,'DataComposition')
        writer.save()
        return render_template("DataComposition.html")
        '''
        return render_template("AllSectors.html",sectors=sectorstemp)


@app.route("/GenerateIndices", methods=['POST','GET'])
def GenerateIndices():
    if request.method == 'GET':
        
        return render_template("GenerateIndices.html",done=0)
    
    else:
        
        start = request.form['start_date']
        end= request.form['end_date']
        #print(start)
        #print(end)
        #sectorName = request.form['SectorName']
        #stocks = request.form.getlist('SectorStocks')
        indexFile = PK.readDataDates('/home/pharos/python_projects/data/indexLiveUpdate.xlsx',2,start,end)
        
        stocks = PK.readDataDates('/home/pharos/python_projects/data/stockLiveUpdate.xlsx',2,start,end)
        indexData=indexFile['.EGX30']
        #print(indexData)
        dates=pd.DataFrame(indexData['Timestamp']) 
        writer = pd.ExcelWriter('sectorIndices.xlsx')
        cap = PK.readData('/home/pharos/python_projects/data/EGX 100 Cap.xlsx',1)
        sharesdata=cap['Sheet1'].copy()
        sharesdata['.EGX100']=sharesdata['.EGX100'].map(lambda x: x.replace('.CA',''))
        #print(sectors)
        PK.getStockValue(sectors,stocks,dates,indexData,1,writer,sharesdata)
        writer.save()
        #print(stocks, file=sys.stderr)
        '''
        indexData.rename(columns={'Timestamp': 'Date (GMT)'} , inplace=True)
        indexData['Date (GMT)'] = pd.to_datetime(indexData['Date (GMT)'], format="%Y/%m/%d")
        CompositionData = tc.dataProcessing ('Trading Flow.csv', startDate,endDate)
        CompositionData = pd.merge(indexData, CompositionData, left_on = 'Date (GMT)' ,right_on = 'Date')
        CompositionData = PK.rolMean(CompositionData,20)
        tc.draw(CompositionData)
        #writing to wxcel file 
        writer = pd.ExcelWriter('output.xlsx')
        CompositionData.to_excel(writer,'DataComposition')
        writer.save()
        return render_template("DataComposition.html")
        '''
        return render_template("GenerateIndices.html",done=1)






if __name__ == '__main__':
    sectors = readStocks('sectorStocks.xlsx',0)
    larger=0
    for name in sectors:
        if(larger<sectors[name].count().max()):
            larger=sectors[name].count().max()
    nColumns=len(sectors.keys())
    sectorstemp=pd.DataFrame(pd.np.empty((larger,nColumns))* 0,columns=sectors.keys()) 
    
    for name in sectors:
        sectorstemp[name]=sectors[name]['stocks']
        
    
    #indexFile = PK.readData('indexLiveUpdate.xlsx',2)
    #indexData=indexFile['.EGX30']
    app.run()