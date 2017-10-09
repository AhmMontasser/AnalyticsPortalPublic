from plotly.offline import  plot
import plotly.graph_objs as go
import pandas as pd
import datetime
datetime.datetime.strptime
from plotly import tools
import Package as PK


'''function reading data from excel sheet adding it to a dictionary each one of them is a separate file '''
def readData(path,skiprows,start_date,end_date):
   parse_date = lambda x: x.strftime('%Y/%m/%d')
   xls = pd.ExcelFile(path)
   stocks={}
   for sh in xls.sheet_names:
       if(sh!='Sheet'):
           stocks[sh]=pd.read_excel(xls,sh, index_col=None,skiprows=skiprows, converters={'Timestamp':parse_date})
           stocks[sh] = stocks[sh].reset_index(drop=True)
           stocks[sh]=stocks[sh].iloc[::-1]
           stocks[sh] = stocks[sh][(stocks[sh]['Timestamp'] > start_date) & (stocks[sh]['Timestamp'] <= end_date)]
           
           
   return stocks


''' Preprocessing on the data '''
def dataProcessing (path,start_date,end_date):
    
    ''' Data Reading '''
    CompositionData = pd.read_csv(path, dayfirst=True, parse_dates=True,delimiter=",",skiprows=1)
    #CompositionData=CompositionData.iloc[::-1]
    CompositionData['Date']=pd.to_datetime(CompositionData['Date'],errors='coerce')
    CompositionData.loc[:, ~CompositionData.columns.str.contains('^Unnamed')]
    
    
    
    ''' DataRange '''
    
    ''' To have a default displaying all dates first '''
    if(start_date != 0 and end_date != 0):
        CompositionData = CompositionData[(CompositionData['Date'] > start_date) & (CompositionData['Date'] <= end_date)]
    
    
    
    ''' Renaming Columns '''
    CompositionData = CompositionData.rename(columns=lambda x: x.strip())
    
    CompositionData = CompositionData.rename (columns = { 'Retail': 'TotalRetail', 'Institutional':'TotalInstitutional', 'Foreign': 'TotalForeigner', 'Regional': 'TotalRegional', 'Local': 'TotalLocal',
                                                          'Retail.1': 'BuyRetail', 'Institutional.1':'BuyInstitutional', 'Foreign.1': 'BuyForeigner', 'Regional.1': 'BuyRegional', 'Local.1': 'BuyLocal',
                                                          'Retail.2': 'SellRetail', 'Institutional.2':'SellInstitutional', 'Foreign.2': 'SellForeigner', 'Regional.2': 'SellRegional', 'Local.2': 'SellLocal',
                                                          'Retail.3': 'NetFlowRetail', 'Institutional.3':'NetFlowInstitutional', 'Foreign.3': 'NetFlowForeigner', 'Regional.3': 'NetFlowRegional', 'Local.3': 'NetFlowLocal',
                                                         })    


    date = pd.DataFrame(CompositionData['Date'])

    columns = ['TotalRetail','TotalInstitutional','TotalForeigner', 'TotalRegional', 'TotalLocal',
                                                           'BuyRetail', 'BuyInstitutional',  'BuyForeigner','BuyRegional', 'BuyLocal',
                                                          'SellRetail', 'SellInstitutional',  'SellForeigner', 'SellRegional','SellLocal',
                                                           'NetFlowRetail', 'NetFlowInstitutional','NetFlowForeigner', 'NetFlowRegional','NetFlowLocal','Total Turnover'
                                                         ]
    CompositionData=CompositionData[columns]
    
    
     
    '''for column in CompositionData:
        if (column != 'Total Turnover'):
            CompositionData[column]= CompositionData[column] / CompositionData['Total Turnover']
          '''       
    CompositionData['Date']=date   
    
    return CompositionData




