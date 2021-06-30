# -*- coding: utf-8 -*-

"""
Created on Mon Sep  7 16:15:18 2020

@author: daanv


"""
import pandas as pd

import os
from os import listdir
from os.path import isfile,join
import numpy as np
import sys
import pickle
import matplotlib.pyplot as plt





#progressbar om te zien hoe lang het nog zal duren
def progress(count, total):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = (100.0 * count / float(total))
    percents = round(percents,2)
    bar = '#' * filled_len + ' ' * (bar_len - filled_len)
    sys.stdout.write('\r')
    sys.stdout.write('[%s] %s%s' % (bar, percents, '%'))
    sys.stdout.write('\r')
    sys.stdout.flush()

#os.remove('data.h5')

def before(value, a):
    # Find first part and return slice before it.
    pos_a = value.find(a)
    if pos_a == -1: return ""
    return value[0:pos_a]
#bron:https://www.dotnetperls.com/between-before-after-python
    
def after(value, a):
    # Find and validate first part.
    pos_a = value.rfind(a)
    if pos_a == -1: return ""
    # Returns chars after the found string.
    adjusted_pos_a = pos_a + len(a)
    if adjusted_pos_a >= len(value): return ""
    return value[adjusted_pos_a:]

#bron:https://www.dotnetperls.com/between-before-after-python
    
def between(value, a, b):
    # Find and validate before-part.
    pos_a = value.find(a)
    if pos_a == -1: return ""
    # Find and validate after part.
    pos_b = value.rfind(b)
    if pos_b == -1: return ""
    # Return middle part.
    adjusted_pos_a = pos_a + len(a)
    if adjusted_pos_a >= pos_b: return ""
    return value[adjusted_pos_a:pos_b]



def Write():
    j=0
    #huidige directory toevoegen
    path=os.getcwd()
    #path zetten voor datafolder
    list_name = []

    
    HDF = pd.DataFrame({"RealTime":[],
                             "LifeTime":[], 
                             "Energie":[],
                             "Counts":[],
                             "Afstand":[],
                             "Activiteit":[],
                             "Hoek":[],
                             "Bron":[]    })
    
    
    for root, directories, files in os.walk(path, topdown=False):
        for name in directories:
            list_name.append(os.path.join(root,name))
             
               
    
        for i in range(0, len(list_name)):
            
            
            data_path = list_name[i]
            # bestandsnamen zonder extensies binnenhalen
            file_names=[".".join(f.split(".")[:-1]) for f in listdir(data_path) if isfile (join(data_path,f))] 
            # bestandsnamen met extensies binnenhalen
            full_file_names=[f for f in listdir(data_path) if isfile (join(data_path,f))]   
        
         
            Data = pd.DataFrame({"RealTime":[],
                             "LifeTime":[], 
                             "Energie":[],
                             "Counts":[],
                             "Peak":[],
                             "Afstand":[],
                             "Activiteit":[],
                             "Hoek":[],
                             "Bron":[]    })
            
            for s in full_file_names:
                j=j+1
                txt = pd.read_csv(data_path+'\\'+s)
                #alles uit .spe file halen
                #live time uit de meting
                lifetime = float(before(txt.iat[7,0]," "))
                #real time uit de meting
                realtime = float(after(txt.iat[7,0]," "))
                # gebruiken van de gemeten waardes
                counts = []
                #Energiekalibratie van het meettoestel
                EKal = []
                c0 = float(before(txt.iat[4107,0]," "))
                c1 = float(after(txt.iat[4107,0]," "))
                
                
                for k in range(0,4096):
                   EKal.append(c0+c1*k)
                   c = int(txt.iat[k+10,0])
                   counts.append(c)
                counts = np.array(counts)
                Ekal = np.array(counts)
                Channel = round((661-c0)/c1)
                peak = np.zeros(4096)
                bron = str(before(str(s),"_"))


        
                #Bepaling welke bron er aanwezig is
                if(bron == str('background')):
                    bron = "Background"
                    activiteit = 0
                if(str('Cs137') ==bron):
                    L = np.log(2)/30.01
                    activiteit = 9.25*10**3*np.exp(-L*21.666666)
                    for i in range (Channel - 100, Channel + 100):
                        peak[i] = 1
                #print(bron)
                afstand = 0
                #bepaling of bron onder een gemeten hoek lag
                if ('°' in str(s)):
                    hoek = float(between('s','°','_'))
                else:
                    hoek = float(0)
                if('cm' in str(s)):
                    afstand= int(between(str(s),"_", "cm"))
                else:
                    afstand = 0
                
                if (j < 6500):
                    sys.stdout.write('\r')
                    progress(j, 6500)
                    
                if( i%650 ==0):
                    plt.figure(i)
                    plt.plot(EKal, counts)
                    plt.plot(EKal, peak)
                   
                Data = Data.append({"RealTime":realtime,
                             "LifeTime":lifetime, 
                             "Energie":EKal,
                             "Counts":counts,
                             "Peak":peak,
                             "Afstand":afstand,
                             "Activiteit":activiteit,
                             "Hoek":hoek,
                             "Bron":bron   }, ignore_index = True)
            # data toevoegen aan hdf5 file om verder te verwerken in ML-algoritme
            HDF = HDF.append(Data,ignore_index = True)
            
    return(HDF)
HDF = Write()
print(HDF)
picklefile = open('data.pkl','wb')

pickle.dump(HDF,picklefile)
picklefile.close()
