
# Retrade: Monitors the stock market and places trades automatically. Specifically US stocks through CommSec.
# Copyright: Jules Carboni, 2020.


VERSION = "0.9.0" # Program version, change this whenever you want



# Import dependencies

from datetime import datetime
from datetime import timedelta
import time # To compare times of day (open and close hours)
from pytz import timezone # For converting times to/from EST

from time import sleep # To sleep the program
from colorama import Fore, Back, Style # For coloured text in the terminal
from getpass import getpass # Hides the typed text when entering passwords

from yahoo_fin import stock_info # Import stock_info module from yahoo_fin, this is what gets the latest price
from selenium import webdriver
from selenium.webdriver.common.keys import Keys # Allows data entry into web elements
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import NoSuchElementException, InvalidArgumentException # For Selenium error handling
import requests.exceptions # For Requests error handling


# Print copyright and version information at start

LOGO_PRINT = Fore.LIGHTRED_EX + "R" + Fore.LIGHTYELLOW_EX + "e" + Fore.LIGHTGREEN_EX + "t" + Fore.LIGHTCYAN_EX + "r" + Fore.LIGHTBLUE_EX + "a" + Fore.LIGHTMAGENTA_EX + "d" + Fore.LIGHTRED_EX + "e" + Fore.RESET
VERSION_PRINT = Fore.LIGHTBLACK_EX + "v" + VERSION + Fore.RESET
print("\n" + Style.BRIGHT + LOGO_PRINT + " " + VERSION_PRINT+ "\n" + "(C) Jules Carboni 2020" + Style.RESET_ALL + "\n")



# Built in variables

TIMEZONE = timezone('US/Eastern')
DATE_TIME_FORMAT = "%Y-%m-%d %H:%M:%S %Z%z"

MARKET_OPEN_TIME = datetime(1, 1, 1, 9, 15, tzinfo=TIMEZONE).time()
MARKET_CLOSE_TIME = datetime(1, 1, 1, 16, 15, tzinfo=TIMEZONE).time()

STOP_WARNING_PROP = 5.0 / 100 # Percentage. If the SS is not within this range of the CS, it will be highlighted as a warning

# Web variables (for CommSec International)
MASTER_LOGIN_URL = "https://www2.commsec.com.au/Public/HomePage/Login.aspx"
INTERNATIONAL_LOGIN_URL = "https://www2.commsec.com.au/Private/SingleSignOn/Pershing.aspx?sso=true"

# Web driver variables
BROWSER_CAPABILITIES = DesiredCapabilities.FIREFOX.copy()
BROWSER_CAPABILITIES['accept_untrusted_certs'] = True


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
        submitted_stop_color = Fore.LIGHTRED_EX
    else:
        submitted_stop_color = "" # Don't change the colour


    time_stamp = "[" + live_time.strftime(DATE_TIME_FORMAT) + "]" # Time stamp displaying date and time of price retrieval
    
    stop_prices = "(" + current_stop_color + "CS: " + format(current_stop, '.2f') + Fore.RESET + ", " + submitted_stop_color + "SS: " + format(submitted_stop, '.2f') + Fore.RESET + ")" # The prices of the stops, rounded to the nearest cent
    #iteration_number = "[" str(iteration) "]" # TEMP
    
    

    print(Style.DIM + time_stamp + Style.RESET_ALL + " " + ticker.upper() + ": " + price_color + "$" + format(live_price, '.4f') + Back.RESET + " " + stop_prices) # Display live price




def log_in():

    # Access the broker's website and validate the session by logging in
    # Sources: https://stackoverflow.com/questions/21186327/fill-username-and-password-using-selenium-in-python, https://medium.com/edureka/selenium-using-python-edc22a44f819


    # Get the master login page and attempt to log in

    try:
    
        # Locate the elements
        username_element = web_driver.find_element_by_id("ctl00_cpContent_txtLogin")
        password_element = web_driver.find_element_by_id("ctl00_cpContent_txtPassword")

        # Populate the elements
        username_element.send_keys(account_username)
        password_element.send_keys(account_password)

        web_driver.find_element_by_name("ctl00_cpContent_btnLogin").click() # Click the login button

    except NoSuchElementException:

        print("GOTCHA")





# --- GET DATA ---


# Get data from user


ticker = input(Style.NORMAL + "Ticker to monitor: " + Style.BRIGHT).lower() # The stock to monitor

interval = float(input(Style.NORMAL + "Time between price checks " + Style.DIM + "(seconds)" + Style.NORMAL + ": " + Style.BRIGHT)) # Number of seconds between each request
duration = int(60 * float(input(Style.NORMAL + "Time until the computer stops monitoring " + Style.DIM + "(minutes)" + Style.NORMAL + ": " + Style.BRIGHT))) # Duration of computer service (multiplied to convert to seconds)

