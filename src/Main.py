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
    url_template = "https://www.immotop.lu/search-list/?{statut}{type}{subtype}&criterio=rilevanza&__lang=fr{location}"

    # Manage folders
    Check_create_folder("LOG")
    Check_create_folder("Outputs")

    # Create an object FileHandler to manage the writing of the logs in a file
    logging.basicConfig(filename='LOG/{}.log'.format(start_time_format), 
                        level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        force=True)
    
    # Get user parameters #
    json_path = input("Enter the path of the json file : ")
    data_json = Read_json(json_path)

    # dictionnary used to translate the filters into url to be scraped
    translate_to_url = Read_json("Inputs/translate_to_url.json")

    # Initialize an instance of immotop
    immotop = Immotop("Outputs/Immotop_{}.xlsx".format(start_time_format), data_json, url_template, translate_to_url)

    # Scrape overview pages to find the url of each property #
    for scraped_url in immotop.urls_to_scrap:

        print("Scrape {}".format(scraped_url))
        logging.info("Scrape {}".format(scraped_url))

        immotop.Scrape_overview_pages(scraped_url)

    # Scrape property pages
    immotop.Scrape_property_pages()    
        
    # Save dataframe
    immotop.Save_df()

    # Manage time
    stop_time = time.time()
    logging.info("Duration : {}".format(str(timedelta(seconds = stop_time-start_time))))