# main.py
import tkinter as tk
from tkinter import messagebox
import traceback

from app import PyknFitApp


def main():
    try:
        root = tk.Tk()
        app = PyknFitApp(root)
        root.mainloop()
    except Exception as e:
        # En mode --windowed, il n'y a pas de console :
        # on affiche l'erreur dans une boîte de dialogue.
        traceback.print_exc()
        try:
            messagebox.showerror(
                "Erreur PyknFit",
                f"Une erreur est survenue :\n\n{e}\n\n"
                f"Détails :\n{traceback.format_exc()}"
            )
        except Exception:
            # Si même messagebox échoue (pas de Tk), on écrit dans un fichier
            with open("pyknfit_error.log", "w", encoding="utf-8") as f:
                f.write(traceback.format_exc())


if __name__ == "__main__":
    main()