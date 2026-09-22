# paths.py
"""
Résolution des chemins compatible PyInstaller (mode --onefile).
En mode .exe, les ressources sont extraites dans sys._MEIPASS.
En mode source, on utilise le dossier du fichier courant.
"""
import os
import sys


def resource_path(relative_path: str) -> str:
    """
    Retourne le chemin absolu d'une ressource (logo, icône, etc.)
    compatible avec le mode source et le mode PyInstaller --onefile.
    """
    if hasattr(sys, "_MEIPASS"):
        # Mode .exe : les données sont extraites dans _MEIPASS
        base_path = sys._MEIPASS
    else:
        # Mode source : dossier du fichier paths.py
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


def writable_path(filename: str) -> str:
    """
    Retourne un chemin d'écriture dans un dossier accessible en écriture.
    Utile pour les exports Excel/PNG/PDF par défaut.
    - Mode .exe : dossier de l'exécutable (là où l'utilisateur l'a mis)
    - Mode source : dossier du projet
    """
    if getattr(sys, "frozen", False):
        # sys.executable = chemin du .exe
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, filename)