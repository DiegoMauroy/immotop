from pydantic import model_validator
from typing import List, ClassVar, Optional
from datetime import datetime

from Tools.Converts import *
from Tools.Dictionnary_tools import *
from Tools.Pydantic import *

########################################
#### Prepare data for the dataframe ####
########################################

## Class to prepare data for the dataframe "Parent"
class ParentDataJson(BaseModelWithIgnoreExtra):

    url                     : str
    id                      : int
    name                    : Optional[str]
    description             : Optional[str]

    country                 : Optional[str]
    province                : Optional[str]
    city                    : Optional[str]
    macrozone               : Optional[str]
    macrozoneid             : Optional[int]
    address                 : Optional[str]
    number                  : Optional[str]
    latitude                : Optional[float]
    longitude               : Optional[float]

    status                  : Optional[str]
    type                    : Optional[str]
    new_project             : Optional[bool]
    availability            : Optional[str]
    building_year           : Optional[int]

    price                   : Optional[float]
    price_m2                : Optional[float]
    min_price               : Optional[float]
    max_price               : Optional[float]
    
    surface                 : Optional[float]
    bedroom_count           : Optional[int]
    bathroom_count          : Optional[int]
    floor_count             : Optional[int]
    floor                   : Optional[str]
    elevator                : Optional[bool]

    energy_consumption      : Optional[str]
    thermal_isolation_class : Optional[str]
    heating_type            : Optional[str]

    last_update             : Optional[datetime]


    mapping_immotop_to_dataframe : ClassVar[dict[Optional[str], List[Optional[str]]]] = {
                                                                                            "url"                     : ["url"],
                                                                                            "id"                      : ["props", "pageProps", "detailData", "realEstate", "properties", "id"],
                                                                                            "name"                    : ["props", "pageProps", "detailData", "realEstate", "title"],
                                                                                            "description"             : ["props", "pageProps", "detailData", "realEstate", "properties", "description"],
                                                                                            
                                                                                            "country"                 : ["props", "pageProps", "detailData", "realEstate", "properties", "location", "nation", "name"],
                                                                                            "province"                : ["props", "pageProps", "detailData", "realEstate", "properties", "location", "province"],
                                                                                            "city"                    : ["props", "pageProps", "detailData", "realEstate", "properties", "location", "city"],
                                                                                            "macrozone"               : ["props", "pageProps", "detailData", "realEstate", "properties", "location", "macrozone"],
                                                                                            "macrozoneid"             : ["props", "pageProps", "detailData", "realEstate", "properties", "location", "macrozoneId"],
                                                                                            "address"                 : ["props", "pageProps", "detailData", "realEstate", "properties", "location", "address"],
                                                                                            "number"                  : ["props", "pageProps", "detailData", "realEstate", "properties", "location", "streetNumber"],
                                                                                            "latitude"                : ["props", "pageProps", "detailData", "realEstate", "properties", "location", "latitude"],
                                                                                            "longitude"               : ["props", "pageProps", "detailData", "realEstate", "properties", "location", "longitude"],

                                                                                            "status"                  : ["props", "pageProps", "detailData", "realEstate", "contractValue"],
                                                                                            "type"                    : ["props", "pageProps", "detailData", "realEstate", "properties", "typologyValue"],
                                                                                            "new_project"             : ["props", "pageProps", "detailData", "realEstate", "isNew"],
                                                                                            "availability"            : ["props", "pageProps", "detailData", "realEstate", "properties", "availability"],
                                                                                            "building_year"           : ["props", "pageProps", "detailData", "realEstate", "properties", "buildingYear"],

                                                                                            "price"                   : ["props", "pageProps", "detailData", "realEstate", "properties", "price", "value"],
                                                                                            "price_m2"                : ["props", "pageProps", "detailData", "realEstate", "properties", "price", "pricePerSquareMeter"],
                                                                                            "min_price"               : ["props", "pageProps", "detailData", "realEstate", "properties", "price", "minValue"],
                                                                                            "max_price"               : ["props", "pageProps", "detailData", "realEstate", "properties", "price", "maxValue"],

                                                                                            "surface"                 : ["props", "pageProps", "detailData", "realEstate", "properties", "surfaceValue"],
                                                                                            "bedroom_count"           : ["props", "pageProps", "detailData", "realEstate", "properties", "bedRoomsNumber"],
                                                                                            "bathroom_count"          : ["props", "pageProps", "detailData", "realEstate", "properties", "bathrooms"],
                                                                                            "floor_count"             : ["props", "pageProps", "detailData", "realEstate", "properties", "floors"],
                                                                                            "floor"                   : ["props", "pageProps", "detailData", "realEstate", "properties", "floor", "value"],
                                                                                            "elevator"                : ["props", "pageProps", "detailData", "realEstate", "properties", "elevator"],

                                                                                            "energy_consumption"      : ["props", "pageProps", "detailData", "realEstate", "properties", "energy", "class", "name"],
                                                                                            "thermal_isolation_class" : ["props", "pageProps", "detailData", "realEstate", "properties", "energy", "thermalInsulation", "consumption", "name"],
                                                                                            "heating_type"            : ["props", "pageProps", "detailData", "realEstate", "properties", "energy", "heatingType"],

                                                                                            "last_update"             : ["props", "pageProps", "detailData", "realEstate", "properties", "lastUpdate"]
                                                                                        }
    
    ## Format the input dictionnary.
    ## This function replaces the list associated to the key 'properties' by the first element of this list.
    ## Thanks to that, mapping fonction can use 'Get_value_dictionnary()' to browse the input data.
    @classmethod
    def format_dictionnary(cls, values : dict):

        # 'properties' is a list, only the first item is interesting
        properties = Get_value_dictionnary(values, ["props", "pageProps", "detailData", "realEstate", "properties"])
        if isinstance(properties, dict):

            return values
                
        elif isinstance(properties, list):

            values["props"]["pageProps"]["detailData"]["realEstate"]["properties"] = properties[0]
            return values
        
        else:

            raise ValueError("The key 'properties' doesn't exist or is not a list or a dictionnary.")

    ## Mapping (dictio -> pydantic)
    @classmethod
    def mapping(cls, values : dict):

        prepared_values = {}
        for field, path in cls.mapping_immotop_to_dataframe.items():

            # Get the type of the treated field
            field_type = cls.model_fields[field].annotation 

            # Manage integer fields
            if field_type is int or Is_optional_of(field_type, int):

                data = Get_value_dictionnary(values, path)

                prepared_values[field] = Convert_to_int(data, True) if data is not None else data
                
            # Manage float fields
            elif Is_optional_of(field_type, float):

                data = Get_value_dictionnary(values, path)

                if field in ["price", "price_m2", "min_price", "max_price", "surface"]:

                    # If the field is a price or surface, clean the data before parsing it
                    prepared_values[field] = Convert_to_float(data, True) if data is not None else data

                else:

                    # For other float fields, parse the data without cleaning it
                    prepared_values[field] = Convert_to_float(data, False) if data is not None else data

            # Manage datetime fields
            elif Is_optional_of(field_type, datetime):

                data = Get_value_dictionnary(values, path)

                if isinstance(data, str):

                    # find all dates in the data
                    dates = re.findall(r"\b\d{2}/\d{2}/\d{2}(?:\d{2})?\b", data)
                    if len(dates) > 0:

                        # If the field is a date, parse it
                        prepared_values[field] = Convert_to_datetime(dates[0], ["%d/%m/%Y", "%d/%m/%y"], 1000)

                    else:

                        prepared_values[field] = None

                else:

                    raise ValueError("The value for field '{field}' is not string: {data}".format(field = field, data = data))
                
            # Other fields
            else:
            
                prepared_values[field] = Get_value_dictionnary(values, path)

        return prepared_values
    
    ## Prepare data
    @model_validator(mode = 'before')
    def convert_dictio_to_pydantic(cls, values : dict):

        # format data
        formated_values = cls.format_dictionnary(values)

        # map data
        mapped_values = cls.mapping(formated_values)

        return mapped_values
    
## Class to prepare data for the dataframe "Property" (depend on Parent)
class PropertyDataJson(ParentDataJson):

    id_parent : Optional[int]

    mapping_immotop_to_dataframe = {
                                        **ParentDataJson.mapping_immotop_to_dataframe,
                                        "id_parent" : ["props", "pageProps", "parentId"]
                                    }