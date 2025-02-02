import json
import pandas as pd
import tqdm
import logging

from Tools.Scrape import *
from Tools.Tool_functions import *

#### Class to scrape Propertyweb ####
class Immotop(Website_selenium):

    ## Initialization ##
    def __init__(self, filename_output):
        
        self.filename_output        = filename_output       # filename of the output
        self.dict_href_properties   = {}                    # dictionnary of property hrefs (use a dictionary to avoid duplicates and keep the order)
        self.scraper                = "bs4"                 # web scraper used to scrape overview page

        # Dataframe to store data
        self.df_property = pd.DataFrame(columns =   [
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
                                                    ])

        # headers used by "requests"
        self.headers = {
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                        }
        
    ## Create urls to be scraped ##
    ## json_create_url  => json containing the filters used to create the url ##
    ## url_template     => template to create the url to be scraped ##
    ## translate_to_url => dictionnary used to translate the filters into url to be scraped ##
    ## Return a dictionnary where the key is the context of the url and the value is the url ##
    def Create_url(self, json_create_url, url_template, translate_to_url):

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
    
    ## Get the number of pages in the URL ##
    ## Return the number of pages ##
    def __Get_page_count(self, source_code, url):

        # Check if the overview page contains properties
        lis = source_code.find_all("li", {"class" : "nd-list__item in-searchLayoutListItem"})
        if lis:
        
            # Search the tag containing the pages
            div_pagination = source_code.find("div", {"class" : "in-pagination__list"})
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

                        count = max(pages)
                        return count
                    
                    # The list is empty
                    else:
                        
                        logging.warning("{} : The list of pages is empty : {}.".format(self.scraper, url))
                        self.scraper = "selenium" if self.scraper == "bs4" else None    # Update scraper to use
                        logging.info("Scraper set to : {}.".format(self.scraper))
                        return 1

                else:

                    logging.warning("{} : There is no <a> and <div> in the tag <div class='in-pagination__list'> in {}.".format(self.scraper, url))
                    self.scraper = "selenium" if self.scraper == "bs4" else None    # Update scraper to use
                    logging.info("Scraper set to : {}.".format(self.scraper))
                    return 1

            else:

                logging.warning("{} : The tag <div class='in-pagination__list'> doesn't exist in {}.".format(self.scraper, url))
                self.scraper = "selenium" if self.scraper == "bs4" else None    # Update scraper to use
                logging.info("Scraper set to : {}.".format(self.scraper))
                return 1

        else:

            logging.warning("{} : There are no properties in : {}.".format(self.scraper, url))
            self.scraper = "selenium" if self.scraper == "bs4" else None    # Update scraper to use
            logging.info("Scraper set to : {}.".format(self.scraper))
            return 0

    ## Search the number of pages in the URL ##
    ## Return the number of pages ##
    ## REMARK : For some overview page, beautifulsoup is not enough to get page count (I don't know why). ##
    ##          That's why, this function starts by using beautifulsoup. If the page count is not found, it tries with selenium. ##
    def __Search_page_count(self, url):

        page_count = 0

        # Try to get page count with bs4
        if self.scraper == "bs4":

            # Get the source code
            source_code, _ = Web_page_source_code_robustification(url, 2, self.headers)

            # Check if the source code was scraped
            if source_code:

                # Get page count
                page_count = self.__Get_page_count(source_code, url)

        # Try to get page count with selenium
        if self.scraper == "selenium":
        
            # Open a navigator
            self.Open_webdriver()

            # Access to the website
            self.Access_website(url)

            # Get the source code
            source_code = BeautifulSoup(self.driver.page_source, features = "lxml")

            # Close navigator
            self.Close_webdriver()

            # Get page count
            page_count = self.__Get_page_count(source_code, url)

        # The page count has not been found
        if not self.scraper:

            logging.warning()
            page_count = 1

        logging.info("Number of page : {}.".format(page_count))
        return page_count
    
    ## Get the url of a specific page ##  
    ## Return the url of this specific page (None if not found) ##
    def __Get_url_specific_page(self, source_code, url, searched_page):

        searched_url = None

        # Search the tag containing the pages
        div_pagination = source_code.find("div", {"class" : "in-pagination__list"})
        if div_pagination:

            # Search the href of the searched_page
            a_pages = div_pagination.find_all('a')
            if a_pages:

                for a_page in a_pages:

                    page = a_page.get_text(strip=True)
                    if page and page.isdigit() and int(page) == searched_page:

                        href = a_page.get("href")
                        if href:
                            
                            searched_url = href 
                        
                        else:

                            logging.warning("There is no href in <a>{}</a> in {}.".format(str(page), url))
                
            else:

                logging.warning("There is no <a> and <div> in the tag <div class='in-pagination__list'> in {}.".format(url))

        else:

            logging.warning("The tag <div class='in-pagination__list'> doesn't exist in {}.".format(url))

        return searched_url

    ## Search the url of a specific page ##  
    ## Return the url of this specific page (None if not found) ##
    def __Search_url_specific_page(self, url, searched_page):

        searched_url = None

        # Try to the get the url with bs4
        if self.scraper == "bs4":

            # Get the source code
            source_code, _ = Web_page_source_code_robustification(url, 2, self.headers)

            # Check if the source code was scraped
            if source_code:

                searched_url = self.__Get_url_specific_page(source_code, url, searched_page)

        # Try to the get the url with selenium
        if self.scraper == "selenium":
                
            # Open a navigator
            self.Open_webdriver()

            # Access to the website
            self.Access_website(url)

            # Get the source code
            source_code = BeautifulSoup(self.driver.page_source, features = "lxml")

            # Close navigator
            self.Close_webdriver()

            # Get the url
            searched_url = self.__Get_url_specific_page(source_code, url, searched_page)

        # Impossible to get the url
        if not self.scraper:

            logging.error("Url of the page {} was not found : {}.".format(searched_page, url))
    
        return searched_url
    
    ## Get the data contained in a tag 'script' with id='__NEXT_DATA__' ##
    ## Return data in a dictionnary (None if data have not been found) ##
    def __Get_json_data(self, source_code, url):

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
    
    ## Get the url of "child" properties ##
    def __Get_children_url(self, url):

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

                                self.dict_href_properties[child_url] = None

                else:

                    logging.warning("The url of the children were not scraped in : {}".format(url))

            else:

                logging.warning("The script id='__NEXT_DATA__' was not found in {}.".format(url))


    ## Scrape the url of a property in the overview page ##
    ## Add the url in dict_href_properties ##
    def __Get_url_property(self, source_code, url):

        # Search the url of each property contained in the overview page
        lis = source_code.find_all("li", {"class" : "nd-list__item in-searchLayoutListItem"})
        if lis:

            for index, li in enumerate(lis):

                title = li.find("a", {"class" : "in-listingCardTitle"})
                if title:

                    # Get url of the page
                    href = title.get("href")
                    if href:

                        # Check that the url has not been already scraped
                        if href not in self.dict_href_properties:

                            self.dict_href_properties[href] = None

                        # If the property has "child" properties, scrape its page to get the url of the children 
                        if li.find("div", {"class" : "nd-strip is-spaced in-listingCardUnits"}):

                            self.__Get_children_url(href)

                    else:

                        logging.warning("{} : The attribute 'href' doesn't exist in the tag <a class='in-listingCardTitle'> : property {}/{} in {}.".format(self.scraper, index+1, len(lis), url))
                        self.scraper = "selenium" if self.scraper == "bs4" else None    # Update scraper to use
                        logging.info("Scraper set to : {}.".format(self.scraper))
                        return

                else:

                    logging.warning("{} : There is no tag <a class='in-listingCardTitle'> in the tag <li class='nd-list__item in-searchLayoutListItem'> : property {}/{} in {}.".format(self.scraper, index+1, len(lis), url))
                    self.scraper = "selenium" if self.scraper == "bs4" else None    # Update scraper to use
                    logging.info("Scraper set to : {}.".format(self.scraper))
                    return

        else:

            logging.warning("{} : The tag <li class='nd-list__item in-searchLayoutListItem'> doesn't exist in {}.".format(self.scraper, url))
            self.scraper = "selenium" if self.scraper == "bs4" else None    # Update scraper to use
            logging.info("Scraper set to : {}.".format(self.scraper))
            return
    
    ## Scrape the overview page ##
    ## The goal is to get the url of each property contained in the overview page ##
    ## REMARK : For some overview page, beautifulsoup is not enough to get the complete source code (I don't know why). ##
    ##          That's why, this function starts by using beautifulsoup. If the url is not found, it tries with selenium. ##
    def __Scrape_overview_page(self, url):

        # Try to get url with beautifulsoup
        if self.scraper == "bs4":

            # Get the source code
            source_code, _ = Web_page_source_code_robustification(url, 2, self.headers)

            # Check if the source code was scraped
            if source_code:
                    
                self.__Get_url_property(source_code, url)

        # Try to get url with selenium
        if self.scraper == "selenium":

            # Open a navigator
            self.Open_webdriver()

            # Access to the website
            self.Access_website(url)

            # Get the source code
            source_code = BeautifulSoup(self.driver.page_source, features = "lxml")

            # Close navigator
            self.Close_webdriver()
            
            # Get the url
            self.__Get_url_property(source_code, url)

        # no url is found
        if not self.scraper:

            logging.warning("No property can be scraped from the overview page {}.".format(url))

        
    ## Scrape the overview pages to get the url of each property ##
    def Scrape_overview_pages(self, url):

        logging.info("Start to scrape overview pages.")
        print("Start to scrape overview pages.")

        # Get the number of pages
        page_count = self.__Search_page_count(url)

        # Scrape each overview page
        for page in tqdm.tqdm(range(1, page_count + 1), "Get the url of each property"):

            # Update current url with the url of the new page
            if page > 1 and url:
                
                url = self.__Search_url_specific_page(url, page)

            # Url has to be different than None
            if url:

                # Scrape data
                self.__Scrape_overview_page(url)

            else:

                logging.error("The url of the overview page is None. Impossible to continue.")
                break

        # Reset scraper
        self.scraper = "bs4"

        logging.info("End to scrape overview pages.\n")
        print("End to scrape overview pages.\n")

    
    ## Transfer data from dictionnary to dataframe ##
    def __Transfer_dictio_to_dataframe(self, dict_data, index, url):

        # Get parent ID
        self.df_property.at[index, "ID parent"]                        = Get_value_dictionnary(dict_data, ["props", "pageProps", "parentId"])

        # Focus on a part of the dictionnary
        data = Get_value_dictionnary(dict_data, ["props", "pageProps", "detailData", "realEstate"])
        if data:

            # In props/pageProps/detailData/realEstate
            self.df_property.at[index, "Nom"]                           = data.get("title")
            self.df_property.at[index, "Statut"]                        = data.get("contractValue")
            self.df_property.at[index, "Projet Neuf"]                   = data.get("isNew")

            # In props/pageProps/detailData/realEstate/properties[0]
            property_data = data.get("properties")
            if property_data:

                property_data = property_data[0]

                self.df_property.at[index, "ID"]                        = property_data.get("id")
                self.df_property.at[index, "Type"]                      = property_data.get("typologyValue")
                self.df_property.at[index, "Disponibilité"]             = property_data.get("availability")
                self.df_property.at[index, "Surface"]                   = property_data.get("surfaceValue").replace("m²", "") if property_data.get("surfaceValue") else None
                self.df_property.at[index, "Nombre de chambres"]        = property_data.get("bedRoomsNumber")
                self.df_property.at[index, "Salle de bain/douche"]      = property_data.get("bathrooms")
                self.df_property.at[index, "Année de construction"]     = property_data.get("buildingYear")
                self.df_property.at[index, "Elévateur"]                 = property_data.get("elevator")
                self.df_property.at[index, "garage"]                    = property_data.get("garage")
                self.df_property.at[index, "Nombre total d'étages"]     = property_data.get("floors")
                self.df_property.at[index, "Etage"]                     = Get_value_dictionnary(property_data, ["floor", "value"])

                # In props/pageProps/detailData/realEstate/properties[0]/energy
                energy_data = property_data.get("energy")
                if energy_data:

                    self.df_property.at[index, "Consommation d'énergie"]        = Get_value_dictionnary(energy_data, ["class", "name"])
                    self.df_property.at[index, "Classe d'isolation thermique"]  = Get_value_dictionnary(energy_data, ["thermalInsulation", "consumption", "name"])
                    self.df_property.at[index, "Chauffage"]                     = energy_data.get("heatingType")

                # In props/pageProps/detailData/realEstate/properties[0]/location
                location_data = property_data.get("location")
                if location_data:
                    
                    self.df_property.at[index, "Pays"]                  = Get_value_dictionnary(location_data, ["nation", "name"])
                    self.df_property.at[index, "Province"]              = location_data.get("province")
                    self.df_property.at[index, "City"]                  = location_data.get("city")
                    self.df_property.at[index, "Macrozone"]             = location_data.get("macrozone")
                    self.df_property.at[index, "MacrozoneId"]           = location_data.get("macrozoneId")
                    self.df_property.at[index, "Adresse"]               = location_data.get("address")
                    self.df_property.at[index, "Numéro"]                = location_data.get("streetNumber")
                    self.df_property.at[index, "Latitude"]              = location_data.get("latitude")
                    self.df_property.at[index, "Longitude"]             = location_data.get("longitude")

                # In props/pageProps/detailData/realEstate/properties[0]/price
                price_data = property_data.get("price")
                if price_data:
                    
                    self.df_property.at[index, "Prix"]                      = price_data.get("value")
                    self.df_property.at[index, "Prix min"]                  = "".join(price_data.get("minValue").replace("€", "").split(" ")) if price_data.get("minValue") else None
                    self.df_property.at[index, "Prix max"]                  = "".join(price_data.get("maxValue").replace("€", "").split(" ")) if price_data.get("maxValue") else None
                    self.df_property.at[index, "Prix/m2"]                   = "".join(price_data.get("pricePerSquareMeter").replace("€/m²", "").split(" ")) if price_data.get("pricePerSquareMeter") else None
                
            else:

                logging.warning("'properties' was not found in the json : {}.".format(url))

        else:

            logging.warning("The data of {} were not scrapped.".format(url))

    ## Scrape property page ##
    def __Scrape_property_data(self, url):

        # Get the source code
        source_code, _ = Web_page_source_code_robustification(url, 2, self.headers)

        # Check if the source code was scraped
        if source_code:

            # First free index in the dataframe
            index = len(self.df_property)

            # Add the URL to the dataframe. If the source code was not scraped, that means that the url won't be added in the dataframe.
            self.df_property.at[index, "URL"] = url

            # Search the tag 'script' containing the data
            data_json = self.__Get_json_data(source_code, url)
            if data_json:

                #Write_json('test_solo_bel.json', data_json)
                self.__Transfer_dictio_to_dataframe(data_json, index, url)

            else:

                logging.warning("The script id='__NEXT_DATA__' was not found in {}.".format(url))

    ## Scrape the property pages ##
    def Scrape_property_pages(self):

        logging.info("Start to scrape property pages.")
        print("Start to scrape property pages.")

        logging.info("Number of properties : {}.".format(len(self.dict_href_properties)))

        for href_property in tqdm.tqdm(self.dict_href_properties, desc = "Scrape the data of each property"):

            self.__Scrape_property_data(href_property)
            time.sleep(1)

        logging.info("End to scrape property pages.\n")
        print("End to scrape property pages.\n")

    ## Save data ##
    def Save_df(self):

        # Write the xlsx
        with pd.ExcelWriter(self.filename_output, engine = "xlsxwriter") as writer:
        
            self.df_property.to_excel(writer, sheet_name = "Propriétés", index = False)
        
        logging.info("The dataframes were saved at '{}'.\n".format(self.filename_output))