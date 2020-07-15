
# Retrade: Monitors the stock market and places trades automatically.
# Copyright: Jules Carboni, 2020.


VERSION = "0.2.0"
print("Retrade v" + VERSION + ", (C) Jules Carboni 2020.") # Print copyright and version information at start


# Import dependencies
from datetime import datetime
from datetime import timedelta
from pytz import timezone # For converting times to/from EST
from time import sleep # To sleep the program
from colorama import Fore, Back, Style # For coloured text in the terminal
from yahoo_fin import stock_info # Import stock_info module from yahoo_fin, this is what gets the latest price




# Built in variables

TIMEZONE = timezone('US/Eastern')
DATE_TIME_FORMAT = "%Y-%m-%d %H:%M:%S %Z%z"

MARKET_OPEN_TIME = 00000 # TEMP
MARKET_CLOSE_TIME = 00000 # TEMP

STOP_WARNING_PROP = 5.0 / 100 # Percentage. If the SS is not within this range of the CS, it will be highlighted as a warning





def print_info(ticker, live_price, live_time, iteration, current_stop, submitted_stop, last_price):
    
    # Format and print live price and other information to console. E.g. TSLA: $1750.3487905234


    # Determine colours to use when printing info

    if live_price > last_price: # If the price went up make it green
        price_color = Back.GREEN #Fore.BLACK + Back.LIGHTGREEN_EX
    elif live_price < last_price: # If the price went down make it red
        price_color = Back.RED #Fore.BLACK + Back.LIGHTRED_EX
    else:
        price_color = Back.BLACK #Fore.BLACK + Back.LIGHTBLACK_EX

    if current_stop != submitted_stop: # If the current stop has changed and the submitted stop hasn't been updated, make it display orange/yellow
        current_stop_color = Fore.YELLOW
    else:
        current_stop_color = "" # Don't change the colour
    
    if abs((submitted_stop - current_stop) / float(submitted_stop)) >= STOP_WARNING_PROP: # If the submitted stop is not within 10% of the current stop, make it display red (could also go red if greater than the current stop (sell trades only))
        submitted_stop_color = Fore.RED
    else:
        submitted_stop_color = "" # Don't change the colour


    time_stamp = "[" + live_time.strftime(DATE_TIME_FORMAT) + "]" # Time stamp displaying date and time of price retrieval
    
    stop_prices = "(" + current_stop_color + "CS: " + format(current_stop, '.2f') + Fore.RESET + ", " + submitted_stop_color + "SS: " + format(submitted_stop, '.2f') + Fore.RESET + ")" # The prices of the stops, rounded to the nearest cent
    #iteration_number = "[" str(iteration) "]" # TEMP
    
    

    print(Style.DIM + time_stamp + Style.RESET_ALL + " " + ticker.upper() + ": " + price_color + "$" + format(live_price, '.4f') + Back.RESET + " " + stop_prices) # Display live price




# Get data from user
ticker = input("Ticker to monitor: ").lower() # The stock to monitor
interval = float(input("Time between price checks (seconds): ")) # Number of seconds between each request
duration = int(60 * float(input("Time until the computer stops monitoring (minutes): "))) # Duration of computer service (multiplied to convert to seconds)
trade_type = input("Trade type (leave blank for 'trailing sell'): ") # Type of trade to execute
volume = int(input("Stocks to trade (INTEGERS ONLY): ")) # Number of stocks to buy/sell

# Calculate the finishing time for the service
finish_time = datetime.now(TIMEZONE) + timedelta(seconds=duration)


# Branch out into different trade methods

if trade_type == "trailing sell" or trade_type == "": # If trade type not specified, assume trailing sell

    # Get trade type specific information
    trail_size = float(input("Trail value (dollars below highest market value to sell at): ")) # Get the size/value of the trail
    update_zone_prop = float(input("Update zone size (percentage) (lower percentage, higher risk): ")) / 100 # Area between the max price and stop price. If live price falls within this lower region, the remote stop price is updated
    #current_stop = float(input("Current stop price: "))
    trade_url = input("URL of trade page (MUST ALREADY HAVE STOP LOSS SET UP): ") # The URL to the stop-loss that has already been set up.


    # Get current/submitted stop price
    submitted_stop = 000000 # TEMP
    current_stop = submitted_stop

    # Calculate price at which to update the stop
    update_zone = update_zone_prop * trail_size
    update_stop = current_stop + update_zone

    last_price = 0.00 # The price of the last retrieval. Starts as an empty value

    iteration = 0 # Counter for number of passes

    # Loop until duration reached (or forever if no duration specified)
    while datetime.now(TIMEZONE) < finish_time or duration == 0:


        iteration += 1
        
        # Get live price of stock
        live_price = stock_info.get_live_price(ticker)
        live_time = datetime.now(TIMEZONE) # The time at which the price was retrieved (or close enough to) # TEMP (use proper datatable function that contains real time)


        calculated_stop = live_price - trail_size # The stop price assuming current price is highest price

        # Check if the new stop price is higher than the old stop price
        if calculated_stop > current_stop:

            # If so, update the current stop price and the stop price at which to update the submitted stop
            current_stop = calculated_stop
            update_stop = current_stop + update_zone

        # If the current stop is higher than the submitted stop, and the live price has fallen into the update zone, update the submitted stop
        if current_stop > submitted_stop and live_price <= update_stop:

            # TEMP Update the trade!

            submitted_stop = current_stop

        
        print_info(ticker, live_price, live_time, iteration, current_stop, submitted_stop, last_price) # Display live price and information TEMP

        last_price = live_price # Make the current price the new last price

        sleep(interval) # Wait the specififed time before getting the price again


else:

    print(Fore.RED + "Trade type does not exist. Program quit itself." + Fore.RESET)


print(Fore.GREEN + "Specified duration ended. You can safely quit this program." + Fore.RESET) # Show that everything closed safely (and that you didn't just crash).