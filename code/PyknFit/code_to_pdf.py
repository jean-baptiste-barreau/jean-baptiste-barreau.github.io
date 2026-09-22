import os
from fpdf import FPDF
from datetime import datetime

print("Demarrage du script...")

try:
    # CONFIGURATION
    directory = "."  # Repertoire courant (ou mettez un chemin)
    output_file = "code_python.pdf"
    
    # Noms des scripts a exclure (ajoutez les votres si besoin)
    scripts_to_exclude = [
        'pdf_generator.py',     # Nom par defaut
        'generate_pdf.py',      # Autre nom possible
        'code_to_pdf.py',       # Autre nom possible
        os.path.basename(__file__)  # Toujours exclure le script actuel
    ]
    scripts_to_exclude = list(set(scripts_to_exclude))  # Enlever les doublons
    
    print(f"Scripts exclus: {', '.join(scripts_to_exclude)}")
    print(f"Analyse du repertoire: {os.path.abspath(directory)}")
    
    # Recuperer tous les fichiers .py (sauf ceux exclus)
    py_files = []
    excluded_count = 0
    excluded_list = []
    
    for root, dirs, files in os.walk(directory):
        # Ignorer les dossiers inutiles
        dirs[:] = [d for d in dirs if d not in ['__pycache__', 'venv', 'env', '.git', 'node_modules']]
        for file in files:
            if file.endswith('.py'):
                full_path = os.path.join(root, file)
                # Verifier si le fichier doit etre exclu
                if file in scripts_to_exclude:
                    excluded_count += 1
                    excluded_list.append(full_path)
                    print(f"  EXCLU: {full_path}")
                else:
                    py_files.append(full_path)
                    print(f"  Ajoute: {full_path}")
    
    print(f"\nTotal fichiers Python trouves: {len(py_files) + excluded_count}")
    print(f"Fichiers inclus: {len(py_files)}")
    print(f"Fichiers exclus: {excluded_count}")
    for excl in excluded_list:
        print(f"  - {os.path.basename(excl)}")
    
    if len(py_files) == 0:
        print("\nATTENTION: Aucun fichier .py a inclure!")
        print("Verifiez que vous avez d'autres fichiers .py dans ce repertoire.")
    else:
        # Creer le PDF
        print("\nCreation du PDF en cours...")
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        
        # Titre
        pdf.set_font("Helvetica", "B", 18)
        pdf.cell(0, 15, "Code Source Python", 0, 1, "C")
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 6, f"Repertoire: {os.path.abspath(directory)}", 0, 1, "C")
        pdf.cell(0, 6, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 1, "C")
        pdf.cell(0, 6, f"Fichiers inclus: {len(py_files)}", 0, 1, "C")
        if excluded_count > 0:
            pdf.cell(0, 6, f"Fichiers exclus: {excluded_count}", 0, 1, "C")
        pdf.ln(10)
        
        # Liste des fichiers inclus
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_fill_color(200, 220, 255)
        pdf.cell(0, 8, "Liste des fichiers inclus:", 0, 1, "L", True)
        pdf.set_font("Helvetica", "", 9)
        for i, filepath in enumerate(py_files, 1):
            rel_path = os.path.relpath(filepath, directory)
            pdf.cell(0, 5, f"{i}. {rel_path}", 0, 1)
        pdf.ln(5)
        
        # Ajouter chaque fichier
        for i, filepath in enumerate(py_files, 1):
            print(f"  Ajout {i}/{len(py_files)}: {os.path.basename(filepath)}")
            
            pdf.add_page()
            
            # En-tete du fichier
            pdf.set_font("Helvetica", "B", 12)
            pdf.set_fill_color(230, 230, 230)
            pdf.cell(0, 10, f"Fichier: {os.path.basename(filepath)}", 0, 1, "L", True)
            pdf.set_font("Helvetica", "I", 9)
            pdf.cell(0, 6, f"Chemin: {filepath}", 0, 1)
            pdf.ln(5)
            
            # Lire le contenu
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    code = f.read()
            except:
                try:
                    with open(filepath, 'r', encoding='latin-1') as f:
                        code = f.read()
                except Exception as e:
                    code = f"# ERREUR DE LECTURE: {e}\n"
            
            # Ajouter le code
            pdf.set_font("Courier", "", 8)
            lines = code.split('\n')
            
            for line_num, line in enumerate(lines, 1):
                # Eviter les debordements de page
                if pdf.get_y() > 270:
                    pdf.add_page()
                    pdf.set_font("Courier", "", 8)
                
                try:
                    line_clean = line.encode('latin-1', 'replace').decode('latin-1')
                    
                    # Numero de ligne (gris)
                    pdf.set_text_color(150, 150, 150)
                    pdf.cell(18, 4, f"{line_num:4d}", 0, 0)
                    
                    # Code (noir)
                    pdf.set_text_color(0, 0, 0)
                    
                    # Gestion des lignes longues
                    max_width = pdf.w - pdf.l_margin - pdf.r_margin - 18
                    if pdf.get_string_width(line_clean) > max_width:
                        # Tronquer avec ...
                        while pdf.get_string_width(line_clean + "...") > max_width and len(line_clean) > 10:
                            line_clean = line_clean[:-10]
                        line_clean = line_clean + "..."
                    
                    pdf.cell(0, 4, line_clean, 0, 1)
                except:
                    pdf.set_text_color(150, 150, 150)
                    pdf.cell(18, 4, f"{line_num:4d}", 0, 0)
                    pdf.set_text_color(0, 0, 0)
                    pdf.cell(0, 4, "[?]", 0, 1)
        
        # Sauvegarder
        pdf.output(output_file)
        print(f"\n" + "="*50)
        print(f"SUCCES! PDF cree: {output_file}")
        
        if os.path.exists(output_file):
            size = os.path.getsize(output_file) / 1024
            print(f"Taille: {size:.2f} KB")
            print(f"Fichiers inclus: {len(py_files)}")
            if excluded_count > 0:
                print(f"Fichiers exclus: {excluded_count}")
                print(f"  ({', '.join([os.path.basename(e) for e in excluded_list])})")
        else:
            print("ERREUR: Le fichier PDF n'a pas ete cree!")

except Exception as e:
    print(f"\nERREUR: {e}")
    import traceback
    traceback.print_exc()

finally:
    print("\n" + "="*50)
    input("Appuyez sur ENTER pour fermer...")