"""
Script de Python hecho para transformar los CSVs importados de Google Earth Engine para mayor claridad
en los análisis, facilidad para realizar gráficos y accesibilidad.

La transformación se centrará en agrupar las variables de acuerdo con su temporalidad así como la 
cobertura geográfica que tengan.

Para el caso de los archivos CSV que tengan los datos mensuales, estos pasarán de un formato wide a long.

Tras ejecutar el script se tendrán guardados en la carpeta ee_terraclimate_db 34 archivos CSV:
- 1 archivo CSV que contenga los valores anuales de las variables climatológicas para cada
  nivel geográfico de México (nacional, entidades y municipios)
- 1 archivo CSV que contenga los valores mensuales de las variables climatológicas para los 
  niveles nacional y entidades de México
- 32 archivos CSVs que contengan los valores mensuales de las variables climatológicas para 
  cada uno de los municipios de las 32 entidades de México.

Autor: Miguel Isaac Arroyo Velázquez

"""
import numpy as np
import pandas as pd
import geopandas
import os
import re
import functools

# - - Start Funciones
def etiquetar_categoria_pdsi(valor):
    if valor <= -4:
        return "Sequía extrema"
    elif -4 < valor <= -3:
        return "Sequía severa"
    elif -3 < valor <= -2:
        return "Sequía moderada"
    elif -2 < valor <= -1:
        return "Sequía media"
    elif -1 < valor <= -0.5:
        return "Sequía incipiente"
    elif -0.5 < valor <= 0.5:
        return "Condiciones normales"
    elif 0.5 < valor <= 1:
        return "Humedad incipiente"
    elif 1 < valor <= 2:
        return "Poca humedad"
    elif 2 < valor <= 3:
        return "Humedad moderada"
    elif 3 < valor <= 4:
        return "Muy húmedo"
    elif valor > 4:
        return "Extremadamente húmedo"
    else:
        return np.nan
# - - End Funciones


current_directory = os.getcwd()
path2imports = current_directory + "/datos/ee_terraclimate_imports/"
list_all_csvs_with_zscore = os.listdir(path2imports)
# Ignorar Z-score de temperaturas ya que no formaran de la base de datos
list_all_csvs = [csv_name for csv_name in list_all_csvs_with_zscore if "_zscore_" not in csv_name]
list_all_csvs.sort()

# = = Valores anuales nacional + entidades + municipios = = #
# - - Nacional - - #
list_csvs_nac_year = [csv_name for csv_name in list_all_csvs if "_nac_year_" in csv_name]
list_df_nac_year = list()

for csv_file in list_csvs_nac_year:
    df_temporal = pd.read_csv(path2imports + csv_file)
    df_temporal["cve_geo"] = "00"
    df_temporal["cve_ent"] = "00"
    df_temporal["date_year"] = df_temporal["date_year"].astype(int)
    df_temporal = df_temporal[["cve_geo", "cve_ent", "date_year", "mean"]]
    df_temporal.columns = ["cve_geo", "cve_ent", "date_year", re.search("ts_(.*)_nac_year", csv_file).group(1)]
    list_df_nac_year.append(df_temporal)

df_nac_year = functools.reduce(lambda df1,df2 : pd.merge(df1, df2, on = ["cve_geo","cve_ent","date_year"]), list_df_nac_year)

# - - Entidades - - #
list_csvs_ent_year = [csv_name for csv_name in list_all_csvs if "_ent_year_" in csv_name]
list_df_ent_year = list()

for csv_file in list_csvs_ent_year:
    df_temporal = pd.read_csv(path2imports + csv_file)
    df_temporal["cve_geo"] = df_temporal["CVEGEO"].apply(lambda x: f"0{str(x)}" if x <= 9 else str(x))
    df_temporal["cve_ent"] = df_temporal["CVEGEO"].apply(lambda x: f"0{str(x)}" if x <= 9 else str(x))
    df_temporal["date_year"] = df_temporal["date_year"].astype(int)
    df_temporal = df_temporal[["cve_geo", "cve_ent", "date_year", "mean"]]
    df_temporal.columns = ["cve_geo", "cve_ent", "date_year", re.search("ts_(.*)_ent_year", csv_file).group(1)]
    list_df_ent_year.append(df_temporal)

df_ent_year = functools.reduce(lambda df1,df2 : pd.merge(df1, df2, on = ["cve_geo","cve_ent","date_year"]), list_df_ent_year)

# - - Municipios - - #
list_csvs_mun_year = [csv_name for csv_name in list_all_csvs if "_mun_year_" in csv_name]
list_df_mun_year = list()