'''Graph drawing'''
def draw(df):
    fig = tools.make_subplots(rows=4,cols=1,shared_xaxes=True)
    
    trace1 = go.Scatter(
            x = df['Date (GMT)'],
            y = df['Trade Close'],
            name = 'Index', 
            )
    
    fig.append_trace(trace1, 3, 1)
    
    for column in df.columns.values:
        
        if (column == 'TotalRetail'or column == 'TotalInstitutional' or column == 'TotalForeigner' or column == 'TotalRegional' or column == 'TotalLocal' or column == 'total Turnover'):
            trace3 = go.Bar(
                    x=df['Date (GMT)'],
                    y=df[column],
                    name = column,
                    visible = "legendonly",
                    opacity = 1)
            fig.append_trace(trace3, 1, 1)
        
        elif (column == 'BuyRetail'or column == 'BuyInstitutional' or column == 'BuyForeigner' or column == 'BuyRegional' or column == 'BuyLocal' or column == 'SellRetail'or column == 'SellInstitutional' or column == 'SellForeigner' or column == 'SellRegional' or column == 'SellLocal' ):
            trace4 =  go.Bar(
                        x=df['Date (GMT)'],
                        y=df[column],
                        name = column,
                        visible = "legendonly",
                        opacity = 1)
            fig.append_trace(trace4, 4, 1)
        
        
        elif(column == 'NetFlowRetail'or column == 'NetFlowInstitutional' or column == 'NetFlowForeigner' or column == 'NetFlowRegional' or column == 'NetFlowLocal'):
            trace2 = go.Bar(
                    x=df['Date (GMT)'],
                    y=df[column],
                    name = column,
                    visible = "legendonly",
                    opacity = 1)
            fig.append_trace(trace2, 2, 1)
           
    plot(fig, filename='stacked-subplots')





''' function calculating coorelation between flow and index '''
def flow(CompositionData,indexData):
    ''' 1 and -1 for closing '''
    indexData['indexPosition'] = indexData['Trade Close']
    indexData['indexPosition'] = indexData['indexPosition'].shift(-1)
    indexData['indexPosition'] = indexData['indexPosition'] - indexData['Trade Close']
    
    
    indexData['indexPosition'].loc[(indexData['indexPosition'] <= 0.0) ] = -1    
    indexData['indexPosition'].loc[(indexData['indexPosition'] > 0.0) ] = 1

    ''' 1 and -1 for flow '''
    flow = CompositionData.copy()
    columns = ['Date','NetFlowRetail', 'NetFlowInstitutional' ,'NetFlowForeigner', 'NetFlowRegional', 'NetFlowLocal']
    flow = flow[columns]    
    for column in CompositionData:
        if (column == 'NetFlowRetail' or column == 'NetFlowInstitutional' or column == 'NetFlowForeigner' or column == 'NetFlowRegional' or column == 'NetFlowLocal'):
             flow[column] = flow[column].astype(float)
             flow[column].loc[(flow[column] <= 0.0) ] = -1
             flow[column].loc[(flow[column] > 0.0) ] = 1
            
    flow = pd.merge(flow, indexData, left_on = 'Date' ,right_on = 'Date (GMT)')
    columns = [ 'indexPosition' ,'NetFlowRetail' , 'NetFlowInstitutional','NetFlowForeigner', 'NetFlowRegional','NetFlowLocal']
    flow = flow[columns]
    return flow






''' Function to write each composiyion data in a separate sheet in an excel file '''
def excelWriter(CompositionData, indexData):

    ''' Save Index in the Excel file '''
    writer = pd.ExcelWriter('output.xlsx')
    indexData.to_excel(writer,'EGX30')
    
    
    for column in CompositionData:
        if (column == 'NetFlowRetail' or column == 'NetFlowInstitutional' or column == 'NetFlowForeigner' or column == 'NetFlowRegional' or column == 'NetFlowLocal'):
             data = CompositionData.copy()
             col= ['Date',column]
             data = data[col]
             data.to_excel(writer,column)
             
    
    writer.save()  
