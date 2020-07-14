
# Retrade: Monitors the stock market and places trades automatically.
# Copyright: Jules Carboni, 2020.


VERSION = "0.1.0"
print("Retrade v" + VERSION + ", (C) Jules Carboni 2020.") # Print copyright and version information at start


# Import dependencies
from datetime import datetime
from datetime import timedelta
from time import sleep

from yahoo_fin import stock_info # Import stock_info module from yahoo_fin



# Get data from user
ticker = input("Ticker to monitor: ").lower() # The stock to monitor
interval = float(input("Time between price checks (seconds): ")) # Number of seconds between each request
duration = int(60 * float(input("Time until the computer stops monitoring (minutes): "))) # Duration of computer service (multiplied to convert to seconds)
trade_type = input("Trade type (leave blank for 'trailing sell'): ") # Type of trade to execute


# Calculate the finishing time for the service
finish_time = datetime.now() + timedelta(seconds=duration)


# Branch out into different trade methods

if trade_type == "trailing sell" or trade_type == "":

    iteration = 0 # Counter for number of passes

    # Loop until duration reached (or forever if no duration specified)
    while datetime.now() < finish_time or duration == 0:


        iteration += 1
        print("Pass: " + iteration) # Display the number of the current pass


        # Get live price of stock
        live_price = stock_info.get_live_price(ticker)

        print(live_price)


        sleep(interval) # Wait the specififed time before getting the price again