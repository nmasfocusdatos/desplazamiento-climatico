"""
El objetivo de este código es extraer información de las badnas del conjunto de datos TerraClimate 
que se encuentra en al plataforma Google Earth Engine.

La información se limita geográficamente a México (país, estados y municipios) a los años a partir 
de 1960 a 2022.

Para mayor información del código, visitar la documentación. 
Para mayor información de Google Earth Engine, visitar -> https://earthengine.google.com/
Para mayor información del conjunto de datos TerraClimate, visitar -> https://developers.google.com/earth-engine/datasets/catalog/IDAHO_EPSCOR_TERRACLIMATE 

Autor: Miguel Isaac Arroyo Velázquez
"""

import ee
import geemap
ee.Initialize()
print("Earth Engine inicializado")
print("Empieza a correr el código...")

# = = = = Valores variables = = = = = = 
banda_interes = "pdsi"
type_of_geometry = "ent"
type_reducer_time = "year"
temp_zscore = False

# - - - - - - - - - - - - - - - - - - - - -
# banda_interes
dict_functions_scalling_var_int = {
    "pdsi": {
        "scalling_func" : lambda img: img.multiply(0.01).copyProperties(img, img.propertyNames()),
        "var_int_func": lambda img: img.copyProperties(img, img.propertyNames()),
    },
    "pr": {
        "scalling_func": lambda img: img.copyProperties(img, img.propertyNames()),
        "var_int_func": lambda img: img.subtract(mean_base_months).divide(mean_base_months).copyProperties(img, img.propertyNames())
    },
    "tmmx": {
        "scalling_func": lambda img: img.multiply(0.1).copyProperties(img, img.propertyNames()),
        "var_int_func": lambda img: img.subtract(mean_base_months).copyProperties(img, img.propertyNames()),
        "var_int_func_zscore": lambda img: img.subtract(mean_base_months).divide(std_base_months).copyProperties(img, img.propertyNames())
    },
    "tmmn": {
        "scalling_func": lambda img: img.multiply(0.1).copyProperties(img, img.propertyNames()),
        "var_int_func": lambda img: img.subtract(mean_base_months).copyProperties(img, img.propertyNames()),
        "var_int_func_zscore": lambda img: img.subtract(mean_base_months).divide(std_base_months).copyProperties(img, img.propertyNames())
    }
}

# type_of_geometry
if type_of_geometry == "mun":
    # Municipios
    fc = ee.FeatureCollection("projects/ee-unisaacarroyov/assets/GEOM-MX/MX_MUN_2022")
elif type_of_geometry == "ent":
    # Estados
    fc = ee.FeatureCollection("projects/ee-unisaacarroyov/assets/GEOM-MX/MX_ENT_2022")
elif type_of_geometry == "nac":
    # Nación
    fc = ee.FeatureCollection("USDOS/LSIB/2017").filter(ee.Filter.eq("COUNTRY_NA","Mexico"))

# type_reducer_time
dict_reducers = {
    "month": lambda number: final_data_img_coll
                            .filter(ee.Filter.eq("date_year", number))\
                            .first()\
                            .reduceRegions(reducer = ee.Reducer.mean(), collection = fc, scale = scale_img_coll)\
                            .map(lambda feature: ee.Feature(feature).set("date_year", number).setGeometry(None)),
    "year": lambda number: final_data_img_coll
                           .filter(ee.Filter.eq("date_year", number))\
                           .first()\
                           .reduce(ee.Reducer.mean())\
                           .reduceRegions(reducer = ee.Reducer.mean(), collection = fc, scale = scale_img_coll)\
                           .map(lambda feature: ee.Feature(feature).set("date_year", number).setGeometry(None))
}


# = = = = Valores constantes = = = = = 
img_coll = ee.ImageCollection("IDAHO_EPSCOR/TERRACLIMATE")
geom_mex = ee.FeatureCollection("USDOS/LSIB/2017").filter(ee.Filter.eq("COUNTRY_NA","Mexico")).first().geometry()
scale_img_coll = 4638.3
start_date_base = "1960-01-01"
end_date_base = "1989-12-31"
img_coll_start_year = 1960
img_coll_end_year = 2022
n_max_features = 3000

