# -*- coding: utf-8 -*-
"""
Created on Wed Oct 19 13:31:48 2022

@author: datomi
"""

#Analise de perfil completa a partir do Xfoil

import os
import subprocess
import pandas as pd
import sys
import fileinput
import math
import pylab as plt
import numpy as np
import time
import shutil
from Ajuste_de_curva_da_analise import varios_ajustes_de_curva

# Simetricos

#n0006        = NACA 0006
#n0009        = NACA 0009            
#n0012        = NACA 0012            
#n63015a      = NACA 63-015A        
#n0015        = NACA 0015  

# Perfis de asa

#s1223           = Selig 1223                 
#s1223RTL        = Selig 1223 RTL
#S 1210          = selig 1210 12%
#aj21s90         = AJ 2021-S90-10        perfil de 2021
#aj2150-rtl50    = AJ 2021-S50-RTL50
#aj2190-SRTL10   = AJ 2021-S90-RTL10     perfil de 2022
#CH 10           = CH 10                 esse perfil é suspeito
#NACA 4412       = NACA 4412
#NACA 4415       = NACA 4415
#fx63137         = FX 63-0137 13.7%
#fx73cl3152      = FX 73-CL3-152
#e423            = Eppler E423 high lift airfoil
#e420            = EPPLER 420

nome_do_perfil      = 'BELL540'         #nome do arquivo do perfil
alpha_inicial       = -2              #ângulo de ataque inicial
alpha_final         = 19              #ângulo de ataque final
alpha_passo         = 1             #passo do ângulo de ataque
Numero_de_intecoes  = 100            #quantas vezes ele vai tentar calcular antes de desistir

Rey_inicial = 5000
Rey_final   = 1300000
Rey_passo   = 20000


# se o perfil for simétrico, coloque o alpha inical e final igual
# para ter um valor bom de Clalpha coloque alpha final perto dos ângulos de stall
# alpha passo pode ser qualquer valor, mas caso dê erro, mude ele para mais ou para menos
# a lista de nomes dos perfis está acima































'CÓDIGO EM SI, NÃO ALTERAR'


com = time.time()

lista_de_reynolds = np.arange(Rey_inicial,Rey_final,Rey_passo)
lista_de_reynolds = list(lista_de_reynolds)

try:
    plt.style.use('extensys-gd')
except:
    pass


nome_do_arquivo = 'PontosPerfis/' + nome_do_perfil

def Dados_perfil(nome_do_perfil,
                 nome_do_arquivo,
                 alpha_inicial,
                 alpha_final,
                 alpha_passo,
                 Numero_de_Reynols,
                 Numero_de_intecoes):
    
    #roda o Xfoil para conseguir os pontos de alpha, CL e CD
    
    nome = str('OutputXfoil/Dados_do_perfil_'+nome_do_perfil+'_Re_'+Numero_de_Reynols+'.txt')
    
    if os.path.exists(nome):
        os.remove(nome)
    
    input_file = open("input_file.in", 'w')
    input_file.write("LOAD {0}.dat\n".format(nome_do_arquivo))
    input_file.write(nome_do_arquivo + '\n')
    input_file.write("PANE\n")
    input_file.write("OPER\n")
    input_file.write("Visc {0}\n".format(Numero_de_Reynols))
    input_file.write("PACC\n")
    input_file.write(nome+"\n\n")
    input_file.write("ITER {0}\n".format(Numero_de_intecoes))
    input_file.write("ASeq {0} {1} {2}\n".format(alpha_inicial, alpha_final,
                                                 alpha_passo))
    input_file.write("\n\n")
    input_file.write("quit\n")
    input_file.close()
    
    
    
    subprocess.call("xfoil.exe < input_file.in", shell=True)

    return(nome)


