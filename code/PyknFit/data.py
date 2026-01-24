import os
import numpy as np 
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import tkinter.simpledialog as sd
from tkinter import filedialog, messagebox, Tk
import tkinter as tk
from tkinter import ttk

class DataManager:
    def __init__(self, app):
        self.app = app

    def load_data(self):
        root = Tk()
        root.withdraw()
        fichier_path = filedialog.askopenfilename(
            title=self.app.t("choose_file"),
            filetypes=[("Fichiers Excel", "*.xlsx *.xls"), ("Fichiers CSV", "*.csv"), ("Tous les fichiers", "*.*")]
        )
        if not fichier_path:
            print(self.app.t("no_file_selected"))
            return None

        try:
            if fichier_path.endswith(('.xlsx', '.xls')):
                self.app.m_imported_data = pd.read_excel(fichier_path)
            elif fichier_path.endswith('.csv'):
                try:
                    self.app.m_imported_data = pd.read_csv(fichier_path, sep="\t")
                except:
                    self.app.m_imported_data = pd.read_csv(fichier_path, sep=";")
            else:
                print("Format non supporté.")
                return None

            self.app.m_imported_data = self.app.m_imported_data.applymap(
                lambda x: float(str(x).replace(",", ".")) if isinstance(x, str) and x.replace(",", "").replace(".", "").isdigit() else x
            )

            self.app.selection_echantillon.config(state="normal")
            self.app.selection_echantillon["values"] = list(self.app.m_imported_data.columns[1:])
            self.app.selection_echantillon.current(0)
            self.app.selection_echantillon.bind("<<ComboboxSelected>>", self.update_input_data_on_change)

            self.update_input_data(0)

        except Exception as e:
            print(f"Erreur import : {e}")
            return None

    def update_input_data(self, idx):
        l_x_data = '\n'.join([str(round(x, 10)).replace('.', ',') for x in self.app.m_imported_data.iloc[:, 0].values])
        l_y_data = '\n'.join([str(round(x, 10)).replace('.', ',') for x in self.app.m_imported_data.iloc[:, idx + 1].values])
        l_titre = self.app.m_imported_data.columns[idx + 1]
        self.insert_input_data(l_titre, l_x_data, l_y_data)

    def update_input_data_on_change(self, event):
        if hasattr(self.app.ui, "graph_frame"):
            for widget in self.app.ui.graph_frame.winfo_children():
                widget.destroy()

        self.app.m_dynamic_x = []
        self.app.m_dynamic_y = []
        self.app.m_init_centers_selected = []
        self.app.m_annotations = {}
        self.app.m_model = None
        self.app.m_components_model = None
        self.app.m_last_error_metrics = None

        self.update_input_data(self.app.selection_echantillon.current())

    def insert_input_data(self, _title="Test", _x_data="0,03\n0,04\n0,07\n0,1\n0,2\n0,3\n0,4\n0,5\n0,6\n0,7\n0,8\n0,9\n1\n1,1\n1,2\n1,3\n1,4\n1,6\n1,8\n2\n2,2\n2,4\n2,6\n3\n4\n5\n6\n6,5\n7\n7,5\n8\n8,5\n9\n10\n11\n12\n13\n14\n15\n16\n17\n18\n19\n20\n22\n25\n28\n32\n36\n38\n40\n45\n50\n53\n56\n63\n71\n75\n80\n85\n90\n95\n100\n106\n112\n125\n130\n140\n145\n150\n160\n170\n180\n190\n200\n212\n242\n250\n300\n400\n500\n600\n700\n800\n900\n1000\n1100\n1200\n1300\n1400\n1500\n1600\n1700\n1800\n1900\n2000\n2100\n2200\n2300\n2400\n2500", _y_data="0\n0,034098991\n0,030277868\n0,025002823\n0,052749706\n0,127566357\n0,077497708\n0\n0\n0\n0,073463388\n0,121143157\n0,169283159\n0,205847235\n0,245978329\n0,289676472\n0,336941689\n0,400709389\n0,499715521\n0,584026898\n0,664325168\n0,737934986\n0,791039597\n0,866232058\n0,967171391\n1,023098084\n1,085866914\n1,147564486\n1,227430437\n1,305505782\n1,423245638\n1,544549755\n1,638214543\n1,794401484\n1,964905428\n2,090815795\n2,20599775\n2,274356398\n2,313718167\n2,349046199\n2,368309625\n2,402714663\n2,391638845\n2,434047723\n2,470166823\n2,595137319\n2,762033312\n2,945214009\n3,111864835\n3,183353773\n3,19903415\n3,18000786\n3,072489334\n2,93850203\n2,80203335\n2,581863525\n2,230493033\n1,936256012\n1,741057771\n1,529839758\n1,341775721\n1,15458427\n1,008391199\n0,902977186\n0,793639504\n0,690270695\n0,636655055\n0,577614323\n0,559093733\n0,552409788\n0,552716753\n0,558979912\n0,592877644\n0,626774318\n0,660670096\n0,704016111\n0,741183296\n0,767761833\n0,7728242\n0,703679185\n0,447605412\n0,088043263\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0"):
        self.app.m_titre_entry.delete("0", "end")
        self.app.m_titre_entry.insert(0, _title)
        self.app.m_textX.delete("1.0", "end")
        self.app.m_textX.insert("1.0", _x_data)
        self.app.m_textY.delete("1.0", "end")
        self.app.m_textY.insert("1.0", _y_data)

    def enregistrer_graphique(self):
        if self.app.m_fig2:
            l_titre = self.app.m_titre_graphique + "_" + datetime.now().strftime("%d-%m-%Y")
            fichier = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("SVG", "*.svg"), ("Tous les fichiers", "*.*")],
                initialfile=l_titre
            )
            if fichier:
                ext = os.path.splitext(fichier)[1].lower()
                if ext in [".png", ".jpg", ".svg"]:
                    self.app.m_fig2.savefig(fichier, dpi=300, bbox_inches='tight')
                    messagebox.showinfo("Enregistrement", self.app.t("graph_saved")+f"'{fichier}'")
                else:
                    messagebox.showerror("Erreur", self.app.t("unsupported_format")+f" : {ext}")
        else:
            messagebox.showinfo("Info", self.app.t("error_graph"))

    def enregistrer_resultats_decomposition(self):
        if not self.app.m_tous_les_resultats:
            messagebox.showinfo("Info", self.app.t("no_results"))
            return

        df = pd.DataFrame(self.app.m_tous_les_resultats)
        l_titre = 'Résultats_décomposition_' + datetime.now().strftime("%d-%m-%Y")
        fichier = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel", "*.xlsx")],
            initialfile=l_titre
        )
        if fichier:
            df.to_excel(fichier, index=False)
            messagebox.showinfo("Enregistrement", self.app.t("results_saved")+ f" '{fichier}'")
            
    def enregistrer_points_gaussiennes_excel(self):
        if self.app.m_model is None or self.app.m_fig1_X is None:
            messagebox.showinfo("Info", self.app.t("no_model"))
            return

        fichier = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel", "*.xlsx")],
            initialfile=f"Points_gaussiennes_{self.app.m_titre_graphique}"
        )
        if not fichier:
            return

        import tkinter.simpledialog as sd

        sample_size = sd.askinteger(
            self.app.t("sampling"),
            self.app.t("num_points"),
            initialvalue=self.app.m_sampling_model_size,
            minvalue=50,
            maxvalue=50000
        )
        if sample_size is None:
            return

        self.app.m_sampling_model_size = sample_size

        x_dense = np.linspace(
            min(self.app.m_fig1_X),
            max(self.app.m_fig1_X),
            self.app.m_sampling_model_size
        )

        components_eval = self.app.m_model.eval_components(x=x_dense)
        best_fit = self.app.m_model.eval(x=x_dense)

        x_dense = x_dense[::-1]
        best_fit = best_fit[::-1]
        for rank, (name, y_component) in enumerate(components_eval.items(), start=1):
            components_eval[name] = y_component[::-1]

        X_microns = 1000 * (2 ** (-x_dense))

        data = {
            "X_phi": x_dense,
            "X_µm": X_microns,
            "Best_fit": best_fit
        }

        for rank, (name, y_component) in enumerate(components_eval.items(), start=1):
            data[f"G{rank}"] = y_component

        df = pd.DataFrame(data)
        df.to_excel(fichier, index=False)

        messagebox.showinfo(
            self.app.t("save_success"),
            self.app.t("save_points") + f"\n{fichier}"
        )