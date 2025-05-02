# -*- coding: utf-8 -*-
"""
Created on Wed Dec 28 16:36:55 2022

@author: datomi
"""

import pandas as pd

#pra transformar o arquivo dos pontos do perfil errado no certo

nome_do_arquivo = 'm3'

pontos = pd.read_csv(nome_do_arquivo+'.dat',delimiter=' ')

xa=pontos.iloc[:,0]
ya=pontos.iloc[:,1]

vx=list(map(lambda i: float(i),xa))
vy=list(map(lambda i: float(i),ya))

print(vx)

for i in range(len(vx)):   
    if vx[i] == 1:
        
        p_metade_vx = vx[:i+1]
        s_metade_vx = vx[i+1:]
        
        p_metade_vy = vy[:i+1]
        s_metade_vy = vy[i+1:]
        
        break

p_metade_vx = p_metade_vx[::-1]
p_metade_vy = p_metade_vy[::-1]

print(p_metade_vx)
print(s_metade_vx)

# s_metade_vx = s_metade_vx[::-1]
# s_metade_vy = s_metade_vy[::-1]

novo_vx = p_metade_vx + s_metade_vx
novo_vy = p_metade_vy + s_metade_vy



data_frame = {'X':novo_vx,'Y':novo_vy}

novos_pontos = pd.DataFrame(data_frame)

nome = 'novo_'+nome_do_arquivo+'.dat'

novos_pontos.to_csv(nome,index=False,sep=' ')


