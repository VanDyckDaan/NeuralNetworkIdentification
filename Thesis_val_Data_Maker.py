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
import time
import pickle








def progress(count, total):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round((100.0 * count / float(total)),3)
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




j=0
#assign working directory to variable
path=os.getcwd()
#setting path for data folder
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
    if(list_name[i] == "F:\Master\School\ThesistestData\Benchmark"):
        
        data_path = list_name[i]
    else:
        print(list_name[i])
        continue
        
    # extracting file names without extensions
    file_names=[".".join(f.split(".")[:-1]) for f in listdir(data_path) if isfile (join(data_path,f))] 
    # extracting file names with extensions
    full_file_names=[f for f in listdir(data_path) if isfile (join(data_path,f))]   

    Data = pd.DataFrame({"RealTime":[],
                             "LifeTime":[],
                             "Energie":[],
                             "Counts":[],
                             "Peak":[],
                             "PeakCounts":[],
                             "Afstand":[],
                             "Locatie":[],
                             "cps":[],
                             "Activiteit":[],
                             "Hoek":[],
                             "Bron":[]    })
 
    
    for s in full_file_names:
        j=j+1
        txt = pd.read_csv(data_path+'\\'+ s, delimiter = "\t")
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
        
        
        for i in range(0,4096):
          EKal.append(c0+c1*i)
          c = int(txt.iat[i+10,0])
          counts.append(c)
            
        counts = np.array(counts)
        EKal = np.array(EKal)
        
        Channel = round((661-c0)/c1)
        peak = np.zeros(4096)
        
        peak_counts = []

        #Bepaling welke bron er aanwezig is
        if("Achtergrond" or "background" or "Background" in str(s)):
            if ("Achtergrond" in str(s)):
                bron = "Background"
            activiteit = 0
        if("Cs137" in str(s)):
            bron = 'Cs137'
            L = np.log(2)/30.01
            activiteit = 9.25*10**3*np.exp(-L*21.666666)
            for i in range (Channel - 100, Channel + 100):
                peak[i] = 1
                peak_counts.append(counts[i])
        
        
        #bepaling of bron onder een gemeten hoek lag
        if ('°' in str(s)):
            hoek = float(between(str(s),'g_','°'))
        else:
            hoek = float(0)
        if('cm' and 'Hoogteverandering' in str(s)):
            afstand = int(between(str(s),"Hoogteverandering_", "cm"))
        if('cm' and 'Hoekverandering' in str(s)):
            afstand = int(between(str(s),"°_", "cm"))
        if('cm' and '2021' in str(s)):
            afstand = int(between(str(s),"2021_","cm"))
        
        
        cps = round(sum(counts) ) 
        print(cps)
        if ('Tijd' in str(s)):
             afstand = 0
        if("HOB" in str(s)):
            locatie = "HOB"
        elif("ENE" in str(s)):
            locatie = "ENE"
        
        if (j <= 2090):
            sys.stdout.write('\r')
            progress(j, 2090)
            time.sleep(0.1)
        
        
            
        # data toevoegen aan dataframe 
        Data = Data.append({"RealTime":realtime,
                             "LifeTime":lifetime, 
                             "Energie":EKal,
                             "Counts":counts,
                             "Peak":peak,
                             "PeakCounts":sum(peak_counts),
                             "Afstand": afstand,
                             "Locatie":locatie,
                             "counts":cps,
                             "Activiteit":activiteit,
                             "Hoek":hoek,
                             "Bron":bron},
                           ignore_index = True)
    
    # data toevoegen aan hdf5 file om verder te verwerken in ML-algoritme
    HDF = HDF.append(Data,ignore_index = True)
   
picklefile = open('Validation.pkl','wb')
DATA = HDF
pickle.dump(HDF,picklefile)
picklefile.close()