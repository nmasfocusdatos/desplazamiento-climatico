# - - - - - - 
# 02
# - - - - - - 
#
# Procesmiento de datos para el cálculo de rachas
# 
# 
# Autor: Miguel Isaac Arroyo Velázquez


library(tidyverse)

path2data_msm <- paste0(getwd(), "/datos/msm/")
file_name_msm_long <- "MunicipiosSequia_long.csv"
file_name_msm_para_rachas <- "MunipiosSequia_long_para_rachas.csv"


read_csv(paste0(path2data_msm, file_name_msm_long)) %>%
  janitor::clean_names() %>%
  replace_na(list(sequia="Sin sequia")) %>%
  mutate(
    sequia = ordered(
        sequia,
        levels = c("Sin sequia", "D0", "D1", "D2", "D3", "D4")
        )
  ) %>%
  filter(!(year(full_date) == 2003 & month(full_date) == 8)) %>%
  filter(!(year(full_date) == 2004 & month(full_date) == 2)) %>%
  select(full_date, cve_concatenada, nombre_mun, sequia) %>%
  write_csv(paste0(path2data_msm, file_name_msm_para_rachas))
