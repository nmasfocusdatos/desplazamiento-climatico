"""
- - - - - -
03
- - - - - - 

Script hecho para crear dos archivos CSV:
    - rachas_sequia_municipios -> archivo que tiene en orden cronológico el inicio y final de 
      la categoría de sequía de un determinado municipio
    - rachas_maximas_sequia_municipios -> archivo que contiene únicamente las rachas máximas (mayor duración)
      de cada categoría de sequía del MSM

Autor: Miguel Isaac Arroyo Velázquez

"""


import pandas as pd
import numpy as np
import os
import sys

path2data_msm = os.getcwd() + "/datos/msm/"
file_name_msm_para_rachas = "MunipiosSequia_long_para_rachas.csv"
file_name_msm_rachas = "rachas_sequia_municipios.csv"
file_name_msm_rachas_maximas = "rachas_maximas_sequia_municipios.csv"

# = = = = = = PARAMETROS
version = 1
iteracion = 0

# = = = = = = FUNCIONES
def contar_rachas_municipio(dataframe, cve_concatenada_mun):
	dataframe_mun = dataframe.query(f"cve_concatenada == {int(cve_concatenada_mun)}")
	lista_sequias = dataframe_mun['sequia'].values.tolist()
	lista_fechas = dataframe_mun['full_date'].values.tolist()
	count = 1
	lista_count = list()

	for i in range(1, len(lista_sequias)):
		if lista_sequias[i] == lista_sequias[i-1]:
			count += 1
		else:
			lista_count.append((int(cve_concatenada_mun), lista_sequias[i-1], count, lista_fechas[i-count], lista_fechas[i-1]))
			count = 1
	lista_count.append((int(cve_concatenada_mun), lista_sequias[-1], count, lista_fechas[-count], lista_fechas[-1]))

	dataframe_rachas = pd.DataFrame(lista_count, columns = ['cve_concatenada','sequia','racha','full_date_start_racha','full_date_end_racha'])
	dataframe_rachas['full_date_start_racha'] = pd.to_datetime(dataframe_rachas['full_date_start_racha'])
	dataframe_rachas['full_date_end_racha'] = pd.to_datetime(dataframe_rachas['full_date_end_racha'])
	dataframe_rachas['racha_meses'] = (dataframe_rachas['full_date_end_racha']-dataframe_rachas['full_date_start_racha'])/np.timedelta64(1, 'M')

	return dataframe_rachas

def obtener_rachas_maximas(dataframe, group_by = "sequia", rachas_name = "racha_meses"):
	idx_max = dataframe.groupby(group_by)[rachas_name].idxmax().values.tolist()
	return dataframe.loc[idx_max]

# = = = = = = CODIGO
# Lectura de datos
datos_sequia_municipios = pd.read_csv(path2data_msm + file_name_msm_para_rachas)

# Lista de códigos de municipios
lista_cve_concatenada = datos_sequia_municipios['cve_concatenada'].unique().tolist()
lista_dfs_rachas = list()
lista_dfs_rachas_max = list()

for i in range(iteracion, len(lista_cve_concatenada)):
	try:
		print(f"Iteración: {i}")
		df_rachas = contar_rachas_municipio(dataframe = datos_sequia_municipios,
											cve_concatenada_mun = lista_cve_concatenada[i])
		print("Lista las rachas")
		df_rachas_max = obtener_rachas_maximas(dataframe = df_rachas)
		print("Lista las rachas máximas")
		lista_dfs_rachas.append(df_rachas)
		lista_dfs_rachas_max.append(df_rachas_max)
	except (Exception, KeyboardInterrupt):
		print(f"A guardar todo porque sí. Nos quedamos en la iteración {i}")
		# Concatenar toda la información y guardar
		df_rachas_mun = pd.concat(lista_dfs_rachas).reset_index(drop=True)
		print("Guardando archivo de rachas...")
		df_rachas_mun.to_csv(os.getcwd()+f"/data/rachas_municipios/rachas_municipios_v{version}.csv", index=False)
		print("Guardado!")
		print("Guardando archivo de rachas máximas...")
		df_rachas_max_mun = pd.concat(lista_dfs_rachas_max).reset_index(drop=True)
		df_rachas_max_mun.to_csv(os.getcwd()+f"/data/rachas_maximas_municipios/rachas_maximas_municipios_v{version}.csv", index=False)
		sys.exit()

# Si no hace falta interrumpir, que se guarde todo.
df_rachas_mun = pd.concat(lista_dfs_rachas).reset_index(drop=True)
print("Guardando archivo de rachas...")
df_rachas_mun.to_csv(path2data_msm + file_name_msm_rachas, index=False)
print("Guardado!")
print("Guardando archivo de rachas máximas...")
df_rachas_max_mun = pd.concat(lista_dfs_rachas_max).reset_index(drop=True)
df_rachas_max_mun.to_csv(path2data_msm + file_name_msm_rachas_maximas, index=False)
print("Guardado!")