def leitura_do_arquivo(nome,
                       ):
    
    x = '    '
    x1= '   '
    x2= '  '
    x3= ' '
    y = ','
    y2= ',,'

    f = open(nome, "r+")

    for l in fileinput.input(files = nome):
        l = l.replace(x, y)
        l = l.replace(x1, y)
        l = l.replace(x2, y)
        l = l.replace(x3, y)
        l = l.replace(y2, y)
        sys.stdout.write(l)
        f.write(l)

    f.close()

    df = pd.read_csv(nome,header=10,delimiter=',')

    val = list(df['alpha'])
    vCl = list(df['CL'])
    vCd = list(df['CD'])
    vCm = list(df['CM'])

    val.pop(0)
    vCl.pop(0)
    vCd.pop(0)
    vCm.pop(0)

    for i in range(len(val)):
        if math.isnan(float(val[i])) == True:
            val = val[0:i]
            vCl = vCl[0:i]
            vCd = vCd[0:i]
            vCm = vCm[0:i]
            break
        val[i]=float(val[i])
        vCl[i]=float(vCl[i])
        vCd[i]=float(vCd[i])
        vCm[i]=float(vCm[i])

    return(val,vCl,vCd,vCm)

def analise_do_perfil(val,
                      vCl,
                      vCd,
                      vCm,
                      nome_do_perfil,
                      nome_do_arquivo,
                      Numero_de_Reynols):
    
    print('\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n')
    
    '______________________________________________________________________'
    
    'Calculo do Clalpha e Cl0'
    
    l=[]
    
    try:
        valusual = val[val.index(0):val.index(10)]
    except:
        valusual = val[val.index(0):val.index(9)]

    for i in range(len(valusual)-1):
        Clal = (vCl[i+1]-vCl[i])/(valusual[i+1]-valusual[i]) #guardando os valores de Clalpha de toda a curva
        if Clal > 0:
            l.append(Clal)
    m=[]

    for i in range(len(l)-1):
      if l[i+1] > 0:
        med = (l[i]+l[i+1])/2
        m.append(med)
    
    Clalpha = 0
    j=0
    alphas=[]
    Clalphas=[]
    
    try:
        e = 3
        
        for i in range(len(m)-2):
          if round(m[i],e) == round(m[i+1],e):  #quanto maior o valor no round, ele só vai pegar os segmentos realmente lineares
    
            Clalpha = m[i] + Clalpha
            Clalphas.append(m[i])
            j=j+1
            alphas.append(valusual[i])
        
        Cla1 = Clalpha/j

        Cla = Cla1

        
    except:
        
        e = 2
        
        for i in range(len(m)-2):
          if round(m[i],e) == round(m[i+1],e):  #quanto maior o valor no round, ele só vai pegar os segmentos realmente lineares
    
            Clalpha = m[i] + Clalpha
            Clalphas.append(m[i])
            j=j+1
            alphas.append(valusual[i])
            
        Cla1 = Clalpha/j

        Cla = Cla1
        
        pass
        
    try:
        Cl0 = vCl[val.index(0)]
    except:
        Cl0 = (vCl[val.index(-1)] + vCl[val.index(1)])/2
        pass
    
    '______________________________________________________________________'
    
    #análises
    
    #alpha 0
    
    al0 = -Cl0/Cla  #mais facil
    
    #Cl máximo
    
    Clmax = max(vCl)
    
    #angulo de stall
    
    sta=vCl.index(Clmax)
    
    als = val[sta]
    
    #Cl/Cd máximo
    
    vClCd=[]
    
    for i in range(len(val)):
        ClCd = vCl[i]/vCd[i]
        vClCd.append(ClCd)
    
    clcdmax=max(vClCd)
    
    #Cd em 0 graus
    
    try:
        Cd0 = vCd[val.index(0)]
    except:
        Cd0 = (vCd[val.index(-1)] + vCd[val.index(1)])/2
        pass

    

    return(Cla,Cl0,Clmax,al0,als,clcdmax,Cd0)
    
  

lista_Cla = []
lista_Cl0 = []
lista_Clmax = []
lista_al0 = []
lista_als = []
lista_clcdmax = []
lista_Cd0 = []
remover=[]

contador = 0
h_ant = 0

