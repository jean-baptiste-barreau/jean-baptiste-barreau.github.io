from obj_utils import *

class Repere:
    def __init__(self):
        self.origin = [100000000,100000000,100000000]
        self.max = [-100000000,-100000000,-100000000]
        self.startFaceCounter = 0
        self.axisWidth = 0.02
        self.textWidth = 0.3
        self.fontSize = 0.65
        self.textUnit = "m"
        self.texturefolder = ""
    
    def GetRepereMinMax(self,_x1,_y1,_z1,_x2,_y2,_z2, _x3="none", _y3="none", _z3="none"):
        self.GetOriginCoord(_x1, 0)
        self.GetOriginCoord(_x2, 0)
        self.GetOriginCoord(_x3, 0)
        self.GetOriginCoord(_y1, 1)
        self.GetOriginCoord(_y2, 1)
        self.GetOriginCoord(_y3, 1)
        self.GetOriginCoord(_z1, 2)
        self.GetOriginCoord(_z2, 2)
        self.GetOriginCoord(_z3, 2)
        self.GetMaxCoord(_x1, 0)
        self.GetMaxCoord(_x2, 0)
        self.GetMaxCoord(_x3, 0)
        self.GetMaxCoord(_y1, 1)
        self.GetMaxCoord(_y2, 1)
        self.GetMaxCoord(_y3, 1)
        self.GetMaxCoord(_z1, 2)
        self.GetMaxCoord(_z2, 2)
        self.GetMaxCoord(_z3, 2)
        self.startFaceCounter += 1
    
    def GetOriginCoord(self,_value, _idx):
        if (_value != "none") and (_value != ""): self.origin[_idx] = min(self.origin[_idx],CleanStr2Float(_value))
    def GetMaxCoord(self,_value, _idx):
        if (_value != "none") and (_value != ""): self.max[_idx] = max(self.max[_idx],CleanStr2Float(_value))
    
    def createAxis(self,_start,_end,_name):
        self.startFaceCounter += 1
        l_res = GetObjFaceVertices(np.array(_start),np.array(_end),self.axisWidth)
        l_res += GetObjNormale(np.array(_start),np.array(_end))
        l_res += GetFaceTextureCoords()
        l_res += GetObjFaceCoords(self.startFaceCounter,_name)
        return l_res;
    
    def createFaceCoordinates(self,_center,_name,_vertical):
        self.startFaceCounter += 1
        if _vertical:
            l_start = [_center[0],_center[1],_center[2]-self.textWidth]
            l_end = [_center[0],_center[1],_center[2]+self.textWidth]            
        else:
            l_start = [_center[0],_center[1]-self.textWidth,_center[2]]
            l_end = [_center[0],_center[1]+self.textWidth,_center[2]]
            
        l_res = GetObjFaceVertices(np.array(l_start),np.array(l_end),self.textWidth)
        l_res += GetObjNormale(np.array(l_start),np.array(l_end))
        l_res += GetFaceTextureCoords()
        l_res += GetObjFaceCoords(self.startFaceCounter,_name)
        return l_res;
    
    def GetObj(self):
        ################################################################################
        ######### Axis
        ################################################################################
        l_origin = self.origin
        l_x_axis_end = [self.max[0],self.origin[1],self.origin[2]]
        l_y_axis_end = [self.origin[0],self.max[1],self.origin[2]]
        l_z_axis_end = [self.origin[0],self.origin[1],self.max[2]]
        l_axis_grid_count = 10
        l_text_shift = 1.1*self.textWidth
        
        l_coordinate = [self.origin[0],self.origin[1]-l_text_shift,self.origin[2]]
        l_res = self.createFaceCoordinates(l_coordinate,"none_origin",False)
        
        l_res += self.createAxis(l_origin,l_x_axis_end,"x_mainaxis")
        l_coordinate = [l_x_axis_end[0],l_x_axis_end[1]-l_text_shift,l_x_axis_end[2]]
        l_res += self.createFaceCoordinates(l_coordinate,"none_endx",False)
        
        l_res += self.createAxis(self.origin,l_y_axis_end,"y_mainaxis")
        l_coordinate = [l_y_axis_end[0]-l_text_shift,l_y_axis_end[1],l_y_axis_end[2]]
        l_res += self.createFaceCoordinates(l_coordinate,"none_endy",False)
        
        l_res += self.createAxis(self.origin,l_z_axis_end,"z_mainaxis")
        l_coordinate = [self.origin[0]-l_text_shift,self.origin[1],self.origin[2]+(self.max[2]-self.origin[2])/2]
        l_res += self.createFaceCoordinates(l_coordinate,"none_middlez",True)
        
        ################################################################################
        ######### Grid
        ################################################################################
        l_length = LA.norm(np.array(l_y_axis_end) - np.array(l_origin))
        l_shift = round(l_length/l_axis_grid_count)
        
        i=1
        while i*l_shift < l_length:
            l_start = [l_origin[0],l_origin[1]+i*l_shift,l_origin[2]]
            l_end = [l_x_axis_end[0],l_x_axis_end[1]+i*l_shift,l_x_axis_end[2]]
            l_res += self.createAxis(l_start,l_end,"x_grid") 
            i += 1
       
        l_length = LA.norm(np.array(l_x_axis_end) - np.array(l_origin))
        l_shift = round(l_length/l_axis_grid_count)
        i=1
        while i*l_shift < l_length:
            l_start = [l_origin[0]+i*l_shift,l_origin[1],l_origin[2]]
            l_end = [l_y_axis_end[0]+i*l_shift,l_y_axis_end[1],l_y_axis_end[2]]
            l_res += self.createAxis(l_start,l_end,"y_grid") 
            i += 1 

        return l_res;
    
    def GetMtl(self):
        l_text_array = [str(round(self.origin[0],2))+self.textUnit,str(round(self.origin[1],2))+self.textUnit,str(round(self.origin[2],2))+self.textUnit]
        CreateTexture('origin','',self.texturefolder,500,l_text_array,self.fontSize,(0, 0, 0),(255, 255, 255))
        l_text_array = [str(round(self.max[0],2))+self.textUnit,str(round(self.origin[1],2))+self.textUnit,str(round(self.origin[2],2))+self.textUnit]
        CreateTexture('endx','',self.texturefolder,500,l_text_array,self.fontSize,(0, 0, 0),(255, 255, 255))
        l_text_array = [str(round(self.origin[0],2))+self.textUnit,str(round(self.max[1],2))+self.textUnit,str(round(self.origin[2],2))+self.textUnit]
        CreateTexture('endy','',self.texturefolder,500,l_text_array,self.fontSize,(0, 0, 0),(255, 255, 255))
        l_text_array = ['',str(round(self.max[2]-self.origin[2],2))+self.textUnit,'']
        CreateTexture('middlez','',self.texturefolder,500,l_text_array,self.fontSize,(0, 0, 0),(255, 255, 255))
        
        l_res = 'newmtl Material_mainaxis\n'
        l_res += '	Kd 0.0 0.0 0.0\n'
        
        l_res += 'newmtl Material_grid\n'
        l_res += '	Kd 0.8 0.8 0.8\n'
        
        l_res += 'newmtl Material_origin\n'
        l_res += '	map_Kd ./' + self.texturefolder + '/origin.png\n'
        
        l_res += 'newmtl Material_endx\n'
        l_res += '	map_Kd ./' + self.texturefolder + '/endx.png\n'
        
        l_res += 'newmtl Material_endy\n'
        l_res += '	map_Kd ./' + self.texturefolder + '/endy.png\n'
        
        l_res += 'newmtl Material_middlez\n'
        l_res += '	map_Kd ./' + self.texturefolder + '/middlez.png\n'
        
        return l_res;