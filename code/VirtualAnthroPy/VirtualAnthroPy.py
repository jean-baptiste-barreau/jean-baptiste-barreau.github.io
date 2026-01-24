from pathlib import Path

from tkinter import *
from tkinter import ttk
from tkinter import LEFT, TOP, X, FLAT, RAISED
from tkinter.filedialog import askopenfilename
from tkinter import colorchooser
from tkinter import messagebox


from empreinte import Empreinte
from squelette import Squelette

import os
import csv

root = Tk(  )
root.geometry('500x600')
Title = root.title( "VirtualAnthroPy")
csv_delimiter = ';'

colnumber=5

################################################################################
######### Progress bar
################################################################################
style = ttk.Style(root)
style.layout('text.Horizontal.TProgressbar',
             [('Horizontal.Progressbar.trough',
               {'children': [('Horizontal.Progressbar.pbar',
                              {'side': 'left', 'sticky': 'ns'})],
                'sticky': 'nswe'}),
              ('Horizontal.Progressbar.label', {'sticky': ''})])
style.configure('text.Horizontal.TProgressbar', text='0 %')
progress = ttk.Progressbar(root, style='text.Horizontal.TProgressbar', orient = HORIZONTAL, length = 350, mode = 'determinate') 
progress['value'] = 0
progress.grid(column = 0, row = 1, pady  =2, columnspan=colnumber) 

################################################################################
######### Options
################################################################################
labelListeCalqueGradients = ttk.Label(root, text = "Color gradient:").grid(column = 0, row = 2, sticky=E)
ListeCalqueGradients = ttk.Combobox(root, values=["None","Angle of rotation", "Height"])
ListeCalqueGradients.current(0)
ListeCalqueGradients.grid(column = 1, row = 2, sticky=W)
HasTextureText = BooleanVar()
l_checkbutton = Checkbutton(root, text="Text info on textures", variable=HasTextureText).grid(column = 2, row = 2, sticky=W)
HasTextureText.set(True)
UnityLabel = ttk.Label(root, text = "Unit").grid(column = 3, row = 2, sticky=E)
UnityValue = ttk.Entry(root, width=4)
UnityValue.insert(0, "m")
UnityValue.grid(column = 4, row = 2, sticky=W)

################################################################################
#########
################################################################################
def Init():
    Empreinte.counter = 0
    Empreinte.repere.startFaceCounter = 0
    Squelette.repere.startFaceCounter = 0
    updateProgressBar('',0)
    Empreinte.gradientType = ListeCalqueGradients.get()
    Empreinte.HasTextureText = bool(HasTextureText.get())
    Empreinte.repere.textUnit = UnityValue.get()
    Squelette.repere.textUnit = UnityValue.get()
    Squelette.HasTextureText = bool(HasTextureText.get())

