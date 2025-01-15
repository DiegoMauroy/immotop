import logging
import time
from datetime import timedelta

from Immotop import *
from Tools.Tool_functions import *

#### Main ####
if __name__ == "__main__":

    # Manage time
    start_time = time.time()
    start_time_format = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime(start_time))

    # URL
    url_base = "https://www.immotop.lu/"


    # Manage folders
    Check_create_folder("LOG")
    Check_create_folder("Outputs")

    # Create an object FileHandler to manage the writing of the logs in a file
    logging.basicConfig(filename='LOG/{}.log'.format(start_time_format), 
                        level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        force=True)

    # Initialize an instance of immotop
    immotop = Immotop("Outputs/Immotop_{}.xlsx".format(start_time_format))

    # Scrape overview pages to find the url of each property #
    immotop.Scrape_overview_pages("https://www.immotop.lu/vente-maisons-appartements/luxembourg-pays/?criterio=rilevanza")

    print(immotop.dict_href_properties)

    # Manage time
    stop_time = time.time()
    logging.info("Duration : {}".format(str(timedelta(seconds = stop_time-start_time))))