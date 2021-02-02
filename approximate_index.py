# libraries
import csv
from collections import defaultdict
import pandas as pd 
import numpy as np  
import statsmodels.api as sm
import os
import sys
import matplotlib as mpl
if os.environ.get('DISPLAY','') == '':
    mpl.use('Agg')
import matplotlib.pyplot as plt
 
def approximateindex(File_name, Market_Index, n):
    
    ###-------------  Setting and cleaning Data ---------------------------------------
    intial_dataframe = pd.read_csv(File_name)
    # change the structure of dataFrame to make each stock as column, and 'Close' values are inserted based on the date.
    Stocks_Data_Table = intial_dataframe.pivot(index='Date', columns='Symbol', values= 'Close')
    # Create a Correlation_dict to store the correlation coefficient of each stock with the Maket_index
    Correlation_dict = pd.DataFrame(Stocks_Data_Table.corrwith(Stocks_Data_Table[Market_Index])).to_dict('index')
    for key in Correlation_dict.keys():
        Correlation_dict[key] = Correlation_dict[key][0]

    # Sort the Correlation_dict as per its values
    sorted_Correlation_dict = sorted(Correlation_dict.items(), key=lambda x: x[1], reverse=True)

    #stock_list will store all stock names in sorted order of correlation values
    stock_list = []
    for key,value in sorted_Correlation_dict:
        if key != Market_Index:
            stock_list.append(key)

    # num_of_stocks refers to the total number of stocks given in data file
    num_of_stocks = len(stock_list)

    if n > num_of_stocks:
        return (False,"Please insert a valid value for 'n'. Current value is bigger than total no. of stocks in Market_Index")


    ###----------------- Generating OLS Regression model --------------------------------
    '''
    -> The following loops will help in generating a Multiple-linear regression model whose all coefficients are positive.
    -> These loops will continuously keep producing regression models until it meets our conditions (i.e. all weights are neither negative nor zero) 
    -> While generating models, we will be picking n stocks based on the correlation coefficients calculated above.
    -> Thereby, stocks with a higher correlation with the Market_Index will have a more prominent chance of getting selected.
    '''
    for i_add in range(0, num_of_stocks - n + 1):

        position_list = list(range(0 + i_add ,n+i_add))
        index = n
        flag = False
        while index > 0:

            # n_Selected_stocks will store stocks picked to form regression model
            n_Selected_stocks = []
            for pos_index in range(len(position_list)):
                n_Selected_stocks.append(stock_list[position_list[pos_index]])

            #Build an accurate OLS multiple regression model
            X = Stocks_Data_Table[n_Selected_stocks]
            y = Stocks_Data_Table[Market_Index]
            model = sm.OLS(y, X).fit()
            
            # check if all model parameters(coef.) are positive
            neg_count = len(list(filter(lambda x: (x < 0), model.params)))
            if neg_count == 0:
                # set flag true if model found
                flag = True
                break

            # Enter here if previous model failed to fulfill our requirements and find the next stock with higher correlation 
            position_list[index-1] += 1

            #increase the position counter to change stock in n_selected_stocks and make sure it doesn't get out of bound
            if position_list[index-1] >= num_of_stocks -1:
                index -= 1
                position_list = list(range(0+ i_add ,n + i_add))
                position_list[index-1] += 1

            # make sure no stock within n_selected_stocks  is repeating. If so, change the repeating stock with the next one.
            if len(position_list) != len(set(position_list)):
                position_list[index-1] += 1
                if position_list[index-1] >= num_of_stocks -1:
                    index -= 1
                    position_list = list(range(0+ i_add ,n + i_add))
                    position_list[index-1] += 1

        #If flag is true that means we have found our model, so exit loop
        if flag == True:
            break

    # weights_dict stores the stock name and its respective weighted average to form Market Index
    weights_dict = pd.DataFrame(model.params).to_dict('index')
    for key in weights_dict.keys():
        weights_dict[key] = float('{:.2f}'.format(weights_dict[key][0]))

    ### --------------------- Printing Results -----------------------------------------------------

    print("Symbol, Weight")
    
    for key in weights_dict.keys():
        print(key + ", " +str(weights_dict[key]))

    #If you like to print model summary in detail, uncomment the line below
    #print(model.summary())

    ### --------------------- Generating a comparsion graph b/w market_index and our model----------
    #comment the code block untill "return" [line-131], if you don't want graph 
    
    newcol = 0
    col_name = str(n) + "_Stocks_Portfolio"
    for i in weights_dict.keys():
        newcol += weights_dict[i]*Stocks_Data_Table[i]

    Stocks_Data_Table[col_name] = newcol
    Stocks_Data_Table.reset_index(inplace=True)

    # multiple line plot
    # plt.figure(figsize=(15, 8))    
    plt.plot( 'Date', Market_Index, data= Stocks_Data_Table, markerfacecolor='blue',  color='red', linewidth=2)
    plt.plot( 'Date', col_name, data= Stocks_Data_Table,  color='green', linewidth=2)
    plt.xticks(rotation=90)
    plt.xlabel('Time (Date ->)')
    plt.ylabel('Range $')
    plt.legend()
    plt.tick_params(axis='x', labelsize=0, length = 0)
    plt.title("Market_Index VS {} Stock Portfolio".format(n))
    plt.savefig('Comparison_chart.png')
    
    return (True,"")
    
    
if __name__ == "__main__":
    # File_name refers to the input data file
    File_name = str(sys.argv[3])  #"dow_jones_historical_prices.csv"
    # Market_Index refers to the index which we want to replicate like - S&P500, NASDAQ, DOW JONES, etc
    Market_Index = str(sys.argv[2]) #'.DJI'
    # n refers to the number of stock used to replicate Market_index
    n = int(sys.argv[1])  #3 
    bo , error = approximateindex(File_name,Market_Index, n)
    if bo == False:
        print(error)
