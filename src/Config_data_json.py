from pydantic import BaseModel, Field

#########################################
#### Use to validate the config json ####
#########################################
class LocationModel(BaseModel):
    Belgique    : bool
    France      : bool
    Luxembourg  : bool
    Allemagne   : bool

class StatutModel(BaseModel):
    vente       : bool
    location    : bool

class MaisonsAppartementsModel(BaseModel):
    Appartement         : bool
    Penthouse_Mansarde  : bool = Field(alias = "Penthouse-Mansarde")
    Duplex_Triplex      : bool = Field(alias = "Duplex - Triplex")
    Maison              : bool
    Loft                : bool
    Studio              : bool
    Maison_de_campagne  : bool = Field(alias = "Maison de campagne")
    Villa               : bool

class ImmobilierNeufModel(BaseModel):
    Appartement_neuf        : bool = Field(alias = "Appartement neuf")
    Penthouse_Mansarde_neuf : bool = Field(alias = "Penthouse-Mansarde neuf")
    Loft_neuf               : bool = Field(alias = "Loft neuf")
    Villa_Pavillon          : bool = Field(alias = "Villa - Pavillon")
    Box_Auto                : bool = Field(alias = "Box Auto")
    Bureau                  : bool
    Magasin                 : bool
    Entrepot                : bool
    Hangar                  : bool

class MagasinsLocauxModel(BaseModel):
    Local_commercial    : bool = Field(alias = "Local commercial")
    Activite_commercial : bool = Field(alias = "Activite commercial")

class TerrainsModel(BaseModel):
    Terrain_Agricole        : bool = Field(alias = "Terrain Agricole")
    Terrain_constructible   : bool = Field(alias = "Terrain constructible")

class ConfigModel(BaseModel):
    location                    : LocationModel
    statut                      : StatutModel
    Maisons_Appartements        : MaisonsAppartementsModel  = Field(alias = "Maisons - Appartements")
    Chambres                    : bool
    Immobilier_neuf             : ImmobilierNeufModel       = Field(alias = "Immobilier neuf")
    Box_Parking                 : bool                      = Field(alias = "Box - Parking")
    Immeubles_Edifices          : bool                      = Field(alias = "Immeubles - Edifices")
    Bureaux_coworking           : bool                      = Field(alias = "Bureaux - coworking")
    Magasins_Locaux_commerciaux : MagasinsLocauxModel       = Field(alias = "Magasins - Locaux commerciaux")
    Entrepots_depots            : bool                      = Field(alias = "Entrepots - depots")
    Hangar_Locaux_industriels   : bool                      = Field(alias = "Hangar - Locaux industriels")
    Terrains                    : TerrainsModel