################################################################################
######### Empreintes
################################################################################
def ConvertCsvToEmpreinteObj(csvfilename):
    Init()
    
    l_result = 'Erreur'
    #création fichiers sortie
    objfile = open(csvfilename.replace("csv", "obj"), "w")
    mtlfile = open(csvfilename.replace("csv", "mtl"), "w")
    l_filename = os.path.basename(csvfilename)
    row_count = len(list(csv.reader(open(csvfilename))))
    
    #lecture/écriture fichier sortie
    l_empreintes = []
    with open(csvfilename, mode='r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=csv_delimiter)
        
        i = 0
        for row in csv_reader:
            l_empreintes.append(Empreinte())
            l_empreintes[i].create(l_filename,f'{row[0]}',f'{row[7]}',f'{row[1]}',f'{row[2]}',f'{row[3]}',f'{row[4]}',f'{row[5]}',f'{row[6]}')
            objfile.write(l_empreintes[i].GetObj())
            mtlfile.write(l_empreintes[i].GetMtl())
            i+=1
            updateProgressBar('création fichier obj',0.5*100* Empreinte.counter / row_count)
    
    i = 1      
    for empreinte in l_empreintes:
        empreinte.CreateTexture()
        updateProgressBar('création textures',50 + 0.5 * 100* i / row_count)
        i+=1
    
    Empreinte.repere.startFaceCounter = Empreinte.counter
    
    objfile.write(Empreinte.repere.GetObj())
    mtlfile.write(Empreinte.repere.GetMtl())
    objfile.close()
    mtlfile.close()
    l_result = 'File ' + l_filename + ' successfully converted'
    return l_result;

def OpenAndConvertCsvToEmpreinteObj():
    name = askopenfilename(initialdir=".",
                                   filetypes =(("Fichier csv", "*.csv"),("All Files","*.*")),
                                   title = "Choisir un fichier."
                                   )
    try:
        l_msg = ConvertCsvToEmpreinteObj(name)
        text.configure(state='normal')
        text.delete('1.0', END)
        text.insert(INSERT, Empreinte.AnalyseEmpreintes())
        text.configure(state='disabled')
        # messagebox.showinfo("Info", l_msg)
        updateProgressBar(l_msg,100)
        
    except:
        messagebox.showinfo("Info", "Erreur")

################################################################################
######### Squelettes
################################################################################
def ConvertCsvToSqueletteObj(csvfilename):
    Init()
    
    objfile = open(csvfilename.replace("csv", "obj"), "w")
    mtlfile = open(csvfilename.replace("csv", "mtl"), "w")
    row_count = len(list(csv.reader(open(csvfilename))))
    
    l_filename = os.path.basename(csvfilename)
    i = 0
    l_squelettes = []
    with open(csvfilename, mode='r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=csv_delimiter)
        next(csv_reader)
        for row in csv_reader:
            l_creationcsvdata =	{
              "csvfilename": l_filename,
              "grave": f'{row[1]}',
              "field": f'{row[2]}',
              "type": f'{row[4]}',
              "skeleton": f'{row[16]}',
              "age_min": f'{row[17]}',
              "age_max": f'{row[18]}',
              "sex": f'{row[19]}',
              "deposit": f'{row[20]}',
              "funeral_architecture": f'{row[22]}',
              "texturepath": "",
              "x1": f'{row[23]}',
              "y1": f'{row[24]}',
              "z1": f'{row[25]}',
              "x2": f'{row[26]}',
              "y2": f'{row[27]}',
              "z2": f'{row[28]}',
              "x3": f'{row[29]}',
              "y3": f'{row[30]}',
              "z3": f'{row[31]}'
            }
            l_squelettes.append(Squelette())
            l_squelettes[i].create(l_creationcsvdata)
            objfile.write(l_squelettes[i].GetObj())
            mtlfile.write(l_squelettes[i].GetMtl())
            i+=1
            updateProgressBar('création fichier obj',0.5*100* Squelette.counter / row_count)
            
    
    i = 1      
    for squelette in l_squelettes:
        squelette.CreateTexture()
        updateProgressBar('création textures',50 + 0.5 * 100* i / row_count)
        i+=1
    
    Squelette.repere.startFaceCounter = Squelette.facecounter
    objfile.write(Squelette.repere.GetObj())
    mtlfile.write(Squelette.repere.GetMtl())
    
    objfile.close()
    mtlfile.close()
    
    l_result = 'File ' + l_filename + ' successfully converted'
    return l_result;
        
def OpenAndConvertCsvToSqueletteObj():
    name = askopenfilename(initialdir=".",
                                   filetypes =(("Fichier csv", "*.csv"),("All Files","*.*")),
                                   title = "Choisir un fichier."
                                   )
    try:
        l_msg = ConvertCsvToSqueletteObj(name)
        updateProgressBar(l_msg,100)
        
    except:
        messagebox.showinfo("Info", "Erreur")

################################################################################
#########
################################################################################
def updateProgressBar(_textstate,_percent):
    progress['value'] = round(_percent)
    style.configure('text.Horizontal.TProgressbar', text='{:g} %'.format(round(_percent)) + ' (' + _textstate + ')')
    root.update_idletasks()

################################################################################
######### Toolbar
################################################################################
toolbar = Frame(root.master, bd=1, relief=SUNKEN, width=500)
toolbar.grid(column=0, row=0, columnspan=3, sticky=W)
buttons = [["footprint.png","skel.png","exit.png"],["OpenAndConvertCsvToEmpreinteObj","OpenAndConvertCsvToSqueletteObj","root.destroy"],[]]
l_photo = []
l_photoimage = []
def CreateButton(_imageFilename,_idx):
    icon_folder = Path("./icons/")
    l_photo.append(PhotoImage(file = icon_folder / _imageFilename))
    l_photoimage.append(l_photo[_idx].subsample(7, 7))
    buttons[2].append(Button(toolbar, image = l_photoimage[_idx], command = eval(buttons[1][_idx])))
    buttons[2][_idx].grid(column=_idx, row=0)

for i, image in enumerate(buttons[0]):
    CreateButton(image,i)
    

################################################################################
######### Texte
################################################################################
text = Text(root, width=62, height=30)

text.configure(state='disabled')
text.grid(column=0, row=3, columnspan=colnumber)

root.update_idletasks()

root.mainloop()
input("Appuyez sur Entrée pour fermer...")