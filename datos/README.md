# Datos: Documentación

En este apartado se explica el proceso de la extracción y transformación de de los datos usados para el proyecto.

> Si encuentras algún error/_bug_ o quisieras recomendar alguna mejora, puedes levantar un _issue_ o enviarme un correo directamente

## TerraClimate a través de Google Earth Engine

[**TerraClimate**](https://developers.google.com/earth-engine/datasets/catalog/IDAHO_EPSCOR_TERRACLIMATE) es un conjunto de imágenes satelitales cuyos pixeles dan información de variables climatológicas mensuales, tales como temperatura mínima y máxima, precipitación, Índice de Intensidad de Sequía de Palmer (PDSI, por sus siglas en inglés), humedad de suelo, entre otras. Estas variables estan separadas por bandas que cubren el mundo.

Algunos de los datos relevantes son los siguientes:

- El proveedor de este conjunto de datos es el equipo del Laboratorio de Climatología ["Climatology Lab"](https://www.climatologylab.org/terraclimate.html) de la Universidad de California, Merced (EE.UU.).
- Cuenta con datos mensuales de las variables a partir de 1958 hasta el año anterior inmediato al presente y es actualizado anualmente. 
- Tiene una resolución espacial de aproximadamente 4.4 km

Para extraer los datos de TerraClimate hace falta tener una cuenta/licencia de [Google Earth Engine](https://earthengine.google.com/) así como aprender a usar la API en alguno de sus lenguajes de programación. A continuación se presentan los _links_ para cada uno de esos pasos:

- [Registro y petición de una licencia gratuita de Earth Engine](https://earthengine.google.com/signup/)
- [Documentación, tutoriales y guías para la API de JavaScript y Python](https://developers.google.com/earth-engine/guides)

Se usó principalmente Python para la transformación y extracción de los datos. Algunos recursos que facilitaron esta tarea fue la librería de [**`geemap`**](https://geemap.org/)

Las variabes climatológicas que se usaron para este reportaje fueron:

- Temperatura Máxima
- Temperatura Mínima
- Precipitación
- Índice de Severidad de Sequía de Palmer (PDSI, por su nombre en inglés _Palmer's Drought Severity Index_): Es uno de los indicadores de sequía más populares el cual no tiene unidades (es simplemente el número). Toma en cuenta otras variables climatológicas tales como temperatua, precipitación y un modelo de balance físico del agua. Sus valores son negativos y positivos:
  - **Valores negativos indican condiciones de sequía**, siendo -4 un valor para condiciones de sequía extrema.
  - **Valores positivos indican condiciones de humedad**, siendo 4 un valor para condiciones humedad extrema.
  - **Valores cercanos a cero indican condiciones normales**.
- Déficit Climático del Agua (CWD, por su nombre en inglés _Climate Water Deficit_): Puede ser pensado como la cantidad de agua que pudo haber sido evaporada o transpirada (usada) de haber estado disponible en la tierra dada a la temperatura. Este cálculo es un estimado del estrés de sequía en los suelos y plantas. Entre mayor sea el CWD, mayor es el estrés de sequía.

### Cálculo de anomalías y _Z-scores_

De acuerdo con la Administración Nacional Oceánica y Atmosférica (NOAA, por sus siglas en inglés), una anomalía es **la desviación de una unidad con respecto a un promedio histórico (de normalmente 30 años).**

Las variables a las que se les calculará las anomalías son a las de **temperatura máxima y mínima** y a **precipitación**. Y para cada una el cálculo de la anomalía varía.

La **anomalía de temperatura máxima y mínima** es la cantidad de grados Celsius (°C) que se encuentra una determinada región en un tiempo determinado con respecto al promedio histórico. Valores positivo significa que hay mayor temperatura y valores negativos que hay menor temperatura.

$$\text{anomalia}_{T} = x_{i_{T}} - \mu_{\text{hist}}$$

Donde:

- $x_{i_{T}}$ es la temperatura de una región en un determinado mes 
- $\mu_{\text{hist}}$ es la temperatura promedio historica de esa región en ese determinado mes.

Mientras que, la **anomalía de precipitación** mide la diferencia relativa de la precipitación, es decir, calcula la proporción de precipitación de un determinado mes con respecto al promedio histórico (de ese mes): valores positivos significa que ha llovido más que lo esperado/promedio y valores negativos, lo contrario.

$$\text{anomalia}_{\text{pr}} = \frac{x_{i_{\text{pr}}} - \mu_{\text{hist}_{\text{pr}}}}{\mu_{\text{hist}_{\text{pr}}}} = \frac{x_{i_{\text{pr}}}}{\mu_{\text{hist}_{\text{pr}}}} - 1$$

- $x_{i_{\text{pr}}}$ es la precipitación de una región en un determinado mes 
- $\mu_{\text{hist}_{\text{pr}}}$ es la precipitación promedio historica de esa región en ese determinado mes.

---

El **Z-score** es una medida estadística sin unidades que indica a cuántas desviaciones estándar (σ) están los datos. Esta estadística es útil al momento de enfocarnos en el comportamiento de los datos sin la preocupación de saber si algún valor es lo suficientemente significativo con respecto al histórico.

Se toma la distancia en desviaciones estándar ya que, en una distribución Gaussiana, casi el 70% de los datos se encuentran a una desivación estándar (por la izquieda o derecha) del promedio, por lo que valores valores que se encuentren a mayor distancia son valores _anómalos_.

La ecuación es la siguiente:

$$\text{Z-score} = \frac{x_{i} - \mu_{\text{hist}}}{\sigma_{\text{hist}}}$$

Donde: 

- $x_{i}$ es el valor de la variable en una región de un determinado tiempo. 
- $\mu_{\text{hist}}$ es el valor promedio histórico de la variable en esa región en ese determinado tiempo.
- $\sigma_{\text{hist}}$ es la desviación estándar historica de la variable en esa región en ese determinado tiempo.

Usar el **Z-score** ayuda a ver el comportamiento más allá de los valores numéricos.

Las variables a las que se les obtendrá el valor del **Z-score** son:

- Temperatura máxima y mínima
- Déficit Climático del Agua

### Transformación de imágenes a elementos vectoriales

Después de la selección de las bandas y el cálculo de las variables para cada mes de todos los años, se extraen los datos como [datos vectoriales](https://docs.qgis.org/3.28/es/docs/gentle_gis_introduction/vector_data.html). 

### Exportar elementos vectoriales a tabulares (CSV)

Al tener un conjunto de datos que son vectoriales, se puede pensar como datos tabulados que tienen columnas de propiedades y una columna específica de geometría

> La tabla es ilustrativa, no muestra la realidad de los datos 

| nombre_entidad_municipio | clave_geografica | anomalia_temp_max | año |geometria |
|---|---|---|---|---|
|Yucatán|31|1.4| 2020 |`Rectangle([(0,0),(2,0),(2,2),(2,0),(0,0)])`|

Así que se extrae la información de las columnas de las propiedades, mas no la de geometría porque el tiempo que toma para extraer ese dato consume mucho tiempo y puede ocasionar alguna falla o error.

El formato en el que se exporta es un CSV, y dependiendo si se extraen los valores de manera mensual o anual, varía su proceso de transformación a un formato llamado _long_ o largo, este tipo de formato de datos facilitará el análisis y la visualización de los datos.

## Monitor de Sequía de México (MSM)

Uno de los documentos que proporciona de manera abierta el MSM es un archivo Exvel (XLSX) donde cada fila es un municipio y las columnas son las fechas del registro (mensual previo al 2014). El tipo de sequía registrado se encuentra debajo de cada columna de fecha.

Para realizar los cálculos y filtrados necesarios para los objetivos de la investigación se tuvieron que cambiar la forma de los datos, donde cada fila sea un registro (fecha) con el tipo de sequía registrado.

|Estado|Municipio|Fecha de registro|Tipo de sequía|
|---|---|---|---|
|Yucatán|Progreso|2020-05-15|D1|
|Yucatán|Chelem|2020-05-15|D1|
|Oaxaca|Santiago Pinotepa Nacional|2020-05-15|D2|
|Quintana Roo|Cozumel|2020-05-15|D0|

Con esta forma se calculan las rachas (el tiempo en meses, de la presencia de una categoría de sequía en un determiando municipio).

## Polígonos de México

Para la creación de mapas, así como para crear los límites de la extracción de datos de TerraClimate en Google Earth Engine, se tuvieron que usar datos vectoriales. Este tipo de dato almacena información de puntos que forman geometrías que delimitan las divisiones de las naciones, estados y municipios de un país.

Para el caso de México, se descargaron del Marco Geoestadístico 2022 del INEGI a través de su portal.

Los datos _crudos_ de la división de los estados y de los municipios se subieron como un proyecto en la nube de Google Earth Engine para que estén a disposición pública. 

Los datos que se usan para la creación de los mapas, pasaron por un procesamiento y filtrado extra que consistió en eliminar islas alejadas de las costas de la nación así como la simplificación de las geometrías. Esto se hizo para que el archivo no sea pesado y sea facil de exportar y y de cargar en un URL.