# TEMP: Here is where to ask for which broker! Use this given variable when making decisions about e.g. the log-in process
account_username = input(Style.NORMAL + "CommSec User ID: " + Style.BRIGHT).lower() # The user's CommSec account ID
account_password = getpass(Style.NORMAL + "CommSec User password: " + Style.BRIGHT).lower() # The user's password, required to place trades

trade_type = "trailing sell" #TEMP: input(Style.NORMAL + "Trade type " + Style.DIM + "(leave blank for 'trailing sell')" + Style.NORMAL + ": " + Style.BRIGHT) # Type of trade to execute
#volume = int(input(Style.NORMAL + "Stocks to trade " + Style.DIM + "(INTEGERS ONLY)" + Style.NORMAL + ": " + Style.BRIGHT)) # Number of stocks to buy/sell

Style.RESET_ALL # Reset style after round of inputs





# Calculate the finishing time for the service
finish_datetime = datetime.now(TIMEZONE) + timedelta(seconds=duration)



# Initialise the selenium webdriver
web_driver = webdriver.Firefox(capabilities=BROWSER_CAPABILITIES)




# --- BEGIN PROCESSING ---


# Branch out into different trade methods


if trade_type == "trailing sell" or trade_type == "": # If trade type not specified, assume trailing sell

    # Get trade type specific information
    trail_size = float(input(Style.NORMAL + "Trail value " + Style.DIM + "(dollars below highest market value to sell at)" + Style.NORMAL + ": " + Style.BRIGHT)) # Get the size/value of the trail
    update_zone_prop = float(input(Style.NORMAL + "Update zone size " + Style.DIM + "(lower percentage means higher risk) (recommended: 80)" + Style.NORMAL + ": " + Style.BRIGHT)) / 100 # Area between the max price and stop price. If live price falls within this lower region, the remote stop price is updated
    #current_stop = float(input("Current stop price: "))
    trade_url = input(Style.NORMAL + "URL of trade page " + Style.DIM + "(MUST ALREADY HAVE STOP LOSS SET UP)" + Style.NORMAL + ": " + Style.BRIGHT) # The URL to the stop-loss that has already been set up.

    Style.RESET_ALL # Reset style after round of inputs


    # Get current/submitted stop price from trade page

    try:
            
        web_driver.get(trade_url) # Load the page

        # Extract the stop price

    except InvalidArgumentException:

        print(Fore.LIGHTRED_EX + "Error: The given trade URL does not exist." + Fore.RESET) # Print the exception message to the console
        
    except ConnectionError:

        print(Fore.YELLOW + "Now logging into CommSec account." + Fore.RESET) # Print the exception message to the console
        
        #TEMP DO GETTING STUFF

    submitted_stop = 000000 # TEMP
    current_stop = submitted_stop


    # Calculate price at which to update the stop
    update_zone = update_zone_prop * trail_size
    update_stop = current_stop + update_zone

    last_price = 0.00 # The price of the last retrieval. Starts as an empty value

    iteration = 0 # Counter for number of passes


    # Loop until the duration is reached (or forever if no duration specified)
    while datetime.now(TIMEZONE) < finish_datetime or duration == 0:

        
        # Check if the markets are open at the current time, if not, sleep and try again later
        if not 0 <= datetime.now(TIMEZONE).weekday() <= 4: # If its the weekend

            # Sleep for an hour then try again
            sleep(3600)
            continue # Go back and check current time again

        else: # If its a weekday

            if not MARKET_OPEN_TIME <= datetime.now(TIMEZONE).time() <= MARKET_CLOSE_TIME: # If markets are currently closed

                # Sleep for 10 minutes then try again
                sleep(600)
                continue # Go back and check current time again

            # If the markets are open, proceed with execution


        iteration += 1
        
        try: # Attempt a web request

            # Get live price of stock
            live_price = stock_info.get_live_price(ticker)
            live_time = datetime.now(TIMEZONE) # The time at which the price was retrieved (or close enough to) # TEMP (use proper datatable function that contains real time)

        except ConnectionError:

            # If failed to get new live price, skip this iteration and go to the next iteration

            print(Fore.LIGHTRED_EX + "Error: Could not get live price. Connection error." + Fore.RESET) # Print the exception message to the console
            continue # Next iteration


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



# Safely quit the Selenium web driver
web_driver.quit

print(Fore.GREEN + "Specified duration ended. You can safely quit this program." + Fore.RESET) # Show that everything closed safely (and that you didn't just crash).