for h in lista_de_reynolds:
    
    Numero_de_Reynols = str(h)
    
    try:
        nome = Dados_perfil(nome_do_perfil,
                            nome_do_arquivo,
                            alpha_inicial,
                            alpha_final,
                            alpha_passo,
                            Numero_de_Reynols,
                            Numero_de_intecoes)
        
        
        val,vCl,vCd,vCm = leitura_do_arquivo(nome)
        
        Cla,Cl0,Clmax,al0,als,clcdmax,Cd0= analise_do_perfil(val,
                                                                  vCl,
                                                                  vCd,
                                                                  vCm,
                                                                  nome_do_perfil,
                                                                  nome_do_arquivo,
                                                                  Numero_de_Reynols)
        
        if math.isnan(Cla) == True:
            print('Sem Clalpha')
            pd.read_csv('dsfasgsdfgjdf') #pra causar erro
        if clcdmax > 210:
            print('Arrasto incorreto')
            pd.read_csv('dsfasgsdfgjdf') #pra causar erro
        if als < 7 :
            print('Estol irrealista')
            pd.read_csv('dsfasgsdfgjdf') #pra causar erro
            
            
        if contador > 0:
            if h - h_ant <= Rey_passo*2: #verificando se os valores estão em rey parecidos primeiro
                # print(lista_Cla[contador-1]/Cla)
                if lista_Cla[contador-1]/Cla > 1.07 or lista_Cla[contador-1]/Cla < 0.93:  #se a diferença ta alta é um erro
                    print('Desvio muito alto no Clapha')
                    pd.read_csv('dsfasgsdfgjdf') #pra causar erro

                
    
        print('Número de Reynolds =',h)
        
        lista_Cla.append(round(Cla,5))
        lista_Cl0.append(Cl0)
        lista_Clmax.append(Clmax)
        lista_al0.append(round(al0,3))
        lista_als.append(als)
        lista_clcdmax.append(round(clcdmax,2))
        lista_Cd0.append(Cd0)
        
        contador +=1
        h_ant = h
    
    except:
        remover.append(h)
        pass
    

if len(remover) > 0:
    for j in remover:
        lista_de_reynolds.remove(j)
        
lista_de_reynolds_graf = list(lista_de_reynolds)
'___________________________________________________________________________'

#limpando a pasta do xfoil:
    
folder = 'OutputXfoil'
for filename in os.listdir(folder):
    file_path = os.path.join(folder, filename)
    try:
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)
    except Exception as e:
        print('Failed to delete %s. Reason: %s' % (file_path, e))
        

'___________________________________________________________________________'


print("___________________________________________________")

#Ajustes de curva a serem feitos:
    
lista_linha = np.arange(lista_de_reynolds[0]/10000,lista_de_reynolds[-1]/10000,1)
    
for i in range(len(lista_de_reynolds)):
    lista_de_reynolds[i] = lista_de_reynolds[i]/10000



lista_n = np.arange(3,6,1)

#Clalpha

print("\nAjuste de curva do Clalpha  1/7")

for n in lista_n:

    lista_de_funcoes,lista_de_erros,lista_de_R2 = varios_ajustes_de_curva(lista_de_reynolds, lista_Cla, n)
    
    menor_erro_indx = lista_de_erros.index(min(lista_de_erros))
    maior_R2_indx   = lista_de_R2.index(max(lista_de_R2))
    
    func_Clal_ma_R2 = lista_de_funcoes[maior_R2_indx]
    er_Clal_ma_R2 = round(lista_de_erros[maior_R2_indx],2)
    R2_Clal_ma_R2 = round(lista_de_R2[maior_R2_indx],4)
    
    if round(lista_de_R2[maior_R2_indx],3) > 0.9 or round(lista_de_erros[menor_erro_indx],2) < 2:
        break

vetor2_Cla = []

if round(lista_de_erros[maior_R2_indx],2) > 10:
    
    func_Clal_ma_R2 = lista_de_funcoes[menor_erro_indx]

else:
    
    func_Clal_ma_R2 = lista_de_funcoes[maior_R2_indx]


for x in lista_linha:

    y_Clal2 = eval((func_Clal_ma_R2))

    vetor2_Cla.append(y_Clal2)
    
