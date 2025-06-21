import logging
import time
from datetime import timedelta

from Immotop import *
from Config_data_json import ConfigModel
from Tools.Files_tools import *
from Tools.Dictionnary_tools import *

#### Main ####
if __name__ == "__main__":

    # Manage time
    start_time = time.time()
    start_time_format = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime(start_time))

    # URL
    url_template = "https://www.immotop.lu/search-list/?{statut}{type}{subtype}&criterio=rilevanza&__lang=fr{location}"

    # Manage folders
    Create_folder("LOG")
    Create_folder("Outputs")

    # Create an object FileHandler to manage the writing of the logs in a file
    logging.basicConfig(filename='LOG/{}.log'.format(start_time_format), 
                        level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        force=True)
    
    # Get user parameters
    json_path = input("Enter the path of the json file : ")

    # Read the json file if it exists
    if Check_file(json_path, ".json"):

        data_json = Read_json(json_path)

    else:

        logging.error("This path doesn't exist : '{path}'.".format(path = json_path))
        exit(0)

    # Check the content of the json file
    try:
    
        config = Check_dictionnary_structure(data_json, ConfigModel)

    except Exception as e:

        logging.error(e)
        exit(1)

    # Dictionnary used to create the url to scrape from the config file
    translate_to_url = Read_json(os.path.join(sys._MEIPASS, "translate_to_url.json")) if Exe_or_local() else Read_json("Inputs/translate_to_url.json")

    # Initialize an instance of immotop
    immotop = Immotop("Outputs/Immotop_{}.xlsx".format(start_time_format))

    # Dictionary of urls to scrape
    scraped_urls = immotop.Create_url(data_json, url_template, translate_to_url)

    # Open a navigator
    immotop.Open_webdriver()   

    # Scrape overview pages to find the url of each property
    for url_context, scraped_url in scraped_urls.items():

        print("\nScrape {} : {}".format(url_context, scraped_url))
        logging.info("Scrape {} : {}".format(url_context, scraped_url))

        immotop.Scrape_overview_pages(scraped_url)
    
    # Close navigator
    immotop.Close_webdriver()

    # Scrape property pages
    immotop.Scrape_property_pages()    
        
    # Save dataframe
    immotop.Save_df()

    # Manage time
    stop_time = time.time()
    logging.info("Duration : {}".format(str(timedelta(seconds = stop_time-start_time))))