# -*- coding: utf-8 -*-
"""
Spyder Editor

Author: CCCM

"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import flopy
from flopy import *


def main():
    plt.close("all")
    
    #Rutas 
    ruta_trabajo = r'E:\WEAP\Weap Areas\Tutorial_ET_v1\MODFLOW_2005_ET\modelo_original'
    ruta_lst = r'.\MODFLOW_2005_ET.lst'
    os.chdir(ruta_trabajo)   
    
    mf_list =  flopy.utils.MfListBudget(ruta_lst)
    incremental, cumulative = mf_list.get_budget()
    
    #Leer el balance del primer timestep y primer stress period
    data = mf_list.get_data(kstpkper=(0,0))
    plt.bar(data['index'], data['value'])
    plt.xticks(data['index'], data['name'], rotation=45, size=6)
    plt.show()
    plt.ylabel('Balance volumétrico ($m^3$)')
    plt.tight_layout()
    plt.grid()
    plt.savefig('balance2.png',dpi=600)
    
    #Leer time steps y stress periods
    kstpkper = mf_list.get_kstpkper() 
    print(kstpkper)
    
    #Leer el tiempo de ejecución del modelo
    tiempo = mf_list.get_model_runtime(units='hours')
    print(tiempo)
    
    # Leer los tiempos del LST file
    times = mf_list.get_times()
    print(times)
    
if __name__ == '__main__': main()
