import pandas as pd
import tqdm
import logging

from Tools.Scrape import *
#from Tools.Tool_functions import *

#### Class to scrape Propertyweb ####
class Immotop():

    ## Initialization ##
    def __init__(self, filename_output):
        
        self.filename_excel = filename_output   # filename of the output
        self.df = pd.DataFrame()                # Dataframe to store data
        self.dict_href_properties = {}          # dictionnary of property hrefs (use a dictionary to avoid duplicates and keep the order)

        # headers used by "requests"
        self.headers = {                                                                                   
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
                            'Accept-Language': 'en-US,en;q=0.9',
                            'Accept-Encoding': 'gzip, deflate, br',
                            'Connection': 'keep-alive',
                        }
    
    ## Get the number of pages in the URL ##
    ## Return the number of pages ##
    def __Get_page_count(self, url):

        # Get the source code
        source_code, _ = Web_page_source_code_robustification(url, 2, self.headers)

        # Check if the source code was scraped
        if source_code:

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
                        logging.info("Number of page : {}.".format(count))
                        return count
                    
                    # The list is empty
                    else:
                        
                        logging.warning("The list of pages is empty : {}.".format(url))

                else:

                    logging.warning("There is no <a> and <div> in the tag <div class='in-pagination__list'> in {}.".format(url))

            else:

                logging.warning("The tag <div class='in-pagination__list'> doesn't exist in {}.".format(url))

        return 1

    ## Get the url of a specific page ##  
    ## Return the url of this specific page (None if not found) ##
    def __Get_url_specific_page(self, url, searched_page):

        # Get the source code
        source_code, _ = Web_page_source_code_robustification(url, 2, self.headers)

        # Check if the source code was scraped
        if source_code:

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
                                
                                return href 
                            
                            else:

                                logging.warning("There is no href in <a>{}</a> in {}.".format(str(page), url))
                    
                else:

                    logging.warning("There is no <a> and <div> in the tag <div class='in-pagination__list'> in {}.".format(url))

            else:

                logging.warning("The tag <div class='in-pagination__list'> doesn't exist in {}.".format(url))
    
        return None
    
    ## Scrape the overview page ##
    ## The goal is to get the url of each property contained in the overview page ##
    def __Scrape_overview_page(self, url):

        # Get the source code
        source_code, _ = Web_page_source_code_robustification(url, 2, self.headers)

        # Check if the source code was scraped
        if source_code:
             
            # Search the url of each property contained in the overview page
            lis = source_code.find_all("li", {"class" : "nd-list__item in-searchLayoutListItem"})
            if lis:

                for li in lis:

                    title = li.find("a", {"class" : "in-listingCardTitle"})
                    if title:

                        href = title.get("href")
                        if href:

                            if href not in self.dict_href_properties:

                                self.dict_href_properties[href] = None

                        else:

                            logging.warning("The attribute 'href' doesn't exist in the tag <a class='in-listingCardTitle'> : {}.".format(url))

                    else:

                        logging.warning("There is no tag <a class='in-listingCardTitle'> in the tag <li class='nd-list__item in-searchLayoutListItem'> in {}.".format(url))

            else:

                logging.warning("The tag <li class='nd-list__item in-searchLayoutListItem'> doesn't exist. No property can be scraped from the overview page {}.".format(url))

        
    # Scrape the overview pages ##
    def Scrape_overview_pages(self, url):

        logging.info("Start to scrape overview pages.")
        print("Start to scrape overview pages.")

        # Get the number of pages
        page_count = self.__Get_page_count(url)

        # Scrape each overview page
        for page in tqdm.tqdm(range(1, page_count + 1), "Get the url of each property"):

            # Update current url with the url of the new page
            if page > 1 and url:
                
                url = self.__Get_url_specific_page(url, page)

            # Url has to be different than None
            if url:

                # Scrape data
                self.__Scrape_overview_page(url)

        logging.info("End to scrape overview pages.\n")
        print("End to scrape overview pages.\n")

    ## Get the data contained in a tag 'script' starting with 'window.AT_HOME_APP' ##
    ## Return data in a dictionnary (None if data have not been found) ##
    def __Get_json_data(self, source_code, url):

        

    ## Scrape property page ##
    def __Scrape_property_data(self, url):

        # Get the source code
        source_code, _ = Web_page_source_code_robustification(url, 2, self.headers)

        # Check if the source code was scraped
        if source_code:

            # First free index in the dataframe
            index = len(self.df_configuration)

            # Add the URL to the dataframe. If the source code was not scraped, that means that the url won't be added in the dataframe.
            self.df.loc[index, "URL"] = url

            # Search the tag 'script' containing the data
            data_json = self.__Get_json_data(source_code, url)

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