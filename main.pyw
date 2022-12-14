# Created by Janak S (https://github.com/codegallivant) on 4th June 2022.



import os
from datetime import timedelta, datetime
import pandas 
# import matplotlib.pylab as mplpyl
# import matplotlib.pyplot as mplp
# import matplotlib.dates as mpld
import mplfinance as mplf
# import mplcursors
import time
import tkinter as tk
import tkcalendar as tkc
import pyautogui as pag
import socket
    

#Note: Requires internet connection 



REMOTE_SERVER = "one.one.one.one"
def is_connected(hostname):
    try:
        # see if we can resolve the host name -- tells us if there is
        # a DNS listening
        host = socket.gethostbyname(hostname)
        # connect to the host -- tells us if the host is actually reachable
        s = socket.create_connection((host, 80), 2)
        s.close()
        return True
    except Exception:
        pass # we ignore any errors, returning False
    return False



def plot_button_command():

    global cancel_boolvar
    global internet_disconnected
    global code_exists

    cancel_boolvar.set(False)
    code_exists = None
    internet_disconnected = None

    plot_button.grid()
    plot_button.grid_remove()
    cancel_button.grid()

    if not is_connected(REMOTE_SERVER):
        pag.alert("Please check your internet connection.")
        cancel_button.grid_remove()
        plot_button.grid()
        return

    code = scriptcode_strvar.get().strip()

    if codetype_intvar.get() == 1:
        codetype = "equity"

        # Names of required columns in the equity csv (check csv link)
        name_col = "SYMBOL"
        open_col = "OPEN"
        high_col = "HIGH"
        low_col = "LOW"
        close_col = "CLOSE"

    elif codetype_intvar.get() == 2:

        codetype = "indice"

        # Names of required columns in the indice csv
        name_col = "Index Name"
        open_col = "Open Index Value"
        high_col = "High Index Value"
        low_col = "Low Index Value"
        close_col = "Closing Index Value"

    else:
        if code == "":
            pag.alert(f"Please enter an equity/index.")
        else:
            pag.alert("Please specify whether the code is an equity or an index.")
        cancel_button.grid_remove()
        plot_button.grid()
        return 

    if code == "":
        pag.alert(f"Please specify the {codetype}'s' code.")
        cancel_button.grid_remove()
        plot_button.grid()
        return

    if codetype == "equity":
        code = code.upper()
    elif codetype == "indice":
        code = code.title()


    start_date = datetime.combine(startdate_input.get_date(), datetime.min.time())
    end_date = datetime.combine(enddate_input.get_date(), datetime.min.time())
    

    algorithm_start= time.time()
    #Function to measure time taken by algorithm
    def measure_time(start_time):
        algorithm_end = time.time()
        seconds_taken = algorithm_end-start_time
        return time.strftime('%H:%M:%S', time.gmtime(seconds_taken))

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
        Equity file_url example = https://www1.nseindia.com/content/historical/EQUITIES/2022/MAY/cm04MAY2022bhav.csv.zip
        Indice file_url example = https://www1.nseindia.com/content/indices/ind_close_all_03062022.csv

        Equity file_url template = https://www1.nseindia.com/content/historical/EQUITIES/{year}/{monthshortformincaps}/cm{Dayofmonth}{monthshortformincaps}{year}bhav.csv.zip
        Indice file_url template = https://www1.nseindia.com/content/indices/ind_close_all_{dayofmonth}{monthofyear}{year}.csv
        '''
        
        print(f"TRADING DAY #{dates_copy.index(date)+1}\nReading CSV file of trades on {get_ambient_date(date)}...") 

        try:
            df = pandas.read_csv(file_url, sep=",")  #Error is thrown here if the url does not direct to a csv i.e. no trades occurred because it was a holiday for the stock exchange
        except Exception as e:
            print(type(e).__name__)
            print(repr(e))
            print("CSV file could not be read.")
            return type(e).__name__

        print("Reading complete. Processing...")

        data = df[df[name_col] == code]

        if data.empty:
            #If the dataframe is empty it means that the equity/indice was not in the CSV inspite of it being a trade day. Therefore, the equity/indice didn't exist on that date.
            return False
        else:
            print(f"Data of trades for {code} on {get_ambient_date(date)}:\n{data}")
           
        return {"open":float(data.iloc[0][open_col]), "high": float(data.iloc[0][high_col]), "low": float(data.iloc[0][low_col]), "close": float(data.iloc[0][close_col])}
        

    dates_copy = list(dates)

    progress_label.pack(side="left", anchor="w")
    progress_bar.pack(side="left", anchor="w")


    #Calling getOHLC() function for each date between start_date and end_date
    run_date_func_running = tk.BooleanVar()
    run_date_func_running.set(True)
    def run_date(ln):

        global internet_disconnected
        global code_exists

        if ln >= len(dates) or cancel_boolvar.get() == True:
            run_date_func_running.set(False)
            return

        date = dates[ln]

        ln += 1

        OHLC = getOHLC(date, code, codetype)

        print("\n")
    
        if OHLC == "HTTPError":
            #Error appears if link not found for that date i.e equity trading didn't happen on that date. Here we catch and combat this error.
            dates_copy.remove(date) # So that graphs can be plotted, elements of  dates & opening, high, low, closing lists must correspond to each other. Hence, we must remove the dates where equity trading didn't happen.
            #Will later equate dates to dates_copy.
        elif OHLC == "URLError" or OHLC == "RemoteDisconnected":
            internet_disconnected = True
            run_date_func_running.set(False)
            return
        elif OHLC is False:
            #If the dataframe is empty it means that the equity/indice was not in the CSV inspite of it being a trade day. Therefore, the equity/indice didn't exist on that date.
            dates_copy.remove(date)
            code_exists = False
        else:
            code_exists = True
            opening.append(OHLC["open"])
            high.append(OHLC["high"])
            low.append(OHLC["low"])
            closing.append(OHLC["close"])

        if dates_copy == []:
            progress_bar["value"] = progress_bar_maxvalue
            progress_label["text"] = "100%"
            root.update_idletasks()
        else:
            progress_bar['value'] = (ln/len(dates))*progress_bar_maxvalue
            progress_label["text"] = measure_time(run_date_start_time)+"   "+str(int((ln/len(dates))*100))+'%'
            root.update_idletasks()

        root.after(5, lambda:run_date(ln))        


    run_date_start_time = time.time()
    run_date(0)
    if run_date_func_running.get() is True:
        root.wait_variable(run_date_func_running)

    dates = list(dates_copy)

    #The graph plotter
    def plot():

        # fig = mplpyl.gcf()
        # fig.canvas.manager.set_window_title(f"{code} OHLC Chart")

        # x = [datetime.strptime(str(date.date()),'%Y-%m-%d').date() for date in dates]

        # mplp.plot(x,opening, label="Open")
        # mplp.plot(x,high, label="High")
        # mplp.plot(x,low, label="Low")
        # mplp.plot(x,closing, label="Close")

     
        # plotting the data
        data = pandas.DataFrame({"Open":opening,"High":high,"Low":low,"Close":closing}, index=dates)
        customstyle = mplf.make_mpf_style(base_mpf_style='yahoo', y_on_right=False, facecolor='w')
        mplf.plot(data, type="candle", xlabel="Date", ylabel="O/H/L/C Price (₹)", style=customstyle, title=f"[OHLC prices VS respective dates] for {codetype} {code} ({get_ambient_date(dates[0])}-{get_ambient_date(dates[-1])})")
         
    
        #To ensure no overlap between x ticks, we specify intervals between consecutive x ticks(dates) in daylocator(), depending on number of ticks
        # if len(x) <= 40:
        #     mplp.gca().xaxis.set_major_locator(mpld.DayLocator())
        #     mplp.gca().xaxis.set_major_formatter(mpld.DateFormatter('%d/%m/%Y'))
        #     mplp.xticks(rotation=30) #To reduce overlapping of x ticks 
        # elif len(x) <=80:
        #     mplp.gca().xaxis.set_major_locator(mpld.DayLocator(interval=15))
        #     mplp.gca().xaxis.set_major_formatter(mpld.DateFormatter('%d/%m/%Y'))
        #     mplp.xticks(rotation=15) #To reduce overlapping of x ticks 
        # elif len(x) <= 365:
        #     mplp.gca().xaxis.set_major_locator(mpld.DayLocator(interval=32))
        #     mplp.gca().xaxis.set_major_formatter(mpld.DateFormatter('%d %b %Y'))
        #     mplp.xticks(rotation=15) #To reduce overlapping of x ticks 
        # elif len(x) <= 2560:
        #     mplp.gca().xaxis.set_major_locator(mpld.DayLocator(interval=182))
        #     mplp.gca().xaxis.set_major_formatter(mpld.DateFormatter('%d %b %Y'))
        #     mplp.xticks(rotation=15) #To reduce overlapping of x ticks 
        # else:
        #     mplp.gca().xaxis.set_major_locator(mpld.DayLocator(interval=365))
        #     mplp.gca().xaxis.set_major_formatter(mpld.DateFormatter('%d %b %Y'))
        #     mplp.xticks(rotation=0) #To reduce overlapping of x ticks 
        
        # mplp.gcf().autofmt_xdate()
        
        # mplp.xlabel("Date")
        # mplp.ylabel("O/H/L/C Price (₹)")
        
        # mplp.title(f"[OHLC prices VS respective dates] for {codetype} {code} ({get_ambient_date(dates[0])}-{get_ambient_date(dates[-1])})")
        # mplp.legend()

        #Implementing hover functionality
        # crs = mplcursors.cursor(hover=True)

        #Ensuring that the graph window is maximized on startup
        # try:
        #     # Option 1
        #     # QT backend
        #     manager = mplp.get_current_fig_manager()
        #     manager.window.showMaximized()
        # except:
        #     try:
        #         # Option 2
        #         # TkAgg backend
        #         manager = mplp.get_current_fig_manager()
        #         manager.resize(*manager.window.maxsize())
        #     except: 
        #         try:   
        #             # Option 3
        #             # WX backend
        #             manager = mplp.get_current_fig_manager()
        #             manager.frame.Maximize(True)
        #         except:
        #             pass

        # mplp.show()


    message = ""


    if cancel_boolvar.get() == True:
        pass
    elif code_exists is False:

        message += f"The {codetype} '{code}' does/did not exist in the given time range i.e it is/was not registered in the NSE of India at the time."
        
        if int(start_date.strftime('%Y')) < 2017: 
            message += "\n* NOTE: Results from 2016 rearwards may be inaccurate due to lack of available data.\n"

        # message += f"\nTime taken: {measure_time(algorithm_start)}"

        pag.alert(message)
    elif internet_disconnected is True:

        pag.alert("Please check your internet connection")

    elif dates==[]:

        message += f"No trades took place in the duration specified.\nThis may be because the analysis date range specified completely consists of National Stock Exchange holidays, on which trading does not occur. Saturday, Sunday and national holidays are non-working days for the stock exchange.\nTo obtain proper results, please set a suitable date range after running the program again."
        
        if int(start_date.strftime('%Y')) < 2017: 
            message += "\n* NOTE: Results from 2016 rearwards may be inaccurate due to lack of available data."
        
        # message += f"\nTime taken: {measure_time(algorithm_start)}"

        pag.alert(message)        
    else:

        # message += f"Analysis complete.\nTime taken: {measure_time(algorithm_start)}"
        
        # message += "\nPress OK to view the graph."

        # pag.alert(message)
        cancel_button.grid_remove()
        plot_button.grid()
        plot_button["state"] = "disabled"

        plot()


    progress_label.pack_forget()
    progress_bar.pack_forget()
    cancel_button.grid_remove()
    plot_button.grid()
    plot_button["state"] = "normal"


root = tk.Tk()
root.resizable(0,0)
root.title("Stock Market OHLC Chart Plotter (NSE)")
root.iconbitmap('favicon.ico')
root.tk.call('source', 'tkthemes/azure-ttk-theme/azure.tcl')  # Put here the path of your theme file
root.tk.call("set_theme", "dark")

scriptcode_input_frame = tk.ttk.LabelFrame(root)
scriptcode_label1 = tk.ttk.Label(scriptcode_input_frame, text = "Enter the equity/index's code.")
scriptcode_label2 = tk.ttk.Label(scriptcode_input_frame, text = "The equity/index must be registered in the National Stock Exchange of India.") 
scriptcode_strvar = tk.StringVar()
scriptcode_entry = tk.ttk.Entry(scriptcode_input_frame, textvariable = scriptcode_strvar)
scriptcode_label1.pack(anchor = "w", padx=10, pady=2.5)
scriptcode_label2.pack(anchor = "w", padx=10, pady=2.5)
scriptcode_entry.pack(padx=10, pady=5, anchor = "w")
scriptcode_input_frame.grid(row=0, column=0, sticky = "ew", padx=10, pady=1.5, ipadx=10, ipady=5)

codetype_input_frame = tk.ttk.LabelFrame(root)
codetype_label = tk.ttk.Label(codetype_input_frame, text = "The above is an -")
codetype_intvar = tk.IntVar()
codetype_radio1 = tk.ttk.Radiobutton(codetype_input_frame, text="Equity (Examples: ZOMATO, IDEA, RELIANCE, INFY (Infosys), ASIANPAINT, BHARTIARTL (Airtel) etc)", variable=codetype_intvar, value=1)
codetype_radio2 = tk.ttk.Radiobutton(codetype_input_frame, text="Index (Examples: Nifty 50, Nifty Next 50, Nifty 100, Nifty 200 etc)", variable=codetype_intvar, value=2)
codetype_label.pack(anchor = "w", padx=10)
codetype_radio1.pack(anchor = "w", padx=10)
codetype_radio2.pack(anchor = "w", padx=10)
codetype_input_frame.grid(row=1, column=0, sticky = "ew", padx=10, pady=1.5, ipadx=10, ipady=10)

date_input_frame = tk.ttk.LabelFrame(root)
date_label1 = tk.Label(date_input_frame, text = "Plot OHLC values from")
max_datetime_obj = datetime.now()
startdate_input = tkc.DateEntry(date_input_frame, selectmode = 'day', maxdate = max_datetime_obj-timedelta(days=1), date_pattern="dd/mm/yyyy")
startdate_input.set_date(max_datetime_obj-timedelta(days=7))
date_label2 = tk.Label(date_input_frame, text = "to")
enddate_input = tkc.DateEntry(date_input_frame, selectmode = 'day', date = max_datetime_obj, maxdate = max_datetime_obj, date_pattern="dd/mm/yyyy")
enddate_input.set_date(max_datetime_obj)
date_label3 = tk.Label(date_input_frame, text = ".")
date_label1.grid(row=0, column=0, padx=(10,0))
startdate_input.grid(row=0, column=1)
date_label2.grid(row=0, column=2)
enddate_input.grid(row=0, column=3)
date_label3.grid(row=0, column=4)
date_input_frame.grid(row=2, column=0, sticky = "ew", padx=10, pady=1.5, ipadx=10, ipady=2.5)

footer_frame = tk.Frame(root)
progress_label = tk.ttk.Label(footer_frame)
progress_bar_maxvalue = 100
progress_bar = tk.ttk.Progressbar(footer_frame, orient = "horizontal", length = 300, maximum = progress_bar_maxvalue, mode = "determinate")
# progress_bar.pack(side="left", anchor = "w")
button_frame = tk.ttk.Frame(footer_frame)
button_frame.pack(side="right", anchor = "e")
plot_button  = tk.ttk.Button(button_frame, text = "Plot chart", command = plot_button_command, style="Accent.TButton")
plot_button.grid(row=0,column=0)
cancel_boolvar = tk.BooleanVar()
cancel_boolvar.set(False)
cancel_button = tk.ttk.Button(button_frame, text = "Cancel", command = lambda:cancel_boolvar.set(True), style="Toggle.TButton")
cancel_button.grid(row=0,column=0)
cancel_button.grid_remove()
footer_frame.grid(row=3, column=0, padx=20, pady=15, sticky = "ew")

root.mainloop()
