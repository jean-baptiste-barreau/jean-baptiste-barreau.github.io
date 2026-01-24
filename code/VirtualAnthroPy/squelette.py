import numpy as np
from numpy import linalg as LA
import math
import datetime

from obj_utils import *
from repere import Repere

import matplotlib.pyplot as plt

class Squelette:
    counter = 0
    facecounter = 0
    HasTextureText = False
    repere = Repere()
    TextureFolder = 'textures_skel'
    repere.texturefolder = 'textures_skel'
    Header = '# File Created: ' + datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + ' by CSV_To_3D ((c) Jean-Baptiste BARREAU)\n\n'
    
    def __init__(self):
        self.id = 0
        self.csvfilename = "undefined.csv"
        self.name = "undefined"
        self.topmaterial = "undefined"
        self.bottommaterial = "undefined"
        self.fullmaterial = "undefined"
        self.grave = "undefined"
        self.field = "undefined"
        self.type = "undefined"
        self.skeleton = "undefined"
        self.age_min = "undefined"
        self.age_max = "undefined"
        self.sex = "undefined"
        self.deposit = "undefined"
        self.funeral_architecture = "undefined"
        self.toptexturepath = "skeltemplates/top.png"
        self.bottomtexturepath = "skeltemplates/bottom.png"
        self.fulltexturepath = "skeltemplates/full.png"
        self.point_head = [0, 0, 0]
        self.point_pelvis = [0, 0, 0]
        self.point_feet = [0, 0, 0]
        self.halfwidth = 0.0
        
    def create(self,_creationcsvdata):
        Squelette.counter +=1
        self.id = Squelette.counter
        self.csvfilename = _creationcsvdata["csvfilename"]
        self.name = "skeleton" + str(Squelette.counter)
        self.grave = _creationcsvdata["grave"] if _creationcsvdata["grave"] != "" else "?"
        self.field = _creationcsvdata["field"] if _creationcsvdata["field"] != "" else "?"
        self.type = _creationcsvdata["type"] if _creationcsvdata["type"] != "" else "?"
        self.skeleton = _creationcsvdata["skeleton"] if _creationcsvdata["skeleton"] != "" else "?"
        self.age_min = _creationcsvdata["age_min"] if _creationcsvdata["age_min"] != "" else "?"
        self.age_max = _creationcsvdata["age_max"] if _creationcsvdata["age_max"] != "" else "?"
        self.sex = _creationcsvdata["sex"] if _creationcsvdata["sex"] != "" else "?"
        self.deposit = _creationcsvdata["deposit"] if _creationcsvdata["deposit"] != "" else "?"
        self.funeral_architecture = _creationcsvdata["funeral_architecture"] if _creationcsvdata["funeral_architecture"] != "" else "?"
        
        Squelette.repere.GetRepereMinMax(_creationcsvdata["x1"],_creationcsvdata["y1"],_creationcsvdata["z1"],
                                         _creationcsvdata["x2"],_creationcsvdata["y2"],_creationcsvdata["z2"],
                                         _creationcsvdata["x3"],_creationcsvdata["y3"],_creationcsvdata["z3"])
        
        self.point_head = np.array([CleanStr2Float(_creationcsvdata["x1"]),CleanStr2Float(_creationcsvdata["y1"]),CleanStr2Float(_creationcsvdata["z1"])])
        self.point_pelvis = np.array([CleanStr2Float(_creationcsvdata["x2"]),CleanStr2Float(_creationcsvdata["y2"]),CleanStr2Float(_creationcsvdata["z2"])])
        self.point_feet = np.array([CleanStr2Float(_creationcsvdata["x3"]),CleanStr2Float(_creationcsvdata["y3"]),CleanStr2Float(_creationcsvdata["z3"])])
        
    def CreateTexture(self):
        l_text_array = []
        if Squelette.HasTextureText :
            l_text_array = ['grave: ' + self.grave,
                            'field: ' + self.field,
                            'type: ' + self.type,
                            'skeleton: ' + self.skeleton,
                            'age_min: ' + self.age_min,
                            'age_max: ' + self.age_max,
                            'sex: ' + self.sex,
                            'deposit: ' + self.deposit,
                            'architecture: ' + self.funeral_architecture]
            
        CreateTexture('top'+self.name,self.toptexturepath,Squelette.TextureFolder,500,l_text_array,0.3,(0, 0, 0),(255,255,255))
        CreateTexture('bottom'+self.name,self.bottomtexturepath,Squelette.TextureFolder,500,[],0.3,(0, 0, 0),(255,255,255))
        CreateTexture('full'+self.name,self.fulltexturepath,Squelette.TextureFolder,500,l_text_array,0.3,(0, 0, 0),(255,255,255))
    
    def GetObj(self):
        res = ''
        if (not np.array_equal(self.point_head, [0, 0, 0])) and (not np.array_equal(self.point_pelvis, [0, 0, 0])):
            if self.halfwidth == 0.0: self.halfwidth = GetHalfWidth(LA.norm(GetDirectionVec(self.point_pelvis,self.point_head)),0.4,self.toptexturepath)
            res += self.GetFace(self.point_pelvis, self.point_head,'top'+self.name,self.toptexturepath)
            self.topmaterial = 'Material_' + str(Squelette.facecounter) + '_' + 'top' + self.name
        if (not np.array_equal(self.point_pelvis, [0, 0, 0])) and (not np.array_equal(self.point_feet, [0, 0, 0])):
            res += self.GetFace(self.point_feet, self.point_pelvis,'bottom'+self.name,self.bottomtexturepath)
            self.bottommaterial = 'Material_' + str(Squelette.facecounter) + '_' + 'bottom' + self.name
        if (not np.array_equal(self.point_head, [0, 0, 0])) and (np.array_equal(self.point_pelvis, [0, 0, 0])) and (not np.array_equal(self.point_feet, [0, 0, 0])):
            if self.halfwidth == 0.0: self.halfwidth = 0.5*GetHalfWidth(LA.norm(GetDirectionVec(self.point_feet,self.point_head)),0.4,self.toptexturepath)
            res += self.GetFace(self.point_feet, self.point_head,'full'+self.name,self.fulltexturepath)
            self.fullmaterial = 'Material_' + str(Squelette.facecounter) + '_' + 'full' + self.name
        return res;
    
    def GetFace(self,_FirstPoint, _SecondPoint,_Name,_Texturepath):
        res = ''
        Squelette.facecounter += 1
        res += GetObjHeader(self.facecounter,Squelette.Header,self.csvfilename,_Name)
        res += GetObjFaceVertices(_FirstPoint,_SecondPoint,self.halfwidth)
        res += GetObjNormale(_FirstPoint,_SecondPoint)
        res += GetFaceTextureCoords()
        res += GetObjFaceCoords(Squelette.facecounter,_Name)
        return res;
    
    def GetMtl(self):
        res = ''
        if Squelette.facecounter == 1:
            res += Squelette.Header
    
        res += 'newmtl ' + self.topmaterial + '\n'
        res += '	map_Kd ' + './' + Squelette.TextureFolder + '/' + 'top' + self.name + '.jpg' + '\n'
        res += '\n'
        
        res += 'newmtl ' + self.bottommaterial + '\n'
        res += '	map_Kd ' + './' + Squelette.TextureFolder + '/' + 'bottom' + self.name + '.jpg' + '\n'
        res += '\n'
        
        res += 'newmtl ' + self.fullmaterial + '\n'
        res += '	map_Kd ' + './' + Squelette.TextureFolder + '/' + 'full' + self.name + '.jpg' + '\n'
        res += '\n'
        
        return res;