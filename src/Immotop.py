import json
import pandas as pd
import tqdm
import logging

from Tools.Scrape import *
from Tools.Dictionnary_tools import *

#### Class to scrape Propertyweb ####
class Immotop(Website_selenium):

    ## Initialization
    def __init__(self, filename_output : str):
        
        self.filename_output        = filename_output       # filename of the output
        self.dict_href_properties   = {}                    # dictionnary of property hrefs (use a dictionary to avoid duplicates and keep the order)
                                                            # the value will be set to True for the properties "parent"
        self.current_url            = None                  # current url (selenium)

        # columns of the dataframes
        columns =   [
                        "URL", "ID", "ID parent",
                        "Nom",
                        "Pays", "Province", "City", "Macrozone", "MacrozoneId", "Adresse", "Numéro",
                        "Latitude", "Longitude", 
                        "Statut", "Type", "Projet Neuf",
                        "Prix", "Prix min", "Prix max", "Prix/m2",
                        "Disponibilité",
                        "Année de construction",
                        "Surface",
                        "Nombre de chambres",
                        "Nombre total d'étages", "Etage",
                        "Elévateur",
                        "Consommation d'énergie", "Classe d'isolation thermique", "Chauffage"
                    ]
        
        self.df_property    = pd.DataFrame(columns = columns)                                           # Dataframe to store data of the property, except the property "parent"
        self.df_parents     = pd.DataFrame(columns = [col for col in columns if col != "ID parent"])    # Dataframe to store data of the property "parent"

        # headers used by "requests"
        self.headers = {
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                        }
        
    ## Create urls to be scraped
    ## Inputs :
    ##  - json_create_url  : json containing the filters used to create the url
    ##  - url_template     : template to create the url to be scraped
    ##  - translate_to_url  : dictionnary used to translate the filters into url to be scraped
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
    ## Outputs :
    ##  - Return the number of pages (0 if there are no properties, 1 if there is only one page)
    def __Get_page_count(self):

        page_count = 0

        # Get the source code
        source_code = BeautifulSoup(self.driver.page_source, features = "lxml")

        # Check if the overview page contains properties
        lis = source_code.find_all("li", {"class" : "nd-list__item styles_in-searchLayoutListItem__y8aER"})
        if lis:
        
            # Search the tag containing the pages
            div_pagination = source_code.find("div", {"class" : "styles_in-pagination__list__vZpLW"})
            if div_pagination:

                # When there are many pages, the last page is not a <a> but a <div>. 
                # That's why, the text of each <div> and <a> have to be recover to get the last page.
                div_a_pages = div_pagination.find_all(['div', 'a'])
                if div_a_pages:

                    pages = []  # list of page numbers
                    for div_a_page in div_a_pages:

                        page = div_a_page.get_text(strip=True)

                        # Store the page number if it is numeric
                        if page and page.isdigit():
                            
                            pages.append(int(page))

                    # Return number of pages if the list of page numbers is not empty
                    if pages:

                        page_count = max(pages)
                    
                    # The list is empty
                    else:
                        
                        logging.warning("The list of pages is empty : {}.".format(self.current_url))
                        page_count = 1

                else:

                    logging.warning("There are no <a> and <div> in the tag <div class='styles_in-pagination__list__vZpLW'> in {}.".format(self.current_url))
                    page_count = 1

            else:

                logging.warning("The tag <div class='styles_in-pagination__list__vZpLW'> doesn't exist in {}.".format(self.current_url))
                page_count = 1

        else:

            logging.warning("There are no properties in : {}.".format(self.current_url))
            page_count = 0

        logging.info("Number of page : {}.".format(page_count))
        return page_count
    
    ## Get the data contained in a tag 'script' with id='__NEXT_DATA__'
    ## Inputs :
    ##  - source_code : source code of the page
    ##  - url : url of the page
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
                
                logging.error("Error json.loads in {} : {}".format(url, e))

        else:
            
            logging.warning("The tag <script id='__NEXT_DATA__'> doesn't exist in : {}.".format(url))

        return None
    
    ## Get the url of "child" properties
    ## Inputs :
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

                    for property in properties_data:

                        id = property.get("id")

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
    ## Inputs :
    ##  - url : url of the overview page to scrape
    def __Scrape_overview_page(self, url : str):

        # Access to the website
        self.Access_website(url)

        # Update current url
        self.current_url = self.driver.current_url

        # Get the source code
        source_code = BeautifulSoup(self.driver.page_source, features = "lxml")

        # Search the url of each property contained in the overview page
        lis = source_code.find_all("li", {"class" : "nd-list__item styles_in-searchLayoutListItem__y8aER"})
        if lis:

            for index, li in enumerate(lis):

                title = li.find("a", {"class" : "styles_in-listingCardTitle__Wy437"})
                if title:

                    # Get url of the page
                    href = title.get("href")
                    if href:

                        # If the property has "child" properties, scrape its page to get the url of the children 
                        if li.find("div", {"class" : "nd-strip is-spaced styles_in-listingCardUnits___DZU3"}):

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

                        logging.warning("The attribute 'href' doesn't exist in the tag <a class='styles_in-listingCardTitle__Wy437'> : property {}/{} in {}.".format(index+1, len(lis), self.current_url))
                        
                else:

                    logging.warning("There is no tag <a class='styles_in-listingCardTitle__Wy437'> in the tag <li class='nd-list__item styles_in-searchLayoutListItem__y8aER'> : property {}/{} in {}.".format(index+1, len(lis), self.current_url))

        else:

            logging.warning("The tag <li class='nd-list__item styles_in-searchLayoutListItem__y8aER'> doesn't exist in {}.".format(self.current_url))
        
    ## Scrape the overview pages to get the url of each property
    ## Inputs : 
    ##  - url : url of the overview page to scrape
    ## REMARK : use selenium to scrape the overview pages because, for some categories, requests is not enough to get the full source code
    def Scrape_overview_pages(self, url : str):

        logging.info("Start to scrape overview pages.")
        print("Start to scrape overview pages.")

        # Access to the website
        self.Access_website(url)

        # Update current url
        self.current_url = self.driver.current_url

        # Get the number of pages
        page_count = self.__Get_page_count()

        # Scrape each overview page
        for page in tqdm.tqdm(range(1, page_count + 1), "Get the url of each property"):
            
            # Scrape urls
            self.__Scrape_overview_page("{}&pag={}".format(url, str(page)))

        # Update current url (stop to use selenium)
        self.current_url = None

        logging.info("End to scrape overview pages.\n")
        print("End to scrape overview pages.\n")

    
    ## Transfer data from dictionnary to dataframe
    ## Inputs :
    ##  - dict_data : dictionnary containing the data to transfer
    ##  - df        : dataframe to fill
    ##  - index     : index of the row to fill in the dataframe
    ##  - url       : url of the page to scrape
    def __Transfer_dictio_to_dataframe(self, dict_data : dict, df : pd.DataFrame, index : int, url : str):

        # Get parent ID
        if "ID parent" in df.columns:
        
            df.at[index, "ID parent"] = Get_value_dictionnary(dict_data, ["props", "pageProps", "parentId"])

        # Focus on a part of the dictionnary
        data = Get_value_dictionnary(dict_data, ["props", "pageProps", "detailData", "realEstate"])
        if data:

            # In props/pageProps/detailData/realEstate
            df.at[index, "Nom"]           = data.get("title")
            df.at[index, "Statut"]        = data.get("contractValue")
            df.at[index, "Projet Neuf"]   = data.get("isNew")

            # In props/pageProps/detailData/realEstate/properties[0]
            property_data = data.get("properties")
            if property_data:

                property_data = property_data[0]

                df.at[index, "ID"]                        = property_data.get("id")
                df.at[index, "Type"]                      = property_data.get("typologyValue")
                df.at[index, "Disponibilité"]             = property_data.get("availability")
                df.at[index, "Surface"]                   = property_data.get("surfaceValue").replace("m²", "") if property_data.get("surfaceValue") else None
                df.at[index, "Nombre de chambres"]        = property_data.get("bedRoomsNumber")
                df.at[index, "Salle de bain/douche"]      = property_data.get("bathrooms")
                df.at[index, "Année de construction"]     = property_data.get("buildingYear")
                df.at[index, "Elévateur"]                 = property_data.get("elevator")
                df.at[index, "garage"]                    = property_data.get("garage")
                df.at[index, "Nombre total d'étages"]     = property_data.get("floors")
                df.at[index, "Etage"]                     = Get_value_dictionnary(property_data, ["floor", "value"])

                # In props/pageProps/detailData/realEstate/properties[0]/energy
                energy_data = property_data.get("energy")
                if energy_data:

                    df.at[index, "Consommation d'énergie"]        = Get_value_dictionnary(energy_data, ["class", "name"])
                    df.at[index, "Classe d'isolation thermique"]  = Get_value_dictionnary(energy_data, ["thermalInsulation", "consumption", "name"])
                    df.at[index, "Chauffage"]                     = energy_data.get("heatingType")

                # In props/pageProps/detailData/realEstate/properties[0]/location
                location_data = property_data.get("location")
                if location_data:
                    
                    df.at[index, "Pays"]          = Get_value_dictionnary(location_data, ["nation", "name"])
                    df.at[index, "Province"]      = location_data.get("province")
                    df.at[index, "City"]          = location_data.get("city")
                    df.at[index, "Macrozone"]     = location_data.get("macrozone")
                    df.at[index, "MacrozoneId"]   = location_data.get("macrozoneId")
                    df.at[index, "Adresse"]       = location_data.get("address")
                    df.at[index, "Numéro"]        = location_data.get("streetNumber")
                    df.at[index, "Latitude"]      = location_data.get("latitude")
                    df.at[index, "Longitude"]     = location_data.get("longitude")

                # In props/pageProps/detailData/realEstate/properties[0]/price
                price_data = property_data.get("price")
                if price_data:
                    
                    df.at[index, "Prix"]      = price_data.get("value")
                    df.at[index, "Prix min"]  = "".join(price_data.get("minValue").replace("€", "").split(" ")) if price_data.get("minValue") else None
                    df.at[index, "Prix max"]  = "".join(price_data.get("maxValue").replace("€", "").split(" ")) if price_data.get("maxValue") else None
                    df.at[index, "Prix/m2"]   = "".join(price_data.get("pricePerSquareMeter").replace("€/m²", "").split(" ")) if price_data.get("pricePerSquareMeter") else None
                
            else:

                logging.warning("'properties' was not found in the json : {}.".format(url))

        else:

            logging.warning("The data of {} were not scrapped.".format(url))

    ## Scrape property page
    ## Inputs :
    ##  - url : url of the property page to scrape
    ##  - df  : dataframe to fill with the data of the property
    def __Scrape_property_data(self, url : str, df : pd.DataFrame):

        # Get the source code
        source_code, _ = Web_page_source_code_robustification(url, 2, self.headers)

        # Check if the source code was scraped
        if source_code:

            # First free index in the dataframe
            index = len(df)

            # Add the URL to the dataframe. If the source code was not scraped, that means that the url won't be added in the dataframe.
            df.at[index, "URL"] = url

            # Search the tag 'script' containing the data
            data_json = self.__Get_json_data(source_code, url)
            if data_json:

                self.__Transfer_dictio_to_dataframe(data_json, df, index, url)

            else:

                logging.warning("The script id='__NEXT_DATA__' was not found in {}.".format(url))

    ## Scrape the property pages
    def Scrape_property_pages(self):

        logging.info("Start to scrape property pages.")
        print("Start to scrape property pages.")

        logging.info("Number of properties : {}.".format(len(self.dict_href_properties)))

        for href_property, is_parent in tqdm.tqdm(self.dict_href_properties.items(), desc = "Scrape the data of each property"):

            # The data of the properties "parent" are stored in a separated dataframe
            if is_parent:

                self.__Scrape_property_data(href_property, self.df_parents)

            else:

                self.__Scrape_property_data(href_property, self.df_property)

            time.sleep(1)

        logging.info("End to scrape property pages.\n")
        print("End to scrape property pages.\n")

    ## Save data in Excel file
    def Save_df(self):

        # Write the xlsx
        with pd.ExcelWriter(self.filename_output, engine = "xlsxwriter") as writer:
        
            self.df_property.to_excel(writer, sheet_name = "Propriétés", index = False)
            self.df_parents.to_excel(writer, sheet_name = "Parents", index = False)
        
        logging.info("The dataframes were saved at '{}'.\n".format(self.filename_output))