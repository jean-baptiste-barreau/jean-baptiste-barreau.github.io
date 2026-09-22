from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk, Menu, Label, messagebox

class UIManager:
    def __init__(self, app):
        self.app = app

    def create_widgets(self):
        self.frame_titre = tk.Frame(self.app.root)
        
        logo_img = Image.open(self.app.logo_path)
        logo_img = logo_img.resize((80, 80))
        self.logo = ImageTk.PhotoImage(logo_img)

        logo_label = tk.Label(self.frame_titre, image=self.logo)
        logo_label.grid(row=0, column=2, rowspan=2, padx=10)
        
        self.frame_titre.grid(row=0, column=0, padx=10, pady=10)

        tk.Label(self.frame_titre, text=self.app.t("select_sample")).grid(row=0, column=0, sticky="e")
        self.app.selection_echantillon = ttk.Combobox(self.frame_titre, values=[], state="disabled", width=37)
        self.app.selection_echantillon.grid(row=0, column=1, padx=5, pady=2)

        tk.Label(self.frame_titre, text=self.app.t("sample_title")).grid(row=1, column=0, sticky="e")
        self.app.m_titre_entry = tk.Entry(self.frame_titre, width=40)
        self.app.m_titre_entry.grid(row=1, column=1, padx=5, pady=2)

        self.app.frameX = self.create_list_frame("x :", 1, self.app.root)
        self.app.m_textX = self.create_text_widget(self.app.frameX, 10, 40)
        self.app.uniteX = ttk.Combobox(self.app.frameX, values=["µ", "φ"], state="readonly", width=3)
        self.app.uniteX.current(0)
        self.app.uniteX.grid(row=0, column=3)

        self.app.frameY = self.create_list_frame("y :", 2, self.app.root)
        self.app.m_textY = self.create_text_widget(self.app.frameY, 10, 40)
        Label(self.app.frameY, text="", width=5).grid(row=0, column=4)

        self.graph_frame = tk.Frame(self.app.root)
        self.graph_frame.grid(row=0, column=1, rowspan=6, padx=10, pady=10)

        self.app.bouton_afficher_donnees = tk.Button(
            self.app.root, text=self.app.t("show_data"),
            command=self.app.plot.afficher_graphique_donnees_wrapper
        )
        self.app.bouton_afficher_donnees.grid(row=4, column=0, padx=10, pady=10)

        self.app.progress = ttk.Progressbar(self.app.root, orient="horizontal", length=300, mode="determinate")
        self.app.progress.grid(row=6, column=0, padx=10, pady=10)

        self.app.menu_contextuel = tk.Menu(self.app.root, tearoff=0)

    def create_menu(self):
        menuBar = tk.Menu(self.app.root)

        # ============================================================
        # Menu Fichier
        # ============================================================
        file_menu = tk.Menu(menuBar, tearoff=0)
        file_menu.add_command(
            label=self.app.t("import_data"),
            command=self.app.data.load_data
        )
        file_menu.add_command(
            label=self.app.t("generate_example"),
            command=self.app.data.insert_input_data
        )
        file_menu.add_separator()
        file_menu.add_command(
            label=self.app.t("quit"),
            command=self.app.root.destroy
        )

        # ============================================================
        # Menu Traitement
        # ============================================================
        process_menu = tk.Menu(menuBar, tearoff=0)
        process_menu.add_command(
            label=self.app.t("show_data"),
            command=self.app.plot.afficher_graphique_donnees_wrapper
        )
        process_menu.add_separator()

        # --- Entrées d'export (désactivées au départ) ---------------
        # ⚠️ add_command() renvoie None : on récupère l'index via menu.index("end")
        process_menu.add_command(
            label=self.app.t("save_full_graph"),
            command=self.app.data.enregistrer_graphique,
            state="disabled"
        )
        self.app.m_entry_save_graph = process_menu.index("end")

        process_menu.add_command(
            label=self.app.t("save_decomposition_results"),
            command=self.app.data.enregistrer_resultats_decomposition,
            state="disabled"
        )
        self.app.m_entry_save_results = process_menu.index("end")

        process_menu.add_command(
            label=self.app.t("save_gaussian_points"),
            command=self.app.data.enregistrer_points_gaussiennes_excel,
            state="disabled"
        )
        self.app.m_entry_save_gauss = process_menu.index("end")

        # --- Options d'export : case à cocher -----------------------
        process_menu.add_separator()
        self.app.var_include_model_info = tk.BooleanVar(
            value=getattr(self.app, "m_include_model_info", True)
        )
        process_menu.add_checkbutton(
            label=self.app.t("include_model_info"),
            variable=self.app.var_include_model_info,
            command=self.toggle_include_model_info
        )

        # ============================================================
        # Menu Langue
        # ============================================================
        lang_menu = tk.Menu(menuBar, tearoff=0)
        lang_menu.add_command(
            label="Français",
            command=lambda: self.app.set_language("fr")
        )
        lang_menu.add_command(
            label="English",
            command=lambda: self.app.set_language("en")
        )

        # ============================================================
        # Assemblage
        # ============================================================
        menuBar.add_cascade(label=self.app.t("file"),     menu=file_menu)
        menuBar.add_cascade(label=self.app.t("process"),  menu=process_menu)
        menuBar.add_cascade(label=self.app.t("language"), menu=lang_menu)

        self.app.root.config(menu=menuBar)

        # Références conservées pour activation/désactivation ultérieure
        self.app.m_file_menu    = file_menu
        self.app.m_process_menu = process_menu

    def create_context_menu(self):
        for action in [self.app.t("clear"), self.app.t("cut"), self.app.t("copy"), self.app.t("paste")]:
            self.app.menu_contextuel.add_command(label=action)

        self.bind_context_menu(self.app.m_textX)
        self.bind_context_menu(self.app.m_textY)

    def bind_context_menu(self, widget):
        widget.bind("<Button-3>", lambda event: self.afficher_menu_contextuel(event, widget))

    def afficher_menu_contextuel(self, event, text_widget):
        self.app.menu_contextuel.entryconfig(self.app.t("clear"), command=lambda: text_widget.delete("1.0", tk.END))
        self.app.menu_contextuel.entryconfig(self.app.t("cut"), command=lambda: text_widget.event_generate("<<Cut>>"))
        self.app.menu_contextuel.entryconfig(self.app.t("copy"), command=lambda: text_widget.event_generate("<<Copy>>"))
        self.app.menu_contextuel.entryconfig(self.app.t("paste"), command=lambda: text_widget.event_generate("<<Paste>>"))
        self.app.menu_contextuel.tk_popup(event.x_root, event.y_root)

    def create_list_frame(self, label_text, row, root):
        frame = tk.Frame(root)
        frame.grid(row=row, column=0, padx=10, pady=10)
        tk.Label(frame, text=label_text).grid(row=0, column=0)
        return frame

    def create_text_widget(self, frame, height, width):
        text_widget = tk.Text(frame, height=height, width=width)
        text_widget.grid(row=0, column=1)
        scrollbar = tk.Scrollbar(frame, command=text_widget.yview)
        scrollbar.grid(row=0, column=2, sticky="ns")
        text_widget.config(yscrollcommand=scrollbar.set)
        return text_widget

    def toggle_include_model_info(self):
        """
        Appelée quand l'utilisateur coche/décoche
        'Inclure les informations du modèle'.

        - Met à jour l'état persistant dans l'app.
        - Redessine le graphique des résultats si un modèle existe déjà,
          pour que l'encadré apparaisse/disparaisse immédiatement.
        """
        # 1) Synchroniser l'état persistant avec la BooleanVar
        self.app.m_include_model_info = self.app.var_include_model_info.get()

        # 2) Rafraîchir le graphique des résultats si nécessaire
        if self.app.m_fig2 is not None and self.app.m_model is not None:
            try:
                self.app.plot.afficher_graphique_resultats()
            except Exception as e:
                import traceback
                traceback.print_exc()
                messagebox.showerror(
                    self.app.t("error"),
                    self.app.t("error_graph") + f"\n{e}"
                )