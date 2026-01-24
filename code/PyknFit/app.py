import tkinter as tk
from ui import UIManager
from data import DataManager
from plotting import PlotManager
from model import ModelManager
from i18n import LANGUAGES

class PyknFitApp:
    def __init__(self, root):
        self.lang = "fr"

        self.root = root
        self.root.title(self.t("app_title"))
        self.root.iconphoto(False, tk.PhotoImage(file="logo.png"))

        self.ui = UIManager(self)
        self.data = DataManager(self)
        self.plot = PlotManager(self)
        self.model = ModelManager(self)

        self.ui.create_widgets()
        self.ui.create_menu()
        self.ui.create_context_menu()

        self.init_attributes()

    def t(self, key):
        return LANGUAGES[self.lang].get(key, key)
    
    def set_language(self, lang):
        self.lang = lang
        self.refresh_ui()
    
    def refresh_ui(self):
        self.root.title(self.t("app_title"))

        for widget in self.root.winfo_children():
            widget.destroy()

        self.ui.create_widgets()
        self.ui.create_menu()
        self.ui.create_context_menu()
    
    def init_attributes(self):
        self.m_chiffresX_µ = []
        self.m_chiffresY_µ = []
        self.m_chiffresX_phi = []
        self.m_chiffresY_phi = []
        self.m_init_centers_selected = []
        self.m_centres_microns = []
        self.m_centres_phi = []
        self.m_proportions = []
        self.m_sigmas = []
        self.m_min_sigma = 0.1
        self.m_min_area_ratio = 0.01
        self.m_amplitudes = []
        self.m_last_error_metrics = None
        self.m_tous_les_resultats = []
        self.m_model = None
        self.m_components_model = None
        self.m_sampling_model_size = 1000
        self.m_titre_graphique = ""
        self.m_fig1_X = None
        self.m_fig1_Y = None
        self.m_best_fit_curve = None
        self.m_ticks = [-1.5849, 0, 3.3219, 6.6439, 9.9658, 13.2877, 16.6096]
        self.m_ticklabels = ['3000', '1000', '100', '10', '1', '0.1', '0.01']

        self.m_ax0 = None
        self.m_ax2 = None
        self.m_fig0 = None
        self.m_fig2 = None

        self.m_dynamic_x = []
        self.m_dynamic_y = []
        self.m_edit_point_menu_open = False
        self.m_annotations = {}

        self.bouton_calculer = None
        self.bouton_calculer_visible = False

        if hasattr(self.ui, "graph_frame"):
            for widget in self.ui.graph_frame.winfo_children():
                widget.destroy()
