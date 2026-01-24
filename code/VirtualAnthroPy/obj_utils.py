import os
import numpy as np
from numpy import linalg as LA
import cv2
from colour import Color

################################################################################
######### 
################################################################################
def GetCrossVec(_P1,_P2):
    l_dir = GetDirectionVec(_P1,_P2)
    if (l_dir[0] != 0) or (l_dir[1] != 0):
        res = np.cross((_P2-_P1), [0, 0, 1])
        res /= LA.norm(res)
    else:   
        res = np.array([1, 0, 0])
    return res;

################################################################################
######### 
################################################################################
def GetDirectionVec(_P1,_P2):
    return _P2-_P1;

################################################################################
######### 
################################################################################
def GetObjHeader(_id,_header,_filename,_name):
    res = ''
    if _id == 1:
        res += _header
        res += 'mtllib ' + _filename.replace("csv", "mtl") + '\n\n'
    
    res += '# object ' + _name + '\n\n'
    return res;

################################################################################
######### 
################################################################################
def GetObjFaceVertices(_P1,_P2,_halfwidth):
    res=""
    l_crossvector = GetCrossVec(_P1,_P2)
    res = 'v  ' + CleanStrVector(np.array_str(_P1+_halfwidth*l_crossvector)) + '\n'
    res += 'v  ' + CleanStrVector(np.array_str(_P1-_halfwidth*l_crossvector)) + '\n'
    res += 'v  ' + CleanStrVector(np.array_str(_P2-_halfwidth*l_crossvector)) + '\n'
    res += 'v  ' + CleanStrVector(np.array_str(_P2+_halfwidth*l_crossvector)) + '\n'
    res += '\n'
    return res;

################################################################################
######### 
################################################################################
def GetObjNormale(_P1,_P2):
    l_normal_vector = np.cross(GetDirectionVec(_P1,_P2), GetCrossVec(_P1,_P2))
    l_normal_vector /= LA.norm(l_normal_vector)
    res = 'vn ' + CleanStrVector(np.array_str(l_normal_vector)) + '\n'
    res += '\n'
    return res;

################################################################################
######### 
################################################################################
def GetFaceTextureCoords():
    res = 'vt 1.0000 0.0000\n'
    res += 'vt 0.0000 0.0000\n'
    res += 'vt 0.0000 1.0000\n'
    res += 'vt 1.0000 1.0000\n'
    res += '\n'
    return res;

################################################################################
######### 
################################################################################
def UseMtl(_id,_name):
    res = ''
    if len(_name.split("_")) > 1:
        res = 'usemtl Material_' + _name.split("_")[1] + '\n' 
    else:
        res = 'usemtl Material_' + str(_id) + '_' + _name + '\n'       
    return res;

################################################################################
######### 
################################################################################
def GetObjFaceCoords(_id,_name):
    res = 'g ' + _name + '\n'
    res += UseMtl(_id,_name)
    l_idx = 4*(_id-1)+1
    res += 'f ' + str(l_idx) + '/' + str(l_idx) + '/' + str(_id) + ' '
    res += str(l_idx+1) + '/' + str(l_idx+1) + '/' + str(_id) + ' '
    res += str(l_idx+2) + '/' + str(l_idx+2) + '/' + str(_id) + ' '
    res += str(l_idx+3) + '/' + str(l_idx+3) + '/' + str(_id) + ' '+ '\n\n'
    return res;

################################################################################
######### 
################################################################################
def CreateTexture(_name,_inputTexturePath,_outputTextureFolder,_maxOutputTextureHeight,_text_array,_font_size,_font_color,_overlayColor):
    if not os.path.exists(_outputTextureFolder):
        os.mkdir(_outputTextureFolder)
    
    l_font_color = _font_color
    l_text_spacement = 10
    l_extension = '.jpg'
    
    if _inputTexturePath != '':
        src = cv2.imread(_inputTexturePath, cv2.IMREAD_UNCHANGED)
        l_size = (src.shape[1],src.shape[0])
        if _maxOutputTextureHeight < src.shape[0]:
            l_size = (int(src.shape[1]*_maxOutputTextureHeight/src.shape[0]), _maxOutputTextureHeight)
        output = cv2.resize(src, l_size)
        
        ######### Calque couleur
        if list(_overlayColor) !=  [255, 255, 255]:
            output = cv2.cvtColor(output, cv2.COLOR_BGR2GRAY)
            output = cv2.cvtColor(output, cv2.COLOR_GRAY2BGR)
            overlay = output.copy()
            cv2.rectangle(overlay, (0, 0), (src.shape[1],src.shape[0]), _overlayColor, -1)
            cv2.addWeighted(overlay, 0.4, output, 1 - 0.4, 0, output)
    else:
        l_font_color = (0, 0, 0)
        l_font_size = 1
        l_text_spacement = 30
        l_extension = '.png'
        output = 255*np.ones(shape=[110, 110, 3], dtype=np.uint8)
        
    i=1
    for _text in _text_array:
        output = cv2.putText(output, _text, (5, i*l_text_spacement), cv2.FONT_HERSHEY_COMPLEX, _font_size, l_font_color, 1, cv2.LINE_AA, False)
        i+=1
    
    l_outputpath = './' + _outputTextureFolder + '/' + _name + l_extension
    cv2.imwrite(l_outputpath,ConvertWhiteToTransparent(output))

################################################################################
######### 
################################################################################
def GetGradientColorFromFloat(_Value,_Min,_Max):
    l_ratio = (_Value - _Min) / (_Max - _Min)
    l_colorCount = 100
    l_idx = int(round((l_colorCount-1)*l_ratio))
    colors = list(Color("#fff702").range_to(Color("red"),l_colorCount))
    res = (round(255*colors[l_idx].blue),round(255*colors[l_idx].green),round(255*colors[l_idx].red))
    return res;

################################################################################
######### 
################################################################################
def ConvertWhiteToTransparent(_image):
    res = cv2.cvtColor(_image, cv2.COLOR_BGR2BGRA)
    res[np.where((res==[255,255,255,255]).all(axis=2))] = [255,255,255,0]
    return res;

################################################################################
######### 
################################################################################
def CleanStrVector(_strvector):
    return _strvector.replace('[','').replace(']','').replace('       ','');

################################################################################
######### 
################################################################################
def CleanStr2Float(_strfloat):
    res = float(_strfloat.replace(',','.')) if (_strfloat != "") else 0
    return res;

################################################################################
######### 
################################################################################
def GetHalfWidth(_VectorNorm,_WidthLengthRatio,_Texturepath):
    res = 0.5*_VectorNorm*_WidthLengthRatio
    if _Texturepath != '':
        l_img = cv2.imread(_Texturepath, cv2.IMREAD_UNCHANGED)
        res = (_VectorNorm*l_img.shape[1])/(2*l_img.shape[0])
    return res;