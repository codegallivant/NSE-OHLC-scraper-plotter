# Created by Janak S (https://github.com/codegallivant) on 4th June 2022.



import os
from datetime import timedelta, datetime
import pandas 
import matplotlib.pyplot as mplp
import matplotlib.dates as mpld
import mplcursors
import time
    
#Note: Requires internet connection 



print("\n")

#Inputting Equity / Indice choice
while True:
    codetype = input("Choose (Type 1 or 2):\n1: Equity    (Examples: ZOMATO, IDEA, RELIANCE, FLIPKART etc)\n2: Indice    (Examples: Nifty 50, Nifty 100, Nifty 200 etc)\n")
    print("\n")

    if codetype == '1':
    
        codetype = "equity"
    
        # Names of required columns in the equity csv (check csv link)
        name_col = "SYMBOL"
        open_col = "OPEN"
        high_col = "HIGH"
        low_col = "LOW"
        close_col = "CLOSE"
    
    elif codetype == '2':
    
        codetype = "indice"
        
        # Names of required columns in the indice csv
        name_col = "Index Name"
        open_col = "Open Index Value"
        high_col = "High Index Value"
        low_col = "Low Index Value"
        close_col = "Closing Index Value"
    
    else:
        continue
    
    break

#Inputting name of equity/indice
code = input(f"Which {codetype}'s details do you want to see?\n")

#Ensuring issues due to case sensitivity don't occur 
if codetype == "equity":
    code = code.upper()
elif codetype == "indice":
    code = code.capitalize()

print("\n")

#Inputting analysis date range
print("Enter analysis date range. (DD-MM-YYYY)")
while True:
    try: 
        start_date = datetime.strptime(input("From: "),"%d-%m-%Y")
        end_date = datetime.strptime(input("Till: "),"%d-%m-%Y")
        break
    except:
        print("\nPlease enter the date in the format DD-MM-YYYY only.")

print("\n")


#Function to measure time taken by algorithm
algorithm_start= time.time()
def measure_algorithm_time():
    algorithm_end = time.time()
    seconds_taken = algorithm_end-algorithm_start
    return time.strftime('%H hours, %M minutes and %S seconds', time.gmtime(seconds_taken))


# Return list of datetime.date objects between start_date and end_date (inclusive):
dates = []
curr_date = start_date
while curr_date <= end_date:
    if curr_date.weekday()!=5 and curr_date.weekday()!=6: #Excluding NSE holidays sat and sun from date list
        dates.append(curr_date)
    curr_date += timedelta(days=1)


def get_ambient_date(date):
    #Converting datetime.date of Y-m-d format to d/m/Y format 
    return datetime.strptime(str(date.date()), '%Y-%m-%d').strftime('%d/%m/%Y')



#OHLC lists    
opening = [] 
high = []
low = []
closing = []


#Fetch OHLC values given date and code of equity/indice
def getOHLC(date, code, codetype):

    if codetype == "equity":
        file_url = f"https://www1.nseindia.com/content/historical/EQUITIES/{date.strftime('%Y')}/{(date.strftime('%b')).upper()}/cm{date.strftime('%d')}{(date.strftime('%b')).upper()}{date.strftime('%Y')}bhav.csv.zip" 
    elif codetype == "indice":
        file_url = f"https://www1.nseindia.com/content/indices/ind_close_all_{date.strftime('%d')}{date.strftime('%m')}{date.strftime('%Y')}.csv"     
    # print(file_url)
    '''
    Equity file_url example = https://www1.nseindia.com/content/indices/ind_close_all_03062022.csv
    Indice file_url example = https://www1.nseindia.com/content/historical/EQUITIES/2022/MAY/cm04MAY2022bhav.csv.zip

    Equity file_url template = https://www1.nseindia.com/content/historical/EQUITIES/{year}/{monthshortformincaps}/cm{Dayofmonth}{monthshortformincaps}{year}bhav.csv.zip
    Indice file_url template = https://www1.nseindia.com/content/indices/ind_close_all_{dayofmonth}{monthofyear}{year}.csv
    '''
    
    print(f"TRADING DAY #{dates_copy.index(date)+1}\nReading CSV file of trades on {get_ambient_date(date)}...") 
    df = pandas.read_csv(file_url, sep=",")  #Error is thrown here if the url does not direct to a csv i.e. no trades occurred because it was a holiday for the stock exchange

    print("Reading complete. Processing...")

    data = df[df[name_col] == code]

    if data.empty:
        #If the dataframe is empty it means that the equity/indice was not in the CSV inspite of it being a trade day. Therefore, the equity/indice doesn't exist.
        return False
    else:
        print(f"Data of trades for {code} on {get_ambient_date(date)}:\n{data}")
       
    return {"open":float(data.iloc[0][open_col]), "high": float(data.iloc[0][high_col]), "low": float(data.iloc[0][low_col]), "close": float(data.iloc[0][close_col])}
    

dates_copy = list(dates)


for date in dates:
    
    try:
        OHLC = getOHLC(date, code, codetype)
        # print(OHLC)
        print("\n")
    except:
        #Error appears if link not found for that date i.e equity trading didn't happen on that date. Here we catch and combat this error.
        dates_copy.remove(date) # So that graphs can be plotted, elements of  dates & opening, high, low, closing lists must correspond to each other. Hence, we must remove the dates where equity trading didn't happen.
         #Will later equate dates to dates_copy.
        continue

    if OHLC is False:
        # The equity/indice does not exist.
        break

    opening.append(OHLC["open"])
    high.append(OHLC["high"])
    low.append(OHLC["low"])
    closing.append(OHLC["close"])


dates = list(dates_copy)

# print(dates)
# print(opening)
# print(high)
# print(low)
# print(closing)


#The graph plotter
def plot():

    x = [datetime.strptime(str(date.date()),'%Y-%m-%d').date() for date in dates]

    mplp.gca().xaxis.set_major_formatter(mpld.DateFormatter('%d/%m/%Y'))
    mplp.gca().xaxis.set_major_locator(mpld.DayLocator())

    mplp.plot(x,opening, label="Open")
    mplp.plot(x,high, label="High")
    mplp.plot(x,low, label="Low")
    mplp.plot(x,closing, label="Close")

    mplp.gcf().autofmt_xdate()
    mplp.xlabel("Date")
    mplp.ylabel("O/H/L/C (₹)")

    mplp.xticks(rotation=60) #To reduce overlapping of x ticks 

    
    mplp.title(f"[ O/H/L/C values V/S respective dates ] for {codetype} '{code}' (Analysis date range: {get_ambient_date(start_date)} to {get_ambient_date(end_date)})")
    mplp.legend()

    crs = mplcursors.cursor(hover=True)

    mplp.show()


print("\n")



if dates==[]:

    print(f"No trades took place in the duration specified.\nThis is because the analysis date range specified completely consists of National Stock Exchange holidays, on which trading does not occur. Saturday, Sunday and national holidays are non-working days for the stock exchange.\nTo obtain proper results, please set a suitable date range after running the program again.")
    
    print(f"Time taken: {measure_algorithm_time()}")

elif OHLC is False:

    print(f"The {codetype} '{code}' does not exist. Please enter a valid {codetype} to obtain proper results.")

    print(f"Time taken: {measure_algorithm_time()}")

else:

    print(f"Analysis complete. Time taken: {measure_algorithm_time()}")
    
    print("\nPlotting graph...")    
    plot()
    