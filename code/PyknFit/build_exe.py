# build_exe.py
"""
Script de construction de l'exécutable PyknFit.
Usage :
    python build_exe.py

Produit :
    dist/PyknFit.exe (Windows)
    dist/PyknFit     (Linux/macOS)
"""
import os
import shutil
import sys

import PyInstaller.__main__


def clean():
    """Nettoie les artefacts de build précédents."""
    for folder in ("build", "dist", "__pycache__"):
        if os.path.isdir(folder):
            print(f"Nettoyage : {folder}/")
            shutil.rmtree(folder)
    spec = "PyknFit.spec"
    if os.path.isfile(spec):
        os.remove(spec)


def build():
    # Séparateur de données selon l'OS : ';' sous Windows, ':' ailleurs
    sep = ";" if sys.platform.startswith("win") else ":"

    args = [
        "main.py",
        "--name=PyknFit",
        "--onefile",
        "--windowed",
        "--clean",
        "--noconfirm",
        "--icon=logo.ico",

        # --- Ressources embarquées ---
        f"--add-data=logo.png{sep}.",

        # --- Modules cachés ---
        "--hidden-import=pyknfit",
        "--hidden-import=pyknfit.distributions",
        "--hidden-import=pyknfit.distributions.gaussian",
        "--hidden-import=pyknfit.distributions.lognormal",
        "--hidden-import=pyknfit.distributions.weibull",
        "--hidden-import=pyknfit.mixtures.mixture_model",
        "--hidden-import=pyknfit.diagnostics.metrics",
        "--hidden-import=lmfit",
        "--hidden-import=lmfit.models",
        "--hidden-import=openpyxl",
        "--hidden-import=scipy._lib.messagestream",
        "--hidden-import=scipy.special._cdflib",
        "--hidden-import=PIL._tkinter_finder",

        # --- Collecter les data files des grosses libs ---
        "--collect-all=matplotlib",
        "--collect-all=scipy",
        "--collect-all=lmfit",
        "--collect-all=PIL",

        # --- Exclusions pour réduire la taille ---
        "--exclude-module=PyQt5",
        "--exclude-module=PyQt6",
        "--exclude-module=PySide2",
        "--exclude-module=PySide6",
        "--exclude-module=wx",
        "--exclude-module=notebook",
        "--exclude-module=IPython",
        "--exclude-module=jupyter",
        "--exclude-module=pytest",
        "--exclude-module=sphinx",
    ]

    print("Construction de PyknFit.exe ...")
    PyInstaller.__main__.run(args)
    print("\nTerminé. Vérifie le dossier dist/")


if __name__ == "__main__":
    clean()
    build()