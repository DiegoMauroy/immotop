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

    # Manage time
    stop_time = time.time()
    logging.info("Duration : {}".format(str(timedelta(seconds = stop_time-start_time))))