# - - Valor "constante" - - - - - 
str_folder = "name_of_folder"


# = = = = Funciones escenciales = = = = = =

def tag_month_year(img):
    full_date = ee.Date(ee.Number(img.get("system:time_start")))
    date_year = ee.Number(full_date.get("year"))
    date_month = ee.Number(full_date.get("month"))
    return img.set({"date_month": date_month, "date_year": date_year})

def func_base_mean(element):
    return data_image_coll_tag_year_month.filterDate(start_date_base, end_date_base).filter(ee.Filter.eq("date_month", element)).mean().set({"date_month": element})

def func_base_std(element):
    return data_image_coll_tag_year_month.filterDate(start_date_base, end_date_base).filter(ee.Filter.eq("date_month", element)).reduce(ee.Reducer.stdDev()).set({"date_month": element})

# = = = =  INICIO DE CÓDIGO  = = = = = = = = 

data_image_coll_tag_year_month = img_coll.select(banda_interes).filter(ee.Filter.bounds(geom_mex)).map(dict_functions_scalling_var_int[banda_interes]["scalling_func"]).map(tag_month_year)

# Media historica
list_img_to_img_coll_base_mean_months = ee.List.sequence(1,12,1).map(func_base_mean)
mean_base_months = ee.ImageCollection.fromImages(list_img_to_img_coll_base_mean_months).toBands().rename(["01","02","03","04","05","06","07","08","09","10","11","12"])

# std historica
list_img_to_img_coll_base_std_months = ee.List.sequence(1,12,1).map(func_base_std)
std_base_months = ee.ImageCollection.fromImages(list_img_to_img_coll_base_std_months).toBands().rename(["01","02","03","04","05","06","07","08","09","10","11","12"])

list_new_collection_by_year = ee.List.sequence(img_coll_start_year, img_coll_end_year).map(lambda element: data_image_coll_tag_year_month.filter(ee.Filter.eq("date_year", element)).toBands().set({"date_year": element}).rename(["01","02","03","04","05","06","07","08","09","10","11","12"]))

if temp_zscore == False:
    final_data_img_coll = ee.ImageCollection.fromImages(list_new_collection_by_year).map(dict_functions_scalling_var_int[banda_interes]["var_int_func"])
elif temp_zscore == True:
    final_data_img_coll = ee.ImageCollection.fromImages(list_new_collection_by_year).map(dict_functions_scalling_var_int[banda_interes]["var_int_func_zscore"])

list_fc_from_img_coll = ee.List.sequence(img_coll_start_year, img_coll_end_year).map(dict_reducers[type_reducer_time])

list_features_from_img_coll = list_fc_from_img_coll.map(lambda fc: ee.FeatureCollection(fc).toList(n_max_features)).flatten()

fc_final = ee.FeatureCollection(list_features_from_img_coll)

# = = = =  Exportar como CSV (a una carpeta de Google Drive) = = = = =
if temp_zscore == False:
    str_var_interes = lambda banda: f"anomaly_{banda}_" if banda in ["pr","tmmx","tmmn"] else f"{banda}_"
elif temp_zscore == True:
    str_var_interes = lambda banda: f"zscore_{banda}_" if banda in ["tmmx","tmmn"] else f"eliminar-error_"

str_description = "export_" + str_var_interes(banda_interes) + "mean_" + f"{type_of_geometry}_" + f"{type_reducer_time}_" + "terraclimate"
str_fileNamePrefix = "ts_" + str_var_interes(banda_interes) + "mean_" + f"{type_of_geometry}_" + f"{type_reducer_time}_" + "terraclimate"

geemap.ee_export_vector_to_drive(
    collection = fc_final,
    description= str_description,
    fileNamePrefix = str_fileNamePrefix,
    fileFormat = "CSV",
    folder = str_folder)