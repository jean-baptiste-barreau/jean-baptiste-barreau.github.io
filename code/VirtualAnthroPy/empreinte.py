import numpy as np
from numpy import linalg as LA
import math
import datetime

from obj_utils import *
from repere import Repere

import matplotlib.pyplot as plt

class Empreinte:
    #https://www.python-course.eu/python3_class_and_instance_attributes.php
    defaultWidthLengthRatio = 0.4
    MaxOutputTextureHeight = 500
    defaultColor = 'y'
    TextureFolder = 'textures'
    Header = '# File Created: ' + datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + ' by CSV_To_3D ((c) Jean-Baptiste BARREAU)\n\n'
    counter = 0
    repere = Repere()
    repere.texturefolder = 'textures'
    gradientType = "Aucun"
    HasTextureText = False
    lengths = []
    widths = []
    angles = []
    heights = []
    
    def __init__(self):
        self.id = 0
        self.csvfilename = "undefined.csv"
        self.name = "undefined"
        self.texturepath = ""
        self.point_talon = [0, 0, 0]
        self.point_orteil = [0, 0, 0]
        self.cross_vector = [0, 0, 0]
        self.dir_vector = [0, 0, 0]
        self.halfwidth = 0
        
    def create(self,_csvfilename,_name,_texturepath,_x1,_y1,_z1,_x2,_y2,_z2):
        Empreinte.counter +=1
        self.id = Empreinte.counter
        self.csvfilename = _csvfilename
        self.name = _name
        self.texturepath = _texturepath
        self.point_talon = np.array([CleanStr2Float(_x1),CleanStr2Float(_y1),CleanStr2Float(_z1)])
        self.point_orteil = np.array([CleanStr2Float(_x2),CleanStr2Float(_y2),CleanStr2Float(_z2)])
        
        Empreinte.repere.GetRepereMinMax(_x1,_y1,_z1,_x2,_y2,_z2)
        self.dir_vector = GetDirectionVec(self.point_talon,self.point_orteil)
        self.halfwidth = GetHalfWidth(LA.norm(self.dir_vector),Empreinte.defaultWidthLengthRatio,'./' + self.texturepath)
        self.cross_vector = GetCrossVec(self.point_talon,self.point_orteil)
        Empreinte.lengths.append(self.GetLength())
        Empreinte.widths.append(2*self.halfwidth)
        Empreinte.angles.append(self.GetAngleDeg())
        Empreinte.heights.append(round((self.point_talon[2] + self.point_orteil[2])/2,2))
    
    ################################################################################
    ######### Textures
    ################################################################################
    def CreateTexture(self):
        l_color = (255,255,255)
        l_text_array = []
        if Empreinte.HasTextureText :
            l_text_array = ['Nom: ' + self.name, 
                            'Longueur: ' + str(self.GetLength()) + Empreinte.repere.textUnit, 
                            'Largeur: ' + str(round(2*self.halfwidth,2))+ Empreinte.repere.textUnit,
                            'Altitude: ' + str(round((self.point_talon[2] + self.point_orteil[2])/2,2))+ Empreinte.repere.textUnit,
                            'Angle: ' + str(self.GetAngleDeg()) + "deg"]
        
        if Empreinte.gradientType == "None":
            l_color = (255,255,255)
        elif Empreinte.gradientType == "Angle of rotation":
            l_color = GetGradientColorFromFloat(self.GetAngleDeg(), np.amin(Empreinte.angles), np.amax(Empreinte.angles))
        elif Empreinte.gradientType == "Height":
            l_color = GetGradientColorFromFloat(round((self.point_talon[2] + self.point_orteil[2])/2,2), np.amin(Empreinte.heights), np.amax(Empreinte.heights))
        
        CreateTexture(self.name,self.texturepath,Empreinte.TextureFolder,Empreinte.MaxOutputTextureHeight,l_text_array,0.3,(255, 255, 255),l_color)
    
    ################################################################################
    ######### OBJ
    ################################################################################
    def GetObj(self):
        res = GetObjHeader(self.id,Empreinte.Header,self.csvfilename,self.name)
        res += GetObjFaceVertices(self.point_talon,self.point_orteil,self.halfwidth)
        res += GetObjNormale(self.point_talon,self.point_orteil)
        res += GetFaceTextureCoords()
        res += GetObjFaceCoords(self.id,self.name)
        return res;
    
    def GetMtl(self):
        res = ''
        if self.id == 1:
            res += Empreinte.Header
    
        res += 'newmtl Material_' + str(self.id) + '_' + self.name + '\n'
        l_outputpath = './' + Empreinte.TextureFolder + '/' + self.name + '.jpg'
        if self.texturepath != '':
            res += '	map_Kd ' + l_outputpath + '\n'
        else:
            res += '	Kd ' + Empreinte.defaultColor + '\n'
            
        res += '\n'
        return res;
 
    ################################################################################
    ######### Analyse
    ################################################################################
    def AnalyseEmpreintes():
        l_result = 'Count: ' + str(Empreinte.counter) + '\n'
        l_result += '###########################\n'
        l_result += 'Lengths\n'
        l_result += 'Mean: ' + str(round(np.mean(Empreinte.lengths),4)) + 'm\n'
        l_result += 'Median: ' + str(round(np.median(Empreinte.lengths),4)) + 'm\n'
        l_result += 'SD: ' + str(round(np.std(Empreinte.lengths),4)) + 'm\n'
        l_result += 'Min: ' + str(round(np.amin(Empreinte.lengths),4)) + 'm\n'
        l_result += 'Max: ' + str(round(np.amax(Empreinte.lengths),4)) + 'm\n'
        l_result += '###########################\n'
        l_result += 'Largeurs\n'
        l_result += 'Mean: ' + str(round(np.mean(Empreinte.widths),4)) + 'm\n'
        l_result += 'Median: ' + str(round(np.median(Empreinte.widths),4)) + 'm\n'
        l_result += 'SD: ' + str(round(np.std(Empreinte.widths),4)) + 'm\n'
        l_result += 'Min: ' + str(round(np.amin(Empreinte.widths),4)) + 'm\n'
        l_result += 'Max: ' + str(round(np.amax(Empreinte.widths),4)) + 'm\n'
        l_result += '###########################\n'
        l_result += 'Altitudes\n'
        l_result += 'Mean: ' + str(round(np.mean(Empreinte.heights),4)) + 'm\n'
        l_result += 'Median: ' + str(round(np.median(Empreinte.heights),4)) + 'm\n'
        l_result += 'SD: ' + str(round(np.std(Empreinte.heights),4)) + 'm\n'
        l_result += 'Min: ' + str(round(np.amin(Empreinte.heights),4)) + 'm\n'
        l_result += 'Max: ' + str(round(np.amax(Empreinte.heights),4)) + 'm\n'
        l_result += '###########################\n'
        l_result += 'Angles\n'
        l_result += 'Mean: ' + str(round(np.mean(Empreinte.angles),4)) + '°\n'
        l_result += 'Median: ' + str(round(np.median(Empreinte.angles),4)) + '°\n'
        l_result += 'SD: ' + str(round(np.std(Empreinte.angles),4)) + '°\n'
        l_result += 'Min: ' + str(round(np.amin(Empreinte.angles),4)) + '°\n'
        l_result += 'Max: ' + str(round(np.amax(Empreinte.angles),4)) + '°\n'
        l_result += '###########################\n'

        Empreinte.ShowGraph()
        
        return l_result;
    
    def ShowGraph():
        plt.subplots_adjust(hspace = 0.6)
        
        plt.subplot(4, 2, 1)
        l_hist = plt.hist(Empreinte.lengths, edgecolor='#000000', color='#EE6666', align='left', orientation = 'horizontal')
        # plt.yticks(range(0, int(max(l_hist[0])+1)))
        plt.title('Histograms')
        plt.ylabel('Lengths (m)')
        
        plt.subplot(4, 2, 3)
        l_hist = plt.hist(Empreinte.widths, edgecolor='#000000', color='#2591e6', align='left', orientation = 'horizontal')
        # plt.yticks(range(0, int(max(l_hist[0])+1)))
        plt.ylabel('Widths (m)')
        
        plt.subplot(4, 2, 5)
        l_hist = plt.hist(Empreinte.heights, edgecolor='#000000', color='#FFD700', align='left', orientation = 'horizontal')
        # plt.yticks(range(0, int(max(l_hist[0])+1)))
        plt.ylabel('Altitudes (m)')
        
        plt.subplot(4, 2, 7)
        l_hist = plt.hist(Empreinte.angles, edgecolor='#000000', color='#86e625', align='left', orientation = 'horizontal')
        # plt.yticks(range(0, int(max(l_hist[0])+1)))
        plt.ylabel('Angles (deg)')
        
        plt.subplot(4, 2, 2)
        plt.boxplot(Empreinte.lengths, showfliers=False)
        plt.xticks([1], [''])
        plt.title('Box plot')
        
        plt.subplot(4, 2, 4)
        plt.boxplot(Empreinte.widths, showfliers=False)
        plt.xticks([1], [''])
        
        plt.subplot(4, 2, 6)
        plt.boxplot(Empreinte.heights, showfliers=False)
        plt.xticks([1], [''])
        
        plt.subplot(4, 2, 8)
        plt.boxplot(Empreinte.angles, showfliers=False)
        plt.xticks([1], [''])
        
        plt.show()
        
        return '';
    
    ################################################################################
    ######### 
    ################################################################################
    def GetAngleDeg(self):
        l_tmp_vector = (self.dir_vector[0], self.dir_vector[1], 0)
        res = np.sign(self.dir_vector[2])*round(np.degrees(math.acos(np.dot(l_tmp_vector, self.dir_vector) / (LA.norm(l_tmp_vector)*LA.norm(self.dir_vector)))),1)
        return res;
    
    def GetLength(self):
        return round(LA.norm(self.dir_vector),2);