import tkinter as tk
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tkinter import Menu, simpledialog, Toplevel, ttk, Tk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.interpolate import interp1d
import re


class PlotManager:
    def __init__(self, app):
        self.app = app

    def extract_sigma_value(self, text):
        m = re.search(r'σ\s*=\s*([\d.]+)', text)
        return float(m.group(1)) if m else None

    def extract_amplitude_value(self, text):
        for line in text.split("\n"):
            if line.startswith("A="):
                try:
                    return float(line.split("=")[1])
                except:
                    return None
        return None

    def on_click(self, event):
        if event.inaxes:
            if event.button == 1 and not self.app.m_edit_point_menu_open:
                x_new = event.xdata
                y_new = self.app.interpolator(x_new)
                self.app.m_dynamic_x.append(x_new)
                self.app.m_dynamic_y.append(y_new)
                self.app.m_init_centers_selected.append(round(x_new, 1))

                annotation = self.app.m_ax0.annotate(
                    f"σ=1.0\nA={np.round(y_new,1)}",
                    (x_new, y_new),
                    textcoords="offset points", xytext=(5, -15),
                    ha='left', fontsize=10, color='red'
                )
                self.app.m_annotations[x_new] = annotation

            elif event.button == 3:
                if self.app.m_dynamic_x:
                    distances = [(x - event.xdata) ** 2 + (y - event.ydata) ** 2
                                 for x, y in zip(self.app.m_dynamic_x, self.app.m_dynamic_y)]
                    nearest_index = distances.index(min(distances))
                    x_selected_point = self.app.m_dynamic_x[nearest_index]
                    annotation = self.app.m_annotations[x_selected_point].get_text()
                    self.show_context_menu(event, nearest_index, x_selected_point, annotation)

            if self.app.m_dynamic_x:
                self.app.scatter.set_offsets(list(zip(self.app.m_dynamic_x, self.app.m_dynamic_y)))
            else:
                self.app.scatter.set_offsets(np.empty((0, 2)))
            event.canvas.draw_idle()

    def show_context_menu(self, event, index, x_selected_point, annotation):
        self.app.m_edit_point_menu_open = True
        root = Tk()
        root.withdraw()
        menu = Menu(root, tearoff=0)
        menu.add_command(label=self.app.t("edit"), command=lambda: self.edit_point(index, x_selected_point, annotation))
        menu.add_command(label=self.app.t("delete"), command=lambda: self.delete_point(index, x_selected_point))
        menu.post(event.guiEvent.x_root, event.guiEvent.y_root)
        root.mainloop()

    def edit_point(self, index, x_selected_point, annotation):
        root = Tk()
        root.withdraw()
        temp_window = Toplevel(root)
        temp_window.withdraw()
        temp_window.grab_set()
        temp_window.lift()
        sigma = simpledialog.askfloat(self.app.t("edit") + " σ", "σ",
                                      initialvalue=self.extract_sigma_value(annotation),
                                      parent=temp_window)
        amplitude = simpledialog.askfloat(self.app.t("edit") + " A", "A",
                                          initialvalue=self.extract_amplitude_value(annotation),
                                          parent=temp_window)
        temp_window.destroy()
        if sigma is not None and amplitude is not None:
            self.app.m_annotations[x_selected_point].set_text(f"σ={sigma:.1f}\nA={amplitude:.1f}")
            plt.draw()
        self.app.m_edit_point_menu_open = False

    def delete_point(self, index, x_selected_point):
        self.app.m_dynamic_x.pop(index)
        self.app.m_dynamic_y.pop(index)
        self.app.m_init_centers_selected.pop(index)
        if x_selected_point in self.app.m_annotations:
            self.app.m_annotations[x_selected_point].remove()
            del self.app.m_annotations[x_selected_point]
        if self.app.m_dynamic_x:
            self.app.scatter.set_offsets(list(zip(self.app.m_dynamic_x, self.app.m_dynamic_y)))
        else:
            self.app.scatter.set_offsets(np.empty((0, 2)))
        plt.draw()
        self.app.m_edit_point_menu_open = False

    def afficher_graphique_donnees_wrapper(self):
        if (self.app.m_titre_entry.get()
            and self.app.m_textX.get("1.0", "end").strip()
            and self.app.m_textY.get("1.0", "end").strip()):
            self.afficher_graphique_donnees()
            self.app.m_process_menu.entryconfig(self.app.m_entry_save_graph,   state="normal")
            self.app.m_process_menu.entryconfig(self.app.m_entry_save_results, state="disabled")
            self.app.m_process_menu.entryconfig(self.app.m_entry_save_gauss,   state="disabled")
        else:
            messagebox.showerror(self.app.t("error"), self.app.t("need_data"))

    def afficher_graphique_donnees(self):
        self.app.model.calcul_resultats()

        for w in self.app.ui.graph_frame.winfo_children():
            w.destroy()

        self.app.m_fig0, self.app.m_ax0 = plt.subplots(figsize=(6, 4), dpi=150)
        self.app.m_ax0.plot(self.app.m_chiffresX_phi, self.app.m_chiffresY_µ, '-')
        self.app.m_ax0.set_title(self.app.m_titre_graphique + "\n(" + self.app.t("left_click_help") + ", " + self.app.t("right_click_help") + ")")
        self.app.m_ax0.set_xlabel(self.app.t("x_label_phi"))
        self.app.m_ax0.set_ylabel(self.app.t("y_label_frequency"))
        self.app.m_ax0.invert_xaxis()
        self.app.m_ax0.grid(True)

        self.app.scatter = self.app.m_ax0.scatter(self.app.m_dynamic_x, self.app.m_dynamic_y, color='red', zorder=5)

        self.app.interpolator = interp1d(self.app.m_chiffresX_phi, self.app.m_chiffresY_µ,
                                         kind='linear', bounds_error=False, fill_value="extrapolate")

        self.app.m_fig0.canvas.mpl_connect("button_press_event", self.on_click)

        canvas = FigureCanvasTkAgg(self.app.m_fig0, master=self.app.ui.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack()

        if not self.app.bouton_calculer_visible:
            frame_boutons = tk.Frame(self.app.root)
            frame_boutons.grid(row=5, column=0, padx=10, pady=10)
            self.app.root.grid_columnconfigure(0, weight=1)
            frame_boutons.grid_configure(sticky='n')

            label_dist = tk.Label(frame_boutons, text="Distribution :")
            label_dist.pack(side=tk.LEFT, padx=(0, 5))
            self.app.distribution_type = ttk.Combobox(frame_boutons, values=['Gaussienne', 'Log-normale', 'Weibull'])
            self.app.distribution_type.current(0)
            self.app.distribution_type.pack(side=tk.LEFT, padx=(0, 10))

            self.app.bouton_calculer = tk.Button(
                frame_boutons, text=self.app.t("calculate_model"),
                command=self.afficher_graphique_resultats_wrapper
            )
            self.app.bouton_calculer.pack(side=tk.LEFT)
            
            self.app.bouton_calculer_visible = True

    def afficher_graphique_resultats_wrapper(self, mode=1):
        if len(self.app.m_init_centers_selected) >= 1:
            self.app.model.calcul_resultats()
            self.afficher_graphique_resultats()
            self.app.m_process_menu.entryconfig(self.app.m_entry_save_graph,   state="normal")
            self.app.m_process_menu.entryconfig(self.app.m_entry_save_results, state="normal")
            self.app.m_process_menu.entryconfig(self.app.m_entry_save_gauss,   state="normal")
        else:
            messagebox.showerror(self.app.t("error"), self.app.t("need_one_center"))

    def ajouter_valeurs_centrales(self, ax):
        composantes = []
        
        for i, p in enumerate(self.app.m_model_params, start=1):
            # Récupérer la distribution correspondante
            dist = self.app.model.distributions[i-1] if hasattr(self.app.model, 'distributions') else None
            
            # Déterminer les paramètres selon le type de distribution
            info = dist.table_info(p)

            composantes.append({
                "index": i,
                "phi": info["phi"],
                "amplitude": p["amplitude"],
                "hauteur": info["hauteur"],
                "micron": info["micron"],
                "params_table": info["params_table"]
            })
        
        # Trier par diamètre (ordre croissant)
        composantes = sorted(composantes, key=lambda c: c['micron'])
        
        # Mettre à jour les listes de l'app
        self.app.m_centres_microns = [c['micron'] for c in composantes]
        self.app.m_centres_phi = [c['phi'] for c in composantes]
        self.app.m_distribution_params = [
            c["params_table"]
            for c in composantes
        ]
        self.app.m_amplitudes = [c['hauteur'] for c in composantes]
        
        # Calculer les proportions
        self.app.m_proportions = self.app.model.calculer_aires_et_proportions()
        
        # Créer le DataFrame pour le tableau
        rows = []
        for c in composantes:
            row = {
                'μm': round(c['micron'], 2),
            }
            row.update({
                k: round(v, 2)
                for k, v in c['params_table'].items()
            })
            row['H'] = round(c['hauteur'], 2)
            rows.append(row)

        df = pd.DataFrame(rows)
        # df['Diamètre (µm)'] = df['Diamètre (µm)'].astype(float)
        
        # Afficher la légende/tableau
        self.afficher_legende_parameters(ax, df)
        
        return [c['index'] for c in composantes]  # ordre des indices

    def afficher_canvas(self, fig, graph_frame):
        canvas = FigureCanvasTkAgg(fig, master=graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack()
        return canvas
    
    def afficher_legende_parameters(self, _ax, _param_df):
        table = _ax.table(cellText=_param_df.values, colLabels=_param_df.columns, loc='upper left', cellLoc='center', bbox=[0, 0.5, 0.3, 0.5])
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        
        for key, cell in table.get_celld().items():
            cell.set_linewidth(0)
        
        l_curves_default_colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
        for i in range(len(_param_df)):
            color = l_curves_default_colors[(i+1) % len(l_curves_default_colors)]
            for j in range(len(_param_df.columns)):
                table[i + 1, j].get_text().set_color(color)
    
    def afficher_graphique_resultats(self):
        try:
            for widget in self.app.ui.graph_frame.winfo_children():
                widget.destroy()

            self.app.m_fig2, self.app.m_ax2 = plt.subplots(figsize=(6, 4), dpi=150)

            order_indices = self.ajouter_valeurs_centrales(self.app.m_ax2)
            self.app.m_proportions = (
                self.app.m_model.calculer_aires_et_proportions()
            )
            
            distribution_type = getattr(
                self.app,
                'current_distribution_type',
                'Gaussienne'
            )
            
            use_log_scale = (
                len(self.app.m_model.distributions) > 0
                and self.app.m_model.distributions[0].use_log_scale
            )

            if use_log_scale:
                x_dense = np.geomspace(
                    max(min(self.app.m_fig1_X), 1e-6),
                    max(self.app.m_fig1_X),
                    self.app.m_sampling_model_size
                )
            else:
                x_dense = np.linspace(
                    min(self.app.m_fig1_X),
                    max(self.app.m_fig1_X),
                    self.app.m_sampling_model_size
                )

            self.app.m_ax2.plot(self.app.m_fig1_X, self.app.m_fig1_Y, 'o',
                                color='#99002299', markersize=4,
                                label=self.app.t("data"), zorder=19)
            self.m_best_fit_curve = self.app.m_ax2.plot(
                x_dense, self.app.m_model.eval(x=x_dense), '-',
                label=self.app.t("best_fit"), zorder=20
            )

            if use_log_scale:
                self.app.m_ax2.set_xscale("log")
                self.app.m_ax2.set_xlabel("Diamètre (µm)")
                self.app.m_ax2.set_xlabel(self.app.t("particle_diameter"))
                self.app.m_ax2.set_ylabel(self.app.t("y_label_frequency"), fontsize=8)
            else:
                self.app.m_ax2.invert_xaxis()
                self.app.m_ax2.set_xlim([min(self.app.m_fig1_X), max(self.app.m_fig1_X)])
                self.app.m_ax2.set_xticks(self.app.m_ticks)
                self.app.m_ax2.set_xticklabels(self.app.m_ticklabels)
                self.app.m_ax2.set_xlabel(self.app.t("particle_diameter"))
                self.app.m_ax2.set_ylabel(self.app.t("y_label_frequency"), fontsize=8)
                self.app.m_ax2.invert_xaxis()

            distribution_type = getattr(
                self.app,
                'current_distribution_type',
                'Gaussienne'
            )

            components_eval = self.app.m_model.eval_components(x_dense)
            for rank, i in enumerate(order_indices):
                name = f'g{i}_'
                y_component = components_eval[name]
                self.app.m_ax2.plot(x_dense, y_component,
                                    label=f'Component {rank+1}', linewidth=2)

                idx_max = np.argmax(y_component)
                x_peak = x_dense[idx_max]
                y_peak = y_component[idx_max]
                self.app.m_ax2.text(x_peak, y_peak * 0.5,
                                    f'{self.app.m_proportions[i-1]*100:.0f}%',
                                    ha='center', va='center', fontsize=8)

            l_error_texte = self.afficher_model_legend()

            # Titre principal au niveau de la figure (en haut)
            self.app.m_fig2.suptitle(
                self.app.t("multi_modal_title") + f" {self.app.m_titre_graphique}",
                fontsize=10,
                y=0.95  # Ajustez la position verticale
            )

            # Sous-titre (erreur) juste en dessous du titre principal
            self.app.m_ax2.set_title(l_error_texte, fontsize=7, pad=2)

            # Bloc d'informations du modèle (conditionnel)
            if getattr(self.app, "m_include_model_info", True):
                texte = (
                    self.app.m_model.formula_description()
                    + '\n\n'
                    + self.app.m_model.derived_quantities_description()
                )
                self.app.m_fig2.text(
                    0.5, 0.02, texte,
                    ha='center', va='bottom',
                    multialignment='left',
                    fontsize=6, family='monospace',
                    bbox=dict(facecolor='white', edgecolor='black', alpha=0.9)
                )
                self.app.m_fig2.subplots_adjust(bottom=0.38)
            else:
                self.app.m_fig2.subplots_adjust(bottom=0.15)

            canvas2 = self.afficher_canvas(self.app.m_fig2, self.app.ui.graph_frame)
            self.app.ui.graph_frame.update_idletasks()

        except Exception as e:
            import traceback
            traceback.print_exc()
            messagebox.showinfo(
                self.app.t("error"),
                self.app.t("error_graph") + f"\n{e}"
            )

    def afficher_model_legend(self):
        handles, labels = self.app.m_ax2.get_legend_handles_labels()
        filtered_handles = []
        filtered_labels = []

        for h, l in zip(handles, labels):
            if l in [self.app.t("data"), self.app.t("best_fit")]:
                filtered_handles.append(h)
                filtered_labels.append(l)

        self.app.m_ax2.legend(filtered_handles, filtered_labels, loc='best', fontsize=6)
        
        distribution_type = getattr(self.app, 'current_distribution_type', 'Gaussienne')
        
        l_error_texte = (
            "("+f'Distribution : {distribution_type} / ' +
            self.app.t("absolute_error")+f"={self.app.m_last_error_metrics['Erreur absolue']:.2f} / " +
            self.app.t("relative_error")+f"={self.app.m_last_error_metrics['Erreur relative (%)']:.2f}% / " + 
            self.app.t("MSE")+f"={self.app.m_last_error_metrics['MSE']:.4f} / " + 
            self.app.t("R_square")+f"={self.app.m_last_error_metrics['R²']:.4f})"
        )
        
        return l_error_texte