for csv_file in list_csvs_mun_year:
    df_temporal = pd.read_csv(path2imports + csv_file)
    df_temporal["cve_geo"] = df_temporal["CVEGEO"].apply(lambda x: f"0{str(x)}" if x <= 10_000 else str(x))
    df_temporal["cve_ent"] = df_temporal["CVE_ENT"].apply(lambda x: f"0{str(x)}" if x <= 9 else str(x))
    df_temporal["date_year"] = df_temporal["date_year"].astype(int)
    df_temporal = df_temporal[["cve_geo", "cve_ent", "date_year", "mean"]]
    df_temporal.columns = ["cve_geo", "cve_ent", "date_year", re.search("ts_(.*)_mun_year", csv_file).group(1)]
    list_df_mun_year.append(df_temporal)

df_mun_year = functools.reduce(lambda df1,df2 : pd.merge(df1, df2, on = ["cve_geo","cve_ent","date_year"]), list_df_mun_year)

# - - Nacional + Entidades + Municipios - - #
df_nac_ent_mun_year = pd.concat([df_nac_year, df_ent_year, df_mun_year]).reset_index(drop=True)
df_nac_ent_mun_year["date_year"] = df_nac_ent_mun_year["date_year"].astype(str) + "-06-30"

# = o = o = o = o = o = o = o = o = o = o = o = o = o = o = o = o = o = o = o = o = o = o = o = o

# = = Valores mensuales nacional + entidades = = #
list_months_num = list(map(lambda x: f"0{x}" if x <= 9 else str(x), range(1,13)))

# - - Nacional - - #
list_csvs_nac_month = [csv_name for csv_name in list_all_csvs if "_nac_month_" in csv_name]
list_df_nac_month = list()

for csv_file in list_csvs_nac_month:
    value_name = re.search("ts_(.*)_nac_month_", csv_file).group(1)
    df_temporal = pd.read_csv(path2imports + csv_file)
    df_temporal = df_temporal.melt(id_vars=["date_year"], value_vars= list_months_num, var_name = "date_month", value_name = value_name)
    df_temporal["cve_geo"] = "00"
    df_temporal["cve_ent"] = "00"
    df_temporal["date_year"] = df_temporal["date_year"].astype(int)
    df_temporal = df_temporal[["cve_geo", "cve_ent", "date_year", "date_month", value_name]]
    list_df_nac_month.append(df_temporal)

df_nac_month = functools.reduce(lambda df1,df2 : pd.merge(df1, df2, on = ["cve_geo","cve_ent","date_year","date_month"]), list_df_nac_month)

# - - Entidades - - #
list_csvs_ent_month = [csv_name for csv_name in list_all_csvs if "_ent_month_" in csv_name]
list_df_ent_month = list()

for csv_file in list_csvs_ent_month:
    value_name = re.search("ts_(.*)_ent_month_", csv_file).group(1)
    df_temporal = pd.read_csv(path2imports + csv_file)
    df_temporal = df_temporal.melt(id_vars=["CVEGEO","CVE_ENT","date_year"], value_vars= list_months_num, var_name = "date_month", value_name = value_name)
    df_temporal["cve_geo"] = df_temporal["CVEGEO"].apply(lambda x: f"0{str(x)}" if x <= 9 else str(x))
    df_temporal["cve_ent"] = df_temporal["CVE_ENT"].apply(lambda x: f"0{str(x)}" if x <= 9 else str(x))
    df_temporal["date_year"] = df_temporal["date_year"].astype(int)
    df_temporal = df_temporal[["cve_geo", "cve_ent", "date_year", "date_month", value_name]]
    list_df_ent_month.append(df_temporal)

df_ent_month = functools.reduce(lambda df1,df2 : pd.merge(df1, df2, on = ["cve_geo","cve_ent","date_year","date_month"]), list_df_ent_month)

# - - Nacional + Entidades - - #
df_nac_ent_month = pd.concat([df_nac_month, df_ent_month]).reset_index(drop = True)
df_nac_ent_month["date_year_month"] = df_nac_ent_month.apply(lambda row: f"{row['date_year']}-{row['date_month']}-15", axis = 1)
df_nac_ent_month = df_nac_ent_month.drop(columns = ["date_year", "date_month"])
df_nac_ent_month = df_nac_ent_month[['cve_geo', 'cve_ent', 'date_year_month', 'anomaly_pr_mean', 'anomaly_tmmn_mean', 'anomaly_tmmx_mean','pdsi_mean']]

# = o = o = o = o = o = o = o = o = o = o = o = o = o = o = o = o = o = o = o = o = o = o = o = o

# = = Valores mensuales municipios = = #
# - - Municipios - - #
list_csvs_mun_month = [csv_name for csv_name in list_all_csvs if "_mun_month_" in csv_name]
list_df_mun_month = list()

for csv_file in list_csvs_mun_month:
    value_name = re.search("ts_(.*)_mun_month_", csv_file).group(1)
    df_temporal = pd.read_csv(path2imports + csv_file)
    df_temporal = df_temporal.melt(id_vars=["CVEGEO","CVE_ENT","date_year"], value_vars= list_months_num, var_name = "date_month", value_name = value_name)
    df_temporal["cve_geo"] = df_temporal["CVEGEO"].apply(lambda x: f"0{str(x)}" if x <= 10_000 else str(x))
    df_temporal["cve_ent"] = df_temporal["CVE_ENT"].apply(lambda x: f"0{str(x)}" if x <= 9 else str(x))
    df_temporal["date_year"] = df_temporal["date_year"].astype(int)
    df_temporal = df_temporal[["cve_geo", "cve_ent", "date_year", "date_month", value_name]]
    list_df_mun_month.append(df_temporal)

df_mun_month = functools.reduce(lambda df1,df2 : pd.merge(df1, df2, on = ["cve_geo","cve_ent","date_year","date_month"]), list_df_mun_month)
df_mun_month["date_year_month"] = df_mun_month.apply(lambda row: f"{row['date_year']}-{row['date_month']}-15", axis = 1)
df_mun_month = df_mun_month.drop(columns = ["date_year","date_month"])
df_mun_month = df_mun_month[['cve_geo', 'cve_ent', 'date_year_month', 'anomaly_pr_mean', 'anomaly_tmmn_mean', 'anomaly_tmmx_mean', 'pdsi_mean']]

# = o = o = o = o = o = o = o = o = o = o = o = o = o = o = o = o = o = o = o = o = o = o = o = o

# = = Agregar nombres de entidades y municipios = = #
cve_names_ent = pd.read_csv(current_directory + "/datos/base_nombres_entidades.csv")[["cve_geo","nombre_estado_2"]]
cve_names_ent["cve_geo"] = cve_names_ent["cve_geo"].fillna(0).apply(lambda x: f"0{int(x)}" if x <= 9 else str(int(x)))
cve_names_mun = pd.read_csv(current_directory + "/datos/base_nombres_municipios.csv")
cve_names_mun["CVEGEO"] = cve_names_mun["CVEGEO"].apply(lambda x: f"0{x}" if x < 10000 else f"{x}")

# - - Valores anuales Nacional + Entidades + Municipios - - #
df_nac_ent_mun_year = pd.merge(left = df_nac_ent_mun_year, right = cve_names_ent, left_on = "cve_ent", right_on = "cve_geo", how = "left")\
                      .drop(columns = "cve_geo_y")\
                      .rename(columns = {"cve_geo_x": "cve_geo"})\
                      .merge(cve_names_mun, left_on = "cve_geo", right_on = "CVEGEO", how = "left")\
                      .drop(columns = "CVEGEO")\
                      .rename(columns = {"NOMGEO": "nombre_municipio", "nombre_estado_2": "nombre_estado"})

df_nac_ent_mun_year["nombre_municipio"] = df_nac_ent_mun_year["nombre_municipio"].fillna("Estados_Nacionales")

# - - Valores mensuales Nacional + Entidades - - #
df_nac_ent_month = df_nac_ent_month.merge(right = cve_names_ent, on = "cve_geo", how = "left").rename(columns = {"nombre_estado_2" : "nombre_estado"})

# - - Valores mensuales Municipios - - #
df_mun_month = df_mun_month.merge(right = cve_names_mun, left_on = "cve_geo", right_on = "CVEGEO", how = "left")\
                           .drop(columns = "CVEGEO").rename(columns = {"NOMGEO":"nombre_municipio"})

# = o = o = o = o = o = o = o = o = o = o = o = o = o = o = o = o = o = o = o = o = o = o = o = o

# = = Categoría de PDSI = = #

df_nac_ent_mun_year["mean_pdsi_categoria"] = df_nac_ent_mun_year["pdsi_mean"].apply(etiquetar_categoria_pdsi)
df_nac_ent_month["mean_pdsi_categoria"] = df_nac_ent_month["pdsi_mean"].apply(etiquetar_categoria_pdsi)
df_mun_month["mean_pdsi_categoria"] = df_mun_month["pdsi_mean"].apply(etiquetar_categoria_pdsi)

# = = Guardar los 34 CSVs = = #
list_cve_ent = list(map(lambda x: f"0{str(x)}" if x <= 9 else str(x), range(1,33)))

df_nac_ent_mun_year.to_csv(current_directory + "/datos/ee_terraclimate_db/" + "ts_nac-ent-mun_year_terraclimate.csv", index = False)
df_nac_ent_month.to_csv(current_directory + "/datos/ee_terraclimate_db/" + "ts_nac-ent_month_terraclimate.csv", index = False)

for estado in list_cve_ent:
    df_mun_month[df_mun_month["cve_ent"] == estado].to_csv(current_directory + "/datos/ee_terraclimate_db/" + f"ts_{estado}mun_month_terraclimate.csv", index = False)