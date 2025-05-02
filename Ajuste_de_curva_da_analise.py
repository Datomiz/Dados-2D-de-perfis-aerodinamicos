# -*- coding: utf-8 -*-
"""
Created on Sat Oct  1 19:25:42 2022

@author: datomi
"""

#**************************Ajuste de Curva**************************

# código de ajuste de curva q testa todas as possibilidades

import numpy as np
import sympy as sy
import pylab as pyl
import math

pyl.style.use('extensys-gd')




def cal_erro(lista1,gx,vx,vy):
    erropor = []
    
    ytra = np.mean(vy)
    
    SQresr = 0
    SQexpr = 0
    
    for i in lista1:
        
        x = vx[i]
        
        y = eval(gx)
                
        yr = vy[i]
                
        if x == 0 or yr == 0:
            pr = 0
        else:
            pr = (abs(yr-y))*100/(yr)
            
        erropor.append(pr)
        
        SQresr += (yr - y) ** 2
        
        SQexpr += (y - ytra) ** 2

    R2 = SQexpr/(SQexpr+SQresr)    

    Erropor = max(erropor)
    
    return(Erropor,R2)
    

def varios_ajustes_de_curva(vx:list,
                            vy:list,
                            n:int):
    

     

    raix = 'x**(1/2)'
    ra3x = 'x**(1/3)'
                      
    sobx = 'x**(-1)'
    # sox2 = 'x**(-2)'
    # sox3 = 'x**(-3)'
    # sox4 = 'x**(-4)'

    dosx = '2**x'
    trex = '3**x'
    xmx1 = 'x*(x-1)'

    # senx = 'np.sin(x)'
    # cosx = 'np.cos(x)'
    # tgx  = 'np.tan(x)'
    # atgx = 'np.arctan(x)*180/np.pi'

    # xsen = 'x*np.sin(x)'
    # xcos = 'x*np.cos(x)'

    sehx = 'np.sinh(x)'
    cohx = 'np.cosh(x)'
    # tghx = 'np.tanh(x)'

    # expx = 'np.exp(x)'
    # exmx = 'np.exp(-x)'
    # xemx = 'x*np.exp(-x)'
    # norm = 'np.exp(-(x**2))'

    # lnnx = 'np.log(x)'
    # logx = 'np.log10(x)'
    pix  = 'np.pi**x'



    p   = len(vx)
    ini = min(vx)
    fin = max(vx)
            
    lista_decisao = [
                      # senx,
                      # cosx,
                      # tgx,
                      sehx,
                      cohx,
                      # tghx,
                      # expx,
                      # exmx,
                      # xemx,
                      raix,
                      ra3x,
                      # lnnx,
                      # logx,
                      # sobx,
                      # sox2,
                      # sox3,
                      # sox4,
                      dosx,
                      trex,
                      pix,
                      # atgx,
                      # norm,
                      xmx1,
                      # xsen,
                      # xcos
                      ]





    lista_escolha1 = [0] * len(lista_decisao)


    def check_de_valores(lista_escolha1,lista_decisao):
        
        if any(a > 600 for a in vx): #limitação do math.exp(x) que não pode ser maior que +ou- 700
                                     #limitação do math.pi**x que não pode ser maior que +ou- 600

            
            lista_decisao.remove(sehx)
            lista_escolha1.remove(0)
            
            lista_decisao.remove(cohx)
            lista_escolha1.remove(0)
            
            
            lista_decisao.remove(dosx)
            lista_escolha1.remove(0)
            
            lista_decisao.remove(trex)
            lista_escolha1.remove(0)
            

        
        return(lista_escolha1,lista_decisao)

    lista_escolha1,lista_decisao = check_de_valores(lista_escolha1,lista_decisao)

   # print('\nAjuste de curva usando o Método dos Mínimos Quadrados')
    #print('\n Carregando...')

    def ajuste(n:int,
               lista_escolha1:list,
               lista_decisao:list,
               vx:list,
               vy:list,
               p:int
               ):
        
        gz=[]
        gx = ""
        lista1=np.arange(0,p,1)

        A = np.zeros((n,n))
        B = np.zeros((1,n))[0]
        
        #criação do sistema de equações para econtrar o resultado do ajuste de curva
        for i in lista1:
            
            gs=[]
            x = vx[i]
            
            #enchendo a matriz de x**j
            for j in range(n):
               gs.append(x**j)
               
            #trocando os x**j por funções escolhidas
            for j in range(len(lista_decisao)):

                v_a_trc = lista_escolha1[j]
                
                if v_a_trc != 0:
                    
                    index_da_troca = lista_escolha1.index(v_a_trc)

                    gs[v_a_trc] = eval(str(lista_decisao[index_da_troca]))
            
            #fazendo as outras partes da matriz
            for k in range(len(A)):

                for j in range(int(len(A))):

                    A[j,k] = A[j,k]+(gs[j]*gs[k])
            
            #fazendo a outra matriz, de reusltados
            for j in range(len(A)):
          
                B[j] = B[j] + (vy[i]*gs[j])

        
        #resultado do sistema de quações
        X=np.linalg.inv(A).dot(B)
        
        #enchendo a equação com x**j primeiramente
        for j in range(n):

            gz.append("x"+"**"+str(j))
        
        #pegando as funções que foram usadas nessa equação e trocando pelos x**j
        for j in range(len(lista_decisao)):
            v_a_trc = lista_escolha1[j]
            if v_a_trc != 0:
                index_da_troca = lista_escolha1.index(v_a_trc)
                gz[v_a_trc] = lista_decisao[index_da_troca]


        #organizando a equação
        for j in range(n):
            
            if X.item(j) < 0:
                
                mais = " "
            
            else:
                
                mais = " + "
            
            if j == 0:
                
                gx = str(gx) +mais+ str(X.item(j))
                
            else:
                gx = str(gx) +mais+ (str(X.item(j))+"*"+str(gz[j]))
            
        # print('Função encontrada:',gx)
        gx=str(gx)
        
        #calculo do erro
        er,R2 = cal_erro(lista1,gx,vx,vy)
        return(gx,er,R2)


        
    #aqui começa a testar tudo

    lista_de_erros = []
    lista_de_R2 = []
    lista_de_funcoes = []
        
    func,erro,R2 = ajuste(n,lista_escolha1,lista_decisao,vx,vy,p)

    lista_de_funcoes.append(func)
    lista_de_erros.append(erro)
    lista_de_R2.append(R2)



    listas_escolhas = []

    for i in np.arange(1,n,1):

        for m in range(len(lista_escolha1)):
            
            lista_escolha1[m] = i
            
            # if lista_escolha1 in listas_escolhas:
            #     lista_escolha1[m] = 0
            #     continue
                    
            try:
                # print()
                # print(lista_escolha1)
                
                listas_escolhas.append(list(lista_escolha1))
                
                func,erro,R2 = ajuste(n,lista_escolha1,lista_decisao,vx,vy,p)
                
                lista_de_funcoes.append(func)
                lista_de_erros.append(erro)
                lista_de_R2.append(R2)
            
            except:
                lista_escolha1[m] = 0
                pass
            
            for j in range(len(lista_escolha1)):
                
                if i+1 < n:
                    lista_escolha1[j] = i+1
                if i+1 == n:
                    lista_escolha1[j] = i-1

                
                if lista_escolha1 in listas_escolhas:
                    lista_escolha1[j] = 0
                    lista_escolha1[m] = 0
                    continue
                
                # if n in lista_escolha1:
                #     lista_escolha1[j] = 0
                #     lista_escolha1[m] = 0
                #     continue
                
                try:
                    # print(lista_escolha1)
                    listas_escolhas.append(list(lista_escolha1))

                    func,erro,R2 = ajuste(n,lista_escolha1,lista_decisao,vx,vy,p)
                    
                    lista_de_funcoes.append(func)
                    lista_de_erros.append(erro)
                    lista_de_R2.append(R2)
                    
                except:
                    pass
                
                lista_escolha1[j] = 0
                

            lista_escolha1[m] = 0

            
    return(lista_de_funcoes,lista_de_erros,lista_de_R2)

    
a = math.pi

