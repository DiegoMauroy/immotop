import json
import pandas as pd
import tqdm
import logging
from pydantic import BaseModel

from Immotop_data_json import ParentDataJson, PropertyDataJson
from Tools.Scrape import *
from Tools.Dictionnary_tools import *
from Tools.Converts import *

#### Class to scrape Immotop ####
class Immotop(Website_selenium):

    ## Initialization
    def __init__(self, filename_output : str):
        
        self.filename_output        = filename_output       # filename of the output
        self.dict_href_properties   = {}                    # dictionnary of property hrefs (use a dictionary to avoid duplicates and keep the order). The value will be set to True for the properties "parent"
        
        self.df_properties = pd.DataFrame(columns = PropertyDataJson.model_fields.keys()).astype(Convert_types_to_pandas_types(PropertyDataJson, "Europe/Brussels")) # Dataframe to store data of the property, except the property "parent"
        self.df_parents    = pd.DataFrame(columns = ParentDataJson.model_fields.keys()).astype(Convert_types_to_pandas_types(ParentDataJson, "Europe/Brussels"))     # Dataframe to store data of the property "parent"

        # headers used by "requests"
        self.headers = {
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                        }
        
    ## Create urls to be scraped
    ## Inputs :
    ##  - json_create_url  : json containing the filters used to create the url
    ##  - url_template     : template to create the url to be scraped
    ##  - translate_to_url : dictionnary used to translate the filters into url to be scraped
    ## Outputs :
    ##  - Return a dictionnary where the key is the context of the url and the value is the url
    def Create_url(self, json_create_url : dict, url_template : str, translate_to_url : dict):

        urls = {}

        # Get the location to be scraped
        locations       = [] 
        json_locations  = json_create_url.get("location")
        if json_locations:

            for json_location, to_scrap in json_locations.items():

                if to_scrap:

                    locations.append(json_location)

        # Sales/Rent ?
        status      = []
        json_status = json_create_url.get("statut")
        if json_status:

            for json_statu, to_scrap in json_status.items():

                if to_scrap:

                    status.append(json_statu)

        # Log an error if there aren't locations/status to be scraped
        if not locations or not status:

            logging.error("There is no location/statut to scrape. Check your 'config.json'.")
            exit(2)

        # Create the urls according to the type of property to be scraped
        for key1, value1 in json_create_url.items():

            if key1 != "location" and key1 != "statut":

                # value1 is a dictionnary if the type has subtypes
                if isinstance(value1, dict):

                    # Create the urls according to the subtype of property to be scraped
                    for key2, value2 in value1.items():

                        # if the subtype has to be scraped, add its url for each location and status to be scraped
                        if value2:
                            
                            for statu in status:
                            
                                for location in locations:

                                    # Check if there is an url for this statu, type (key1) and subtype (key2)
                                    if Get_value_dictionnary(translate_to_url, [statu, "types", key1, "subtypes", key2], False):
                                        
                                        urls["{}/{}/{}/{}".format(location, statu, key1, key2)] = url_template.format(statut     = "idContratto=" + Get_value_dictionnary(translate_to_url, [statu, "id"]),
                                                                                                                      type       = "&idCategoria=" + Get_value_dictionnary(translate_to_url, [statu, "types", key1, "id"]), 
                                                                                                                      subtype    = "&idTipologia[0]=" + Get_value_dictionnary(translate_to_url, [statu, "types", key1, "subtypes", key2]), 
                                                                                                                      location   = "&idNazione=" + translate_to_url[location])
                
                # There are no subtypes
                # if the type has to be scraped, add its url for each location and status to be scraped
                elif value1:
                                
                    for statu in status:

                        for location in locations:

                            # Check if there is an url for this statu and type (key1)
                            if Get_value_dictionnary(translate_to_url, [statu, "types", key1], False):

                                urls["{}/{}/{}".format(location, statu, key1)] = url_template.format(statut     = "idContratto=" + Get_value_dictionnary(translate_to_url, [statu, "id"]),
                                                                                                     type       = "&idCategoria=" + Get_value_dictionnary(translate_to_url, [statu, "types", key1, "id"]), 
                                                                                                     subtype    = "", 
                                                                                                     location   = "&idNazione=" + translate_to_url[location])
        
        return urls

    ## Get the number of pages in the URL
    ## Input : 
    ##  - url : url of the page in which we search the number of pages
    ## Output :
    ##  - Return the number of pages (0 if there are no properties, 1 if there is only one page)
    def __Get_page_count(self, url : str):

        page_count = 0

        # Get the source code
        source_code = BeautifulSoup(self.driver.page_source, features = "lxml")

        # Check if the overview page contains properties
        properties = source_code.find_all("li", {"class" : "nd-list__item styles_in-searchLayoutListItem__y8aER"})
        if properties:
        
            # Search the tag containing the pages
            div_pagination = source_code.find("div", {"data-cy" : "pagination-list"})
            if div_pagination:

                # When there are many pages, the last page is not a <a> but a <div>. 
                # That's why, the text of each <div> and <a> have to be scraped to get the last page.
                div_a_pages = div_pagination.find_all(['div', 'a'])
                if div_a_pages:

                    pages = []  # list of page numbers
                    for div_a_page in div_a_pages:

                        page = div_a_page.get_text(strip = True)

                        # Store the page number if it is numeric
                        if page and page.isdigit():
                            
                            pages.append(int(page))

                    # Return number of pages if the list of page numbers is not empty
                    if len(pages) > 0:

                        page_count = max(pages)
                    
                    # The list is empty
                    else:
                        
                        logging.warning("The list of pages is empty : {}.".format(url))
                        page_count = 1

                else:

                    logging.warning("There are no <a> and <div> in the tag <div data-cy='pagination-list'> in {}.".format(url))
                    page_count = 1

            else:

                logging.warning("The tag <div data-cy='pagination-list'> doesn't exist in {}.".format(url))
                page_count = 1

        else:

            logging.warning("There are no properties in : {}.".format(url))
            page_count = 0

        logging.info("Number of page : {}.".format(page_count))
        return page_count
    
    ## Get the data contained in a tag 'script' with id='__NEXT_DATA__'
    ## Inputs :
    ##  - source_code : source code of the page
    ##  - url         : url of the page
    ## Outputs :
    ##  - Return the data in a dictionnary (None if data have not been found)
    def __Get_json_data(self, source_code : BeautifulSoup, url : str):

        # Search the tag <script id='__NEXT_DATA__'> containing the data
        script_data = source_code.find("script", {"id" : "__NEXT_DATA__"})
        if script_data:

            # Try to store data in a dictionnary
            try:

                data = json.loads(script_data.get_text(strip=True))
                return data
                
            except json.JSONDecodeError as e:
                
                logging.warning("Error json.loads in {} : {}".format(url, e))

        else:
            
            logging.warning("The tag <script id='__NEXT_DATA__'> doesn't exist in : {}.".format(url))

        return None
    
    ## Get the url of "child" properties
    ## Input :
    ##  - url : url of the property page to scrape
    def __Get_children_url(self, url : str):

        # Get the source code
        source_code, _ = Web_page_source_code_robustification(url, 2, self.headers)
        
        # Check if the source code was scraped
        if source_code:

            # Search the tag 'script' containing the data
            data_json = self.__Get_json_data(source_code, url)
            if data_json:

                properties_data = Get_value_dictionnary(data_json, ["props", "pageProps", "detailData", "realEstate", "properties"])
                if properties_data:

                    for properti in properties_data:

                        id = properti.get("id")

                        # Check that it is not the id of the "Parent" property
                        if id not in url:

                            child_url = url + id
                            if child_url not in self.dict_href_properties:

                                self.dict_href_properties[child_url] = False

                else:

                    logging.warning("The url of the children were not scraped in : {}".format(url))

            else:

                logging.warning("The script id='__NEXT_DATA__' was not found in {}.".format(url))

    
    ## Scrape the overview page
    ## The goal is to get the url of each property contained in the overview page
    ## Input :
    ##  - url : url of the overview page to scrape
    def __Scrape_overview_page(self, url : str):

        # Access to the website
        self.Access_website(url)

        # Get the source code
        source_code = BeautifulSoup(self.driver.page_source, features = "lxml")

        # Search the url of each property contained in the overview page
        properties = source_code.find_all("li", {"class" : "nd-list__item styles_in-searchLayoutListItem__y8aER"})
        if properties:

            for index, prop in enumerate(properties):

                title = prop.find("a", {"class" : "styles_in-listingCardTitle__Wy437"})
                if title:

                    # Get url of the page
                    href = title.get("href")
                    if href:

                        # If the property has "child" properties, scrape its page to get the url of the children 
                        if prop.find("div", {"class" : "nd-strip is-spaced styles_in-listingCardUnits___DZU3"}):

                            # Add the property "parent"
                            if href not in self.dict_href_properties:

                                self.dict_href_properties[href] = True

                            #  Add the properties "child"
                            self.__Get_children_url(href)

                        else:

                            # Add the property
                            if href not in self.dict_href_properties:

                                self.dict_href_properties[href] = False

                    else:

                        logging.warning("The attribute 'href' doesn't exist in the tag <a class='styles_in-listingCardTitle__Wy437'> : property {}/{} in {}.".format(index+1, len(properties), url))
                        
                else:

                    logging.warning("There is no tag <a class='styles_in-listingCardTitle__Wy437'> in the tag <li class='nd-list__item styles_in-searchLayoutListItem__y8aER'> : property {}/{} in {}.".format(index+1, len(properties), url))

        else:

            logging.warning("The tag <li class='nd-list__item styles_in-searchLayoutListItem__y8aER'> doesn't exist in {}.".format(url))
        
    ## Scrape the overview pages to get the url of each property
    ## Inputs : 
    ##  - url : url of the overview pages to scrape
    ## REMARK : use selenium to scrape the overview pages because, for some categories, requests is not enough to get the full source code
    def Scrape_overview_pages(self, url : str):

        logging.info("Start to scrape overview pages.")
        print("Start to scrape overview pages.")

        # Access to the website
        self.Access_website(url)

        # Get the number of pages
        page_count = self.__Get_page_count(url)

        # Scrape each overview page
        for page in tqdm.tqdm(range(1, page_count + 1), "Get the url of each property"):
            
            # Scrape urls
            self.__Scrape_overview_page("{}&pag={}".format(url, str(page)))

        logging.info("End to scrape overview pages.\n")
        print("End to scrape overview pages.\n")


    ## Scrape property page
    ## Inputs :
    ##  - url   : url of the property page to scrape
    ##  - df    : dataframe to fill with the data of the property
    ##  - model : pydantic model used to prepare the data for the dataframe
    ## Output : 
    ##  - df : dataframe filled with data (or not filled, if the scrap has failed)
    def __Scrape_property_data(self, url : str, df : pd.DataFrame, model : type[BaseModel]):

        # Get the source code
        source_code, _ = Web_page_source_code_robustification(url, 2, self.headers)

        # Check if the source code was scraped
        if source_code:

            # Search the tag 'script' containing the data
            data_json = self.__Get_json_data(source_code, url)
            if data_json:

                try: 
                    
                    # Add the url in the dictionnary
                    data_json["url"] = url

                    # Check the structure of the property data and prepare the data for the DataFrame
                    prepared_data = Check_dictionnary_structure(data_json, model)

                    # Add the data to the DataFrame
                    tmp_df = pd.DataFrame([prepared_data.model_dump()]).astype(Convert_types_to_pandas_types(model, "Europe/Brussels"))
                    df = pd.concat([df, tmp_df], ignore_index = True)

                except Exception as e:

                    logging.warning("Error during the scraping of '{url}' : {e}".format(url = url, e = e))

            else:

                logging.warning("The script id='__NEXT_DATA__' was not found in {}.".format(url))

        return df

    ## Scrape the property pages
    def Scrape_property_pages(self):

        logging.info("Start to scrape property pages.")
        print("Start to scrape property pages.")

        logging.info("Number of properties : {}.".format(len(self.dict_href_properties)))

        for href_property, is_parent in tqdm.tqdm(self.dict_href_properties.items(), desc = "Scrape the data of each property"):

            # The data of the properties "parent" are stored in a separated dataframe
            if is_parent:

                self.df_parents = self.__Scrape_property_data(href_property, self.df_parents, ParentDataJson)

            else:

                self.df_properties = self.__Scrape_property_data(href_property, self.df_properties, PropertyDataJson)

            time.sleep(1)

        logging.info("End to scrape property pages.\n")
        print("End to scrape property pages.\n")

    ## Save data in Excel file
    def Save_df(self):

        # Write the xlsx
        with pd.ExcelWriter(self.filename_output, engine = "xlsxwriter") as writer:
        
            Remove_timezone_from_dataframe(self.df_properties).to_excel(writer, sheet_name = "Propriétés", index = False)
            Remove_timezone_from_dataframe(self.df_parents).to_excel(writer, sheet_name = "Parents", index = False)
        
        logging.info("The dataframes were saved at '{}'.\n".format(self.filename_output))