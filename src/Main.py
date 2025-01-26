import logging
import time
from datetime import timedelta

from Immotop import *
from Tools.Tool_functions import *

url_template = "https://www.immotop.lu/search-list/?idContratto=1{type}{subtype}&criterio=rilevanza&__lang=fr{location}"
translate_to_url = {    
                        "Belgique"                          : "BE",
                        "France"                            : "FR",
                        "Luxembourg"                        : "LU",
                        "Allemagne"                         : "DE",
                        "Maisons - Appartements"            : "1",
                        "Appartement"                       : "4",
                        "Penthouse-Mansarde"                : "5",
                        "Duplex - Triplex"                  : "114",
                        "Maison"                            : "7",
                        "Loft"                              : "31",
                        "Studio"                            : "113",
                        "Maison de campagne"                : "11",
                        "Villa"                             : "12",
                        "Immobilier neuf"                   : "6",
                        "Appartement neuf"                  : "54",
                        "Penthouse-Mansarde neuf"           : "85",
                        "Loft neuf"                         : "60",
                        "Villa - Pavillon"                  : "58",
                        "Box Auto"                          : "57",
                        "Bureau"                            : "56",
                        "Magasin"                           : "55",
                        "Entrepot"                          : "61",
                        "Hangar"                            : "59",
                        "Box - Parking"                     : "22",
                        "Immeubles - Edifices"              : "20",
                        "Bureaux - coworking"               : "23",
                        "Magasins - Locaux commerciaux"     : "26",                          
                        "Local commercial"                  : "1",
                        "Activite commercial"               : "2",
                        "Entrepots - depots"                : "21",
                        "Hangar - Locaux industriels"       : "25",
                        "Terrains"                          : "24",
                        "Terrain Agricole"                  : "106",
                        "Terrain constructible"             : "107"
                    }

# translate_to_url = {    
#                         "Belgique"                          : "belgique-pays",
#                         "France"                            : "france-pays",
#                         "Luxembourg"                        : "luxembourg-pays",
#                         "Allemagne"                         : "allemagne-pays",
#                         "Appartement"                       : "https://www.immotop.lu/vente-appartements/{}/?criterio=rilevanza",
#                         "Penthouse-Mansarde"                : "https://www.immotop.lu/vente-penthouses/{}/?criterio=rilevanza",
#                         "Duplex - Triplex"                  : "https://www.immotop.lu/vente-duplex/{}/?criterio=rilevanza",
#                         "Maison"                            : "https://www.immotop.lu/vente-maisons/{}/?criterio=rilevanza",
#                         "Loft"                              : "https://www.immotop.lu/vente-loft/{}/?criterio=rilevanza",
#                         "Studio"                            : "https://www.immotop.lu/vente-studios/{}/?criterio=rilevanza",
#                         "Maison de campagne"                : "https://www.immotop.lu/vente-ferme/{}/?criterio=rilevanza",
#                         "Villa"                             : "https://www.immotop.lu/vente-villas/{}/?criterio=rilevanza",
#                         "Appartement neuf"                  : "https://www.immotop.lu/immobilier-neuf/appartements-{}/?criterio=rilevanza",
#                         "Penthouse-Mansarde neuf"           : "https://www.immotop.lu/immobilier-neuf/penthouses-{}/?criterio=rilevanza",
#                         "Loft neuf"                         : "https://www.immotop.lu/immobilier-neuf/loft-{}/?criterio=rilevanza",
#                         "Villa - Pavillon"                  : "https://www.immotop.lu/immobilier-neuf/villas-{}/?criterio=rilevanza",
# #                        "Box Auto"                          : "https://www.immotop.lu/search-list/?idContratto=1&idCategoria=6&idTipologia%5B0%5D=57&criterio=rilevanza&__lang=fr&idNazione=DE&pag=1",
#                         "Bureau"                            : "https://www.immotop.lu/immobilier-neuf/bureaux-{}/?criterio=rilevanza",
#                         "Magasin"                           : "https://www.immotop.lu/immobilier-neuf/local-commercial-{}/?criterio=rilevanza",
#                         "Entrepot"                          : "https://www.immotop.lu/immobilier-neuf/entrepots-{}/?criterio=rilevanza",
#                         "Hangar"                            : "https://www.immotop.lu/immobilier-neuf/hangars-{}/?criterio=rilevanza",
#                         "Box - Parking"                     : "https://www.immotop.lu/vente-parkings/{}/?criterio=rilevanza",
#                         "Immeubles - Edifices"              : "https://www.immotop.lu/vente-immeubles/{}/?criterio=rilevanza",
#                         "Bureaux - coworking"               : "https://www.immotop.lu/vente-bureaux/{}/?criterio=rilevanza",
#                         "Local commercial"                  : "https://www.immotop.lu/vente-local-commercial/{}/?criterio=rilevanza&tipologiaCommerciale=1",
#                         "Activite commercial"               : "https://www.immotop.lu/vente-fonds-de-commerce/{}/?criterio=rilevanza",
#                         "Entrepots - depots"                : "https://www.immotop.lu/vente-entrepots/{}/?criterio=rilevanza",
#                         "Hangar - Locaux industriels"       : "https://www.immotop.lu/vente-hangars/{}/?criterio=rilevanza",
#                         "Terrain Agricole"                  : "https://www.immotop.lu/vente-terrains/{}/?criterio=rilevanza&idTipologia=106",
#                         "Terrain constructible"             : "https://www.immotop.lu/vente-terrains/{}/?criterio=rilevanza"
#                     }


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
    
    # Get user parameters #
    json_path = input("Enter the path of the json file : ")
    data_json = Read_json(json_path)

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