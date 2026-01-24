#labelDefaultRatio = Label(root, text = "Ratio par défaut")
#labelDefaultRatio.grid(column=1, row=1, padx=6)
#EntryDefaultRatio = Entry(root, width=10)
#EntryDefaultRatio.insert(0,functions_CSV_2_3D.defaultWidthLengthRatio)
#EntryDefaultRatio.grid(column=2, row=1)

#SetDefaultColorButton = Button(root, text='Choisir la couleur\npar défaut des faces', command=SetDefaultColor)
#SetDefaultColorButton.grid(column=1, row=2, columnspan=2)

#SetVarButton = Button(root, text='Mise à jour\ndes paramètres', fg='#0577d1', command=SetGlobalVariables)
#SetVarButton.grid(column=1, row=3, columnspan=2)

################################################################################
#########
################################################################################
def SetDefaultColor():
    l_colorchosen = colorchooser.askcolor(title="Choisir la couleur par défaut des faces")
    l_colorchosen = str(l_colorchosen[0][0]/256) + " " + str(l_colorchosen[0][1]/256) + " " + str(l_colorchosen[0][2]/256)
    Empreinte.defaultColor = l_colorchosen
        
################################################################################
#########
################################################################################
def SetGlobalVariables():
    try:
        global g_colorchosen
        functions_CSV_2_3D.SetDefaultWidthLengthRatio(float(EntryDefaultRatio.get()))
        functions_CSV_2_3D.SetDefaultColor(g_colorchosen)
    except ValueError:
        messagebox.showerror("Erreur","Le ratio par défaut doit être un nombre réel")
    else:
        messagebox.showinfo("Info", "Variables mises à jour")