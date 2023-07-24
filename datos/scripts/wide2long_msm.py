"""
- - - - - -
01
- - - - - - 

Script hecho para transformar el conjunto de datos del Monitor de Sequía de México de un formato ancho (wide) a largo (long).
Esto con el objetivo de contar con un conjunto donde la manipulación de los datos se más facil en diferentes librerías de 
análisis de datos, tales como Pandas (Python) y dplyr (R)


Autor: Miguel Isaac Arroyo Velázquez

"""


import pandas as pd
import numpy as np
import os

path2data_msm = os.getcwd() + "/datos/msm/"
file_name_msm_excel = "MunicipiosSequia.xlsx"
file_name_msm_long = "MunicipiosSequia_long.csv"

excel_1 = pd.read_excel(path2data_msm + file_name_msm_excel, sheet_name=0)

# nombre de columnas a pivotear
pivot_columnas = excel_1.columns.values[9:].tolist()
id_columns = excel_1.columns.values[:9]
df = pd.melt(excel_1, id_vars=id_columns, value_vars=pivot_columnas, var_name="full_date", value_name="sequia")

df.to_csv(path2data_msm + file_name_msm_long, index=False)