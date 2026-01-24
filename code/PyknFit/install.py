import subprocess
import sys

# Liste des librairies nécessaires
packages = [
    "numpy",
    "pandas",
    "matplotlib",
    "scipy",
    "lmfit",
    "pillow",
    "openpyxl",   # pour l'import/export Excel
]

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

if __name__ == "__main__":
    print("Installation des dépendances...")
    for pkg in packages:
        try:
            print(f"→ Installation de {pkg}...")
            install(pkg)
        except Exception as e:
            print(f"⚠️ Erreur lors de l'installation de {pkg} : {e}")

    print("\n✔️ Installation terminée.")