print('R² =',round(lista_de_R2[maior_R2_indx],2))
print('er =',round(lista_de_erros[menor_erro_indx],2))

'___________________________________________________________________________'

#Cl0

print("\nAjuste de curva do Cl0  2/7")

for n in lista_n:

    lista_de_funcoes,lista_de_erros,lista_de_R2 = varios_ajustes_de_curva(lista_de_reynolds, lista_Cl0, n)
    
    menor_erro_indx = lista_de_erros.index(min(lista_de_erros))
    maior_R2_indx   = lista_de_R2.index(max(lista_de_R2))
    
    func_Cl0_ma_R2 = lista_de_funcoes[maior_R2_indx]
    er_Cl0_ma_R2 = round(lista_de_erros[maior_R2_indx],2)
    R2_Cl0_ma_R2 = round(lista_de_R2[maior_R2_indx],4)
    
    if round(lista_de_R2[maior_R2_indx],3) > 0.98 or round(lista_de_erros[menor_erro_indx],2) < 0.5:
        break


vetor2_Cl0 = []

if round(lista_de_erros[maior_R2_indx],2) > 10:
    
    func_Cl0_ma_R2 = lista_de_funcoes[menor_erro_indx]

else:
    
    func_Cl0_ma_R2 = lista_de_funcoes[maior_R2_indx]


for x in lista_linha:

    y_Cl02 = eval((func_Cl0_ma_R2))

    vetor2_Cl0.append(y_Cl02)

print('R² =',round(lista_de_R2[maior_R2_indx],2))
print('er =',round(lista_de_erros[menor_erro_indx],2))

'___________________________________________________________________________'

#Clmax

print("\nAjuste de curva do Clmax  3/7")

for n in lista_n:

    lista_de_funcoes,lista_de_erros,lista_de_R2 = varios_ajustes_de_curva(lista_de_reynolds, lista_Clmax, n)
    
    menor_erro_indx = lista_de_erros.index(min(lista_de_erros))
    maior_R2_indx   = lista_de_R2.index(max(lista_de_R2))
    
    func_Clmax_ma_R2 = lista_de_funcoes[maior_R2_indx]
    er_Clmax_ma_R2 = round(lista_de_erros[maior_R2_indx],2)
    R2_Clmax_ma_R2 = round(lista_de_R2[maior_R2_indx],4)

    if round(lista_de_R2[maior_R2_indx],3) > 0.98 or round(lista_de_erros[menor_erro_indx],2) < 0.5:
        break

vetor2_Clm = []

if round(lista_de_erros[maior_R2_indx],2) > 10:
    
    func_Clmax_ma_R2 = lista_de_funcoes[menor_erro_indx]

else:
    
    func_Clmax_ma_R2 = lista_de_funcoes[maior_R2_indx]


for x in lista_linha:
 
    y_Clm2 = eval((func_Clmax_ma_R2))

    vetor2_Clm.append(y_Clm2)

print('R² =',round(lista_de_R2[maior_R2_indx],2))
print('er =',round(lista_de_erros[menor_erro_indx],2))

'___________________________________________________________________________'

#alpha 0

print("\nAjuste de curva do alpha 0  4/7")

for n in lista_n:

    lista_de_funcoes,lista_de_erros,lista_de_R2 = varios_ajustes_de_curva(lista_de_reynolds, lista_al0, n)
    
    menor_erro_indx = lista_de_erros.index(min(lista_de_erros))
    maior_R2_indx   = lista_de_R2.index(max(lista_de_R2))
    
    func_al0_ma_R2 = lista_de_funcoes[maior_R2_indx]
    er_al0_ma_R2 = round(lista_de_erros[maior_R2_indx],2)
    R2_al0_ma_R2 = round(lista_de_R2[maior_R2_indx],4)
    
    if round(lista_de_R2[maior_R2_indx],3) > 0.9 or round(lista_de_erros[menor_erro_indx],2) < 2:
        break

vetor2_al0 = []

if round(lista_de_erros[maior_R2_indx],2) > 10:
    
    func_al0_ma_R2 = lista_de_funcoes[menor_erro_indx]

else:
    
    func_al0_ma_R2 = lista_de_funcoes[maior_R2_indx]

for x in lista_linha:

    y_al02 = eval((func_al0_ma_R2))

    vetor2_al0.append(y_al02)

print('R² =',round(lista_de_R2[maior_R2_indx],2))
print('er =',round(lista_de_erros[menor_erro_indx],2))

'___________________________________________________________________________'

#angulo de estol

print("\nAjuste de curva do alpha s  5/7")

for n in lista_n:

    lista_de_funcoes,lista_de_erros,lista_de_R2 = varios_ajustes_de_curva(lista_de_reynolds, lista_als, n)
    
    menor_erro_indx = lista_de_erros.index(min(lista_de_erros))
    maior_R2_indx   = lista_de_R2.index(max(lista_de_R2))
    
    func_als_ma_R2 = lista_de_funcoes[maior_R2_indx]
    er_als_ma_R2 = round(lista_de_erros[maior_R2_indx],2)
    R2_als_ma_R2 = round(lista_de_R2[maior_R2_indx],4)
    
    if round(lista_de_R2[maior_R2_indx],3) > 0.98 or round(lista_de_erros[menor_erro_indx],2) < 0.5:
        break

vetor2_als = []

if round(lista_de_erros[maior_R2_indx],2) > 10:
    
    func_als_ma_R2 = lista_de_funcoes[menor_erro_indx]

else:
    
    func_als_ma_R2 = lista_de_funcoes[maior_R2_indx]


for x in lista_linha:

    y_als2 = eval((func_als_ma_R2))

    vetor2_als.append(y_als2)

print('R² =',round(lista_de_R2[maior_R2_indx],2))
print('er =',round(lista_de_erros[menor_erro_indx],2))

'___________________________________________________________________________'

#clcdmax

print("\nAjuste de curva do clcd max  6/7")

for n in lista_n:

    lista_de_funcoes,lista_de_erros,lista_de_R2 = varios_ajustes_de_curva(lista_de_reynolds, lista_clcdmax, n)
    
    menor_erro_indx = lista_de_erros.index(min(lista_de_erros))
    maior_R2_indx   = lista_de_R2.index(max(lista_de_R2))
    
    func_clcdmax_ma_R2 = lista_de_funcoes[maior_R2_indx]
    er_clcdmax_ma_R2 = round(lista_de_erros[maior_R2_indx],2)
    R2_clcdmax_ma_R2 = round(lista_de_R2[maior_R2_indx],4)
    
    if round(lista_de_R2[maior_R2_indx],3) > 0.98 or round(lista_de_erros[menor_erro_indx],2) < 0.5:
        break

vetor2_clcd = []

if round(lista_de_erros[maior_R2_indx],2) > 10:
    
    func_clcdmax_ma_R2 = lista_de_funcoes[menor_erro_indx]

else:
    
    func_clcdmax_ma_R2 = lista_de_funcoes[maior_R2_indx]


for x in lista_linha:

    y_clcd2 = eval((func_clcdmax_ma_R2))

    vetor2_clcd.append(y_clcd2)

print('R² =',round(lista_de_R2[maior_R2_indx],2))
print('er =',round(lista_de_erros[menor_erro_indx],2))

'___________________________________________________________________________'

#Cd0

print("\nAjuste de curva do Cd0  7/7")

for n in lista_n:

    lista_de_funcoes,lista_de_erros,lista_de_R2 = varios_ajustes_de_curva(lista_de_reynolds, lista_Cd0, n)
    
    menor_erro_indx = lista_de_erros.index(min(lista_de_erros))
    maior_R2_indx   = lista_de_R2.index(max(lista_de_R2))
    
    func_Cd0_ma_R2 = lista_de_funcoes[maior_R2_indx]
    er_Cd0_ma_R2 = round(lista_de_erros[maior_R2_indx],2)
    R2_Cd0_ma_R2 = round(lista_de_R2[maior_R2_indx],4)
    
    if round(lista_de_R2[maior_R2_indx],3) > 0.98 or round(lista_de_erros[menor_erro_indx],2) < 0.5:
        break

vetor2_Cd0 = []

if round(lista_de_erros[maior_R2_indx],2) > 10:
    
    func_Cd0_ma_R2 = lista_de_funcoes[menor_erro_indx]

else:
    
    func_Cd0_ma_R2 = lista_de_funcoes[maior_R2_indx]

for x in lista_linha:
  
    y_Cd02 = eval((func_Cd0_ma_R2))
    
    vetor2_Cd0.append(y_Cd02)

print('R² =',round(lista_de_R2[maior_R2_indx],2))
print('er =',round(lista_de_erros[menor_erro_indx],2))


'___________________________________________________________________________'


nome_da_pasta = 'Resultados de '+nome_do_perfil

local_graf = 'Resultados/'+nome_da_pasta+'/'

try:
    path = os.path.join(os.path.dirname(__file__)+'\Resultados',nome_da_pasta)
    os.mkdir(path)
except:
    pass


'___________________________________________________________________________'


#graficos

graf1=plt.figure(num=None, figsize=(10.5, 7.5), dpi=200, facecolor='w', edgecolor='k')
plt.scatter(lista_de_reynolds,lista_Cla,color='b',marker='*')
plt.plot(lista_linha,vetor2_Cla,color='g')
plt.xlabel ('Número de Reynolds 10e4')
plt.ylabel ('Cl\u03B1 (1/°)')    
plt.title (nome_do_perfil+' Clalpha em função do número de reynolds')

graf1.savefig(local_graf+nome_do_perfil+' Clalpha em função do numero de reynolds'+'.png')

graf2=plt.figure(num=None, figsize=(10.5, 7.5), dpi=200, facecolor='w', edgecolor='k')
plt.scatter(lista_de_reynolds,lista_Cl0,color='b',marker='*')
plt.plot(lista_linha,vetor2_Cl0,color='g')
plt.xlabel ('Número de Reynolds 10e4')
plt.ylabel ('Cl0')    
plt.title (nome_do_perfil+' Cl0 em função do número de reynolds')

graf2.savefig(local_graf+nome_do_perfil+' Cl0 em função do numero de reynolds'+'.png')

graf3=plt.figure(num=None, figsize=(10.5, 7.5), dpi=200, facecolor='w', edgecolor='k')
plt.scatter(lista_de_reynolds,lista_Clmax,color='b',marker='*')
plt.plot(lista_linha,vetor2_Clm,color='g')
plt.xlabel ('Número de Reynolds 10e4')
plt.ylabel ('Clmáx')    
plt.title (nome_do_perfil+' Clmáx em função do número de reynolds')

graf3.savefig(local_graf+nome_do_perfil+' Clmax em função do numero de reynolds'+'.png')

graf4=plt.figure(num=None, figsize=(10.5, 7.5), dpi=200, facecolor='w', edgecolor='k')
plt.scatter(lista_de_reynolds,lista_al0,color='b',marker='*')
plt.plot(lista_linha,vetor2_al0,color='g')
plt.xlabel ('Número de Reynolds 10e4')
plt.ylabel ('\u03B10 (°)')    
plt.title (nome_do_perfil+' \u03B10 em função do número de reynolds')

graf4.savefig(local_graf+nome_do_perfil+' alpha0 em função do numero de reynolds'+'.png')

graf5=plt.figure(num=None, figsize=(10.5, 7.5), dpi=200, facecolor='w', edgecolor='k')
plt.scatter(lista_de_reynolds,lista_als,color='b',marker='*')
plt.plot(lista_linha,vetor2_als,color='g')
plt.xlabel ('Número de Reynolds 10e4')
plt.ylabel ('\u03B1s (°)')    
plt.title (nome_do_perfil+' \u03B1s em função do número de reynolds')

graf5.savefig(local_graf+nome_do_perfil+' angulo de estol em função do numero de reynolds'+'.png')

graf6=plt.figure(num=None, figsize=(10.5, 7.5), dpi=200, facecolor='w', edgecolor='k')
plt.scatter(lista_de_reynolds,lista_clcdmax,color='b',marker='*')
plt.plot(lista_linha,vetor2_clcd,color='g')
plt.xlabel ('Número de Reynolds 10e4')
plt.ylabel ('Cl/Cd máximo')    
plt.title (nome_do_perfil+' Cl/Cd máximo em função do número de reynolds')

graf6.savefig(local_graf+nome_do_perfil+' Cl_Cdmax em função do numero de reynolds'+'.png')

graf7=plt.figure(num=None, figsize=(10.5, 7.5), dpi=200, facecolor='w', edgecolor='k')
plt.scatter(lista_de_reynolds,lista_Cd0,color='b',marker='*')
plt.plot(lista_linha,vetor2_Cd0,color='g')
plt.xlabel ('Número de Reynolds 10e4')
plt.ylabel ('Cd0')    
plt.title (nome_do_perfil+' Cd0 em função do número de reynolds')

graf7.savefig(local_graf+nome_do_perfil+' Cd0 em função do numero de reynolds'+'.png')



'___________________________________________________________________________'


tamanho_das_listas = len(lista_de_reynolds)

#arquivo de texto

local_das_listas='Resultados/'+nome_da_pasta+'/Listas dos graf'+'.txt'

f = open(local_das_listas,'w')
f.write('________________________________________________________________________________________________________________________________________________________________________________')

f.write('\n\nPerfil '+nome_do_perfil)
f.write('\n\nRey = [')

for i in range(tamanho_das_listas):
    f.write(' , '+str(lista_de_reynolds[i]))
    
f.write(' ]\n')

f.write('\n\nCla = [')

for i in range(tamanho_das_listas):
    f.write(' , '+str(lista_Cla[i]))
    
f.write(' ]\n')

f.write('\n\nCl0 = [')

for i in range(tamanho_das_listas):
    f.write(' , '+str(lista_Cl0[i]))
    
f.write(' ]\n')

f.write('\n\nClmax = [')

for i in range(tamanho_das_listas):
    f.write(' , '+str(lista_Clmax[i]))
    
f.write(' ]\n')

f.write('\n\nal0 = [')

for i in range(tamanho_das_listas):
    f.write(' , '+str(lista_al0[i]))
    
f.write(' ]\n')

f.write('\n\nals = [')

for i in range(tamanho_das_listas):
    f.write(' , '+str(lista_als[i]))
    
f.write(' ]\n')

f.write('\n\nclcdmax = [')

for i in range(tamanho_das_listas):
    f.write(' , '+str(lista_clcdmax[i]))
    
f.write(' ]\n')

f.write('\n\nCd0 = [')

for i in range(tamanho_das_listas):
    f.write(' , '+str(lista_Cd0[i]))
    
f.write(' ]\n')

f.write('________________________________________________________________________________________________________________________________________________________________________________')
f.close()




   


local='Resultados/'+nome_da_pasta+'/Dados dos graficos de '+nome_do_perfil+'.txt'

f = open(local,'w')
f.write('____________________________________________________________________________________________________________________________')

f.write('\n\nPerfil '+nome_do_perfil)

f.write('\n\nals      = '+str(func_als_ma_R2))

f.write('\n\nal0      = '+str(func_al0_ma_R2))

f.write('\n\nCl0      = '+str(func_Cl0_ma_R2))

f.write('\n\nClmax    = '+str(func_Clmax_ma_R2))

f.write('\n\nCla      = '+str(func_Clal_ma_R2))

f.write('\n\nCd0      = '+str(func_Cd0_ma_R2))

f.write('\n\nclcdmax  = '+str(func_clcdmax_ma_R2))

f.write('\n\n____________________________________________________________________________________________________________________________')
f.close()


fim = time.time()

print('Análise válida somente no intervalor de Número de Reynolds entre',(lista_de_reynolds[0]*10000),'e',(lista_de_reynolds[-1]*10000))
print('\nTempo de processamento: %s segundos'%round(fim-com,1))
print('Terminado! Verifique a pasta de resultados')
