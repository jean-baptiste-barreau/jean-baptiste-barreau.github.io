import json
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from opencage.geocoder import OpenCageGeocode
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from geopy.distance import geodesic
import requests
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import LabelEncoder
from sklearn.manifold import MDS
import os
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.cluster.hierarchy import fcluster
from sklearn.metrics import silhouette_score, calinski_harabasz_score
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import sys
import platform
from ydata_profiling import ProfileReport

#_corrected_manually Books about Africa -- Description and travel: https://www.gutenberg.org/ebooks/subject/612

# Initialiser les géocodeurs
def init_geolocators(opencage_key):
    geolocator = Nominatim(user_agent="geoapi")
    opencage_geocoder = OpenCageGeocode(opencage_key)
    return geolocator, opencage_geocoder

# Charger les données du fichier JSON
def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        return json.load(file)

# Sauvegarder les données dans le fichier JSON
def save_json(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

# Fonction pour obtenir les coordonnées avec Geopy
def get_coordinates_geopy(geolocator, lieu):
    try:
        location = geolocator.geocode(lieu, timeout=10)
        if location:
            return (location.latitude, location.longitude)
        return None
    except GeocoderTimedOut:
        return get_coordinates_geopy(geolocator, lieu)  # Réessayer en cas de timeout

# Fonction pour obtenir les coordonnées avec OpenCage
def get_coordinates_opencage(opencage_geocoder, lieu):
    result = opencage_geocoder.geocode(lieu)
    if result and len(result):
        return (result[0]['geometry']['lat'], result[0]['geometry']['lng'])
    return None

# Fonction pour afficher la progression
def afficher_progression(current, total):
    pourcentage = (current / total) * 100
    print(f"Progression: {pourcentage:.2f}%")

# Fonction pour traiter un lieu et ajouter les coordonnées manquantes
def process_location(geolocator, opencage_geocoder, etape):
    lieu = etape.get("lieu_depart")
    if lieu and not ("latitude" in etape and "longitude" in etape):
        coords = get_coordinates_geopy(geolocator, lieu)
        if coords:
            etape["latitude"] = coords[0]
            etape["longitude"] = coords[1]
            etape["source"] = "Geopy"
        else:
            coords = get_coordinates_opencage(opencage_geocoder, lieu)
            if coords:
                etape["latitude"] = coords[0]
                etape["longitude"] = coords[1]
                etape["source"] = "OpenCage"
            else:
                etape["latitude"] = None
                etape["longitude"] = None
                etape["source"] = "manual"
    return etape

# Fonction principale pour parcourir les étapes et ajouter les coordonnées manquantes
def process_explorateurs(filepath, geolocator, opencage_geocoder):
    data = load_json(filepath)
    
    # Compteurs pour les statistiques
    geopy_count = 0
    opencage_count = 0
    manual_null_count = 0
    manual_non_null_count = 0
    
    total_etapes = sum(len(voyage["etapes"]) for voyage in data if "etapes" in voyage)
    etapes_traitees = 0  # Compteur d'étapes traitées
    
    for voyage in data:
        if "etapes" in voyage:
            for etape in voyage["etapes"]:
                process_location(geolocator, opencage_geocoder, etape)
                
                # Compter les occurrences des sources et des coordonnées
                if etape.get("source") == "Geopy":
                    geopy_count += 1
                elif etape.get("source") == "OpenCage":
                    opencage_count += 1
                elif etape.get("source") == "manual":
                    if etape.get("latitude") is None or etape.get("longitude") is None:
                        manual_null_count += 1
                    else:
                        manual_non_null_count += 1

                etapes_traitees += 1
                afficher_progression(etapes_traitees, total_etapes)

    # Sauvegarder les modifications dans le fichier JSON
    save_json(filepath, data)
    
    # Afficher les statistiques
    print("Statistiques des sources :")
    print(f"Geopy: {geopy_count}")
    print(f"OpenCage: {opencage_count}")
    print(f"Manual avec coordonnées null: {manual_null_count}")
    print(f"Manual avec coordonnées non null: {manual_non_null_count}")
    
    return {
        "Geopy": geopy_count,
        "OpenCage": opencage_count,
        "Manual_null": manual_null_count,
        "Manual_non_null": manual_non_null_count
    }

def replace_images_with_urls(page_url):
    # Étape 1 : Télécharger la page
    response = requests.get(page_url)
    response.raise_for_status()  # Vérifie si la requête a réussi

    # Étape 2 : Analyser le contenu avec BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Étape 3 : Remplacer chaque <img> par son URL
    for img in soup.find_all('img'):
        if 'src' in img.attrs:
            # Récupérer l'URL de l'image
            img_url = img['src']
            
            # Remplacer la balise <img> par un lien vers l'image
            img.replace_with(img_url)

    # Étape 4 : Sauvegarder le contenu modifié dans un fichier HTML
    with open("pg70754-images-modified.html", "w", encoding='utf-8') as file:
        file.write(str(soup))

    print("Fichier HTML modifié enregistré avec succès.")

# Fonction pour extraire les moyens de transport uniques
def lister_moyens_transport(fichier_json):
    # Charger le fichier JSON
    with open(fichier_json, 'r', encoding='utf-8') as fichier:
        donnees = json.load(fichier)

    # Initialiser un ensemble pour stocker les moyens de transport uniques
    moyens_transport = set()

    # Parcourir les données
    for explorateur in donnees:
        if 'etapes' in explorateur:
            for etape in explorateur['etapes']:
                # Ajouter les moyens de transport à l'ensemble
                moyen = etape.get('moyen_transport', '').strip('.')
                if moyen:
                    moyens_transport.add(moyen)

    # Retourner les moyens de transport sous forme de liste triée
    return sorted(moyens_transport)

transport_categories = [
    {"type": "Boat", "items": [
        "Bateau", "Bateau sur le Niger", "Bateau à vapeur", "Bateau à vapeur (*Peters*)", 
        "Bateau à vapeur (*Scott*)", "Bateau à vapeur (Calabar)", "Bateau à vapeur (différent de *Deliverance*)",
        "Bateau à vapeur (non nommé)", "Bateau à vapeur *Deliverance*", "Bateau à vapeur \u00ab Pioneer \u00bb",
        "Bateau à vapeur \u00ab Pioneer \u00bb remorqué par le H.M.S. \u00ab Orestes \u00bb", "Cargo à vapeur, le 'Limpopo'.",
        "Cargo à voile, le 'Snowdrop'.", "Dahabieh", "Dhow", "Goélette", "Goélette de la marine française",
        "Lancement fluvial (\u00ab Réné Caillé \u00bb)", "Navire", "Navire côtier nommé 'Mesâoud'",
        "Navire de transport de troupes Neuralia", "Navire à vapeur ('Pentakota')",
        "Navire à vapeur ('Tabora' initialement, puis 'Möwe')", "Navire à vapeur ('Tabora')",
        "Navire à vapeur (probablement le 'Tabora')", "Navire à vapeur *Goëland*",
        "Navires à vapeur du lac [xix]", "Navires à vapeur du lac [xvii]", "Paquebot à vapeur français.",
        "Paquebot à vapeur russe, l'Odessa.", "Petit bateau à voile, le 'Meta'.", "Gáreb (petit navire)", "Par bateau sur le Niger", "Embarcation", "À pied, puis en pirogue pour traverser le Bagoé", "Le vapeur colonial de Sa Majesté « Pearl »", "Bateau à vapeur (*Peters* )", "Bateau à vapeur (*Scott* )", "Vapeur *Archimède*", "Vapeur *Richelieu*", "Vapeur *Bruxellesville*", "D'abord un bateau à vapeur appartenant à M. Philippi, puis un bateau à vapeur postal anglais", "Croiseur britannique ('Pegasus')", "Cargo à voile, le 'Snowdrop'", "Petit bateau à voile, le 'Meta'", "Cargo à vapeur, le 'Limpopo'", "Dow arabe puis marche à pied", "Paquebot à vapeur russe, l'Odessa", "Paquebot à vapeur français", "Barge fluviale", "Chaloupe", "Chaloupe et canot", "Chaloupe à quatre rameurs", "Petite chaloupe",
        "Petite chaloupe remorquée par une chaloupe à voile", "Canot", "Pirogue", "Pirogues", "Pirogue (probablement, car il voyageait en pirogue depuis Niafounké et a ensuite continué jusqu'à Kabara)",
        "Pirogues pour traverser le Dhioliba", "Radeau"
    ]},
    {"type": "Caravan", "items": [
        "Caravane", "Caravane (mule pour Mr. Lucas)", "Caravane avec chameaux", "Caravane avec chameaux, chevaux et mulets",
        "Caravane avec une escorte arabe.", "Caravane de chameaux", "Caravane de chameaux et de voitures Lefèvre tirées par des mulets",
        "Caravane de chameaux, chevaux et mulets.", "Caravane de chameaux, faisant partie du *Taralum*, un rassemblement massif de commerçants se rendant aux oasis de Fachi et Bilma pour le sel",
        "Caravane de chameaux, puis âne", "Caravane de mules", "Grande caravane de chameaux", "Âne (pour Richardson) et caravane avec chameaux", "Caravane de chameaux, chevaux et mulets", "Caravane avec une escorte arabe", "Non spécifié, probablement une caravane de chameaux"
    ]},
    {"type": "Camelid", "items": [
        "Chameau", "Chameau jusqu'à Touggourt", "Chameaux", "Chameaux (loués)", "Chameaux et ânes",
        "Chameaux pour le voyage principal, ânes loués pour atteindre la première station.", "Chameaux, buffles et mules",
        "Chameaux, chevaux et mulets", "Méhara", "Méhari", "Méhari (chameau de selle)", "Sur un chameau , puis sur un bœuf porteur", "Chameaux pour le voyage principal, ânes loués pour atteindre la première station", "Chameau. L'auteur avait loué deux chameaux, l'un pour le transport de ses provisions et l'autre pour ses effets personnels", "Chameau. L'auteur mentionne l'utilisation d'une chamelle, ou 'nagah', pour cette partie du voyage", "Chameau pour le voyage principal, mais l'auteur mentionne avoir effectué une excursion à pied jusqu'à un palais de démons", "Chameau pour le voyage principal, mais l'auteur a emprunté un raccourci à pied avec son guide et des esclaves", "Impliqué des chameaux, mais les détails exacts ne sont pas fournis dans la source"
    ]},
    {"type": "Equid", "items": [
        "Cheval", "Cheval pour Rohlfs, tandis que ses serviteurs et ses animaux de bât ont suivi plus lentement",
        "Cheval, bateau", "Chevaux", "Chevaux et chameaux", "Chevaux et mulets", "Chevaux, mulets et chameaux",
        "Chevaux, mulets et un chameau nouvellement loué", "Mulets", "Mulets et ânes", "Mulets, un poney",
        "Mulets, un poney, des ânes", "Trois mules et deux ânes", "Deux ânes", "À cheval", "Âne (pour les bagages), cheval (fourni par le Commandant de Tombouctou)", "À dos d'âne", "Mule, puis à pied, puis à dos d'âne", "Chevaux et mulets. Deux hommes ont été laissés pour s'occuper des chameaux, qui avaient du mal à naviguer sur le terrain difficile", "À cheval", "Initialement à cheval, puis à pied avec des animaux de bât", "À cheval jusqu'au fleuve Mari, puis non spécifié"
    ]},
    {"type": "Train", "items": [
        "Train", "Train (chemin de fer Sénégal-Niger)", "Train express de nuit pour Oran",
        "Train jusqu'à Plymouth, puis navire de transport de troupes Neuralia",
        "Train pour Aïn-Sefra", "Train pour Saïda", "Train vers Alger", "Train, calèche", "Train, diligence", "Train, diligence, à pied", "Chemin de fer de la Sierra Leone", "Chemin de fer"
    ]},
    {"type": "Walking", "items": [
        "Marche", "Marche - en suivant la route Stevenson", "Marche - en suivant le cours du Zitembi",
        "Marche et pirogue", "Marche à pied", "À pied", "Marche à pied (l'auteur ayant suffisamment récupéré pour marcher sur de courtes distances)",
        "Marche à pied au sein d'une caravane", "Marche à pied et à cheval", "À pied, puis sur un bœuf porteur", "À pied en caravane", "À pied, en traversant un bras du fleuve à gué", "Marche à pied [xxxvii]", "À pied avec des porteurs", "À pied et avec des bœufs", "Non spécifié, probablement à pied", "Colonne militaire", "Convoi organisé en hâte", "Hamac (en raison d'une blessure à la jambe)", "Pont de hamac", "Porteurs"
    ]},
    {"type": "Slow ground vehicle", "items": [
        "Bœuf porteur", "Bœufs", "Calèche", "Charrette tirée par des bœufs.", "Chariot tiré par des chevaux, puis à pied.", "Chariot à bœufs", "Diligence", "Diligence, bateau à vapeur", "Diligence, charrette de boucher", "Diligence, à pied", "Véhicule loué, parfois à pied", "Chariot tiré par des chevaux, puis à pied", "Charrette tirée par des bœufs"
    ]}
]

def add_transport_category(data):
    for livre in data:
        for etape in livre['etapes']:
            moyen_transport = etape.get('moyen_transport', '').strip('.').strip()
            category = "Not specified"
            for transport in transport_categories:
                if moyen_transport in transport['items']:
                    category = transport['type']
                    break
            etape['categorie_transport'] = category
    return data

difficulty_categories = [
    {"type": "Climate", "items": [
        "Chaleur", 
        "Chaleur et fatigue extrêmes pendant la traversée du désert, ce qui a nécessité une gestion minutieuse des réserves d'eau et entraîné un inconfort physique",
        "Chaleur excessive, vent d'est désagréable, ânes jetant leurs charges",
        "Chaleur extrême et fatigue lors d'une marche particulièrement difficile jusqu'au puits, car le guide avait sous-estimé la distance ; l'équipe et les chameaux étaient épuisés et ont dû supporter des heures d'exposition au soleil brûlant sans ombre ni pâturage",
        "Chaleur intense",
        "Chaleur intense, fatigue et tempêtes de sable fréquentes tout en traversant la vaste étendue de sable plat du Tanezrouft . Le manque d'ombre et les conditions monotones ont également contribué aux difficultés",
        "Chaleur intense, rues sombres et labyrinthiques, attaque de mendiants",
        "Chaleur intense, sable profond",
        "Chaleur, soif, fatigue due à la marche sur des pierres pointues",
        "Froid intense à l'intérieur des bâtiments, routes en mauvais état",
        "La pluie, le manque de nourriture et les conflits avec les tribus locales (Mazitu)",
        "Orage violent, pluie froide et abondante",
        "Vent contraire",
        "Vent fort lors de la traversée vers Kabogo",
        "Vent fort, températures extrêmes, inquiétudes concernant la sécurité des routes",
        "Vent plus froid, soleil plus chaud, poussière et menace de pluie",
        "Voyage de nuit avec un vent froid",
        "Inondations de la Loire",
        "Voyage difficile en raison des conditions météorologiques et des difficultés à trouver un point d'atterrissage approprié",
        "Certaines routes rendues impraticables par les inondations",
    ]},
    {"type": "Transport", "items": [
        "Conduite imprudente du conducteur de la diligence dans les rues étroites",
        "Douane lente",
        "Départs matinaux en raison des horaires de train",
        "Long trajet en diligence, mendicité agressive dans le quartier de l'Albaicin, manque de librairies bien achalandées",
        "La diligence est bondée en raison des assises",
        "La diligence était bondée",
        "Cheval difficile à contrôler, attaque de mendiants",
        "La diligence était dans un état déplorable et risquait de s'effondrer",
        "La diligence était rudimentaire et le voyage inconfortable, traversant un terrain sablonneux et sujet aux ornières, ce qui obligeait parfois les passagers à descendre et à pousser",
        "Tarifs de diligence et de train déraisonnables",
        "Voyage inconfortable en diligence",
        "L'auteur a trouvé la selle et le harnachement des chevaux indigènes extrêmement inconfortables",
        "La barge s'est échouée dans un cours d'eau peu profond près de Kabara, nécessitant l'aide d'une cinquantaine d'indigènes pour la dégager",
        "La pirogue fuyait considérablement, obligeant deux hommes à écoper en permanence ; l'absence d'auvent a également exposé l'auteur au soleil intense",
        "Le pont de hamac était instable et nécessitait une traversée prudente",
        "Le radeau était instable et sujet aux fuites, ce qui a fait passer l'auteur à travers des « mini-vagues »",
        "Le sentier traversant El Guettera était périlleux, traversant des chemins escarpés et des ravins profonds, ce qui présentait des risques pour les chameaux et les voyageurs",
        "Navigation difficile en raison de bancs de sable, ce qui rend le voyage lent et fastidieux",
        "Navigation difficile la nuit en raison des nombreux bancs de sable du lac, ce qui a obligé le lancement à jeter l'ancre jusqu'à l'aube",
        "Traversée en pirogues inconfortables et instables",
        "Difficultés de transport en raison des chameaux surchargés, du climat chaud et du manque de nourriture",
        "Difficultés de transport en raison des sepoys qui surchargent les animaux, le manque de nourriture et les conditions climatiques difficiles"
    ]},
    {"type": "Fatigue/Illness", "items": [
        "Fièvre",
        "Fièvre, frissons",
        "Fièvre, hippopotames dangereux",
        "Fièvre, moustiques",
        "Maladie, possible empoisonnement",
        "Douleurs dues à la maladie, faiblesse, soif",
        "L'auteur souffrait d'un empoisonnement du sang dû à une blessure à la jambe, ce qui a rendu le voyage extrêmement douloureux sur les routes de montagne accidentées",
        "Difficulté à marcher, fatigue",
        "Fatigue extrême",
        "Fatigue, rhumes fréquents dus aux changements brusques de température",
        "Maux de tête , fatigue due aux ânes jetant leurs charges",
        "Inactivité prolongée rend la marche fatigante",
        "Difficulté à supporter les changements de température, toux , esclave insultant refusant de porter ses bagages"
    ]},
    {"type": "Thirst/Hunger", "items": [
        "Soif",
        "Soif intense, bœufs épuisés, lenteur des progrès, désaccord avec les guides",
        "Soif, incendie dans la plaine",
        "Tentative de vol, soif extrême",
        "L'eau du puits d'Imbelram était extrêmement salée, ce qui la rendait presque imbuvable et causait des maladies à ceux qui la consommaient",
        "Le manque de nourriture, le climat chaud, la pluie et la difficulté de trouver des guides fiables",
        "Le puits de Taoundert était à sec, ce qui a obligé l'expédition à poursuivre sa route vers le puits suivant, In Ouzel, avec des réserves d'eau extrêmement limitées . Deux chameaux transportant de la nourriture et des provisions ont disparu, ce qui a encore aggravé la situation",
        "Manque de nourriture, faim"
    ]},
    {"type": "Nature", "items": [
        "Moustiques, orage, pluie",
        "Rapides, fatigue des pagayeurs",
        "Le désert du Kalahari, la soif, le terrain sablonneux épuisant pour les bœufs, la lenteur des progrès",
        "Le voyage a traversé une région sablonneuse avec une rareté de l'eau",
        "Les sentiers de montagne étaient difficiles à parcourir",
        "Nombreuses rivières à traverser",
        "Panique et destructions causées par un tremblement de terre récent",
        "Passage difficile d'un ravin, fatigue",
        "Perte dans les bois, soif",
        "Pistes inondées, route perdue dans l'oasis, nuit glaciale",
        "Risque de chute en traversant les montagnes, fatigue, traversée dangereuse d'une rivière",
        "Rivages accidentés comme ceux près de Caprera",
        "Tsetse, chaleur intense, terrain accidenté, faim",
        "Traversée d'un bras de rivière profond et à courant rapide",
        "Traversée d'un marigot, rencontre tendue avec des Foulahs le soupçonnant d'être chrétien",
        "Traversée du Bagoé, longue et coûteuse en raison de la quantité de bagages",
        "Chemin difficile avec des pierres calcinées"
    ]},
    {"type": "Humans", "items": [
        "Guide essayant d'extorquer de l'argent",
        "Guide essayant de le dissuader d'aller au comptoir",
        "Le guide a eu du mal à suivre la bonne route à travers le réseau de lacs et de marécages . Les moustiques et les mouches des sables près du ruisseau de Tango-Maré ont provoqué des fièvres chez l'auteur et son équipe",
        "Le guide s'est de nouveau perdu pendant le voyage, ce qui a entraîné des retards et un gaspillage de ressources précieuses dans un environnement désertique impitoyable",
        "Le guide s'est perdu la nuit, les obligeant à faire un détour important et à manquer d'eau, ce qui a mis à rude épreuve l'équipe et les animaux",
        "Difficulté à maintenir les porteurs motivés ; ils devaient recourir à une organisation quotidienne avec des chefs de village pour de nouveaux porteurs à chaque étape",
        "Délais dus à des bancs de sable et à une mutinerie parmi les chauffeurs qui a entraîné des problèmes de moteur et de graves retards",
        "La ville est déserte, la plupart des commerces sont fermés, les habitants campant à l'extérieur",
        "Manque de vêtements, nécessité de demander l'aumône, difficulté à cacher ses notes et ses effets personnels",
        "Rencontre avec le chef rebelle Bonga, menace de vol par les indigènes",
        "Risque de banditisme, car la région entre Ahnet et le puits suivant, El Jibal, est connue pour les rencontres avec des bandits touaregs",
        "Réglementation stricte de quarantaine, problèmes avec les propriétaires de chevaux, inconfort dû à une selle inadaptée",
        "Service lent à l'hôtel",
        "Contrôle douanier à l'entrée de la ville",
        "Difficulté à obtenir des informations fiables sur les bateaux, embarras de mendicité",
        "Le village est désert et en ruines, les habitants campant à l'extérieur",
        "Un mendiant au comportement suspect"
    ]}
]

def add_difficulties_category(data):
    for livre in data:
        for etape in livre['etapes']:
            difficultes_rencontrees = etape.get('difficultés_rencontrées', '').strip('.').strip()
            category = "Not specified"
            for difficulty in difficulty_categories:
                if difficultes_rencontrees in difficulty['items']:
                    category = difficulty['type']
                    break
            etape['categorie_difficulty'] = category
    return data

# Fonction pour extraire les difficultes uniques
def lister_difficultes(fichier_json):
    # Charger le fichier JSON
    with open(fichier_json, 'r', encoding='utf-8') as fichier:
        donnees = json.load(fichier)

    # Initialiser un ensemble pour stocker les moyens de transport uniques
    difficultes = set()

    # Parcourir les données
    for explorateur in donnees:
        if 'etapes' in explorateur:
            for etape in explorateur['etapes']:
                # Ajouter les moyens de transport à l'ensemble
                moyen = etape.get('difficultés_rencontrées', '').strip('.')
                if moyen:
                    difficultes.add(moyen)

    # Retourner les moyens de transport sous forme de liste triée
    return sorted(difficultes)

# Fonction pour extraire les nourritures uniques
def lister_nourritures(fichier_json):
    # Charger le fichier JSON
    with open(fichier_json, 'r', encoding='utf-8') as fichier:
        donnees = json.load(fichier)

    # Initialiser un ensemble pour stocker les moyens de transport uniques
    nourritures = set()

    # Parcourir les données
    for explorateur in donnees:
        if 'etapes' in explorateur:
            for etape in explorateur['etapes']:
                # Ajouter les nourritures à l'ensemble
                moyen = etape.get('nourriture_prise', '').strip('.')
                if moyen:
                    nourritures.add(moyen)

    # Retourner les moyens de transport sous forme de liste triée
    return sorted(nourritures)

def validate_date(date_str):
    """Valide si une date respecte le format %d/%m/%Y ou %Y."""
    try:
        # Vérifie si la date est au format jour/mois/année
        return datetime.strptime(date_str, "%d/%m/%Y")
    except ValueError:
        try:
            # Vérifie si la date est uniquement une année
            year = datetime.strptime(date_str, "%Y").year
            # Retourne le 1er juillet de l'année donnée
            return datetime(year, 7, 1)
        except ValueError:
            # Si aucun format ne fonctionne, retourne une erreur
            return "format date invalide"

def calculate_age(date_of_birth, date_to_calculate):
    """Calcule l'âge en fonction des dates fournies."""
    if isinstance(date_of_birth, str) or isinstance(date_to_calculate, str):
        return "format date invalide"  # Gestion des dates invalides

    age = date_to_calculate.year - date_of_birth.year - \
          ((date_to_calculate.month, date_to_calculate.day) < (date_of_birth.month, date_of_birth.day))
    return age

# Fonction pour calculer la distance totale
def calculer_distance_totale(etapes):
    distance_totale = 0.0
    dernier_point_valide = None  # Pour stocker la dernière étape valide

    for etape in etapes:
        try:
            # Récupérer les coordonnées de l'étape
            lat, lon = etape['latitude'], etape['longitude']
            
            # Vérifier si l'étape est valide
            if lat is not None and lon is not None:
                # Si on a un point valide précédent, calculer la distance
                if dernier_point_valide:
                    distance_totale += geodesic(dernier_point_valide, (lat, lon)).km
                
                # Mettre à jour le dernier point valide
                dernier_point_valide = (lat, lon)
        except KeyError:
            continue  # Ignorer les étapes sans clé 'latitude' ou 'longitude'
    
    return round(distance_totale, 2)

def calculer_duree(etapes_info):
    date_format = "%d/%m/%Y"  # Format des dates JJ/MM/YYYY
    
    # Récupérer les dates d'arrivée et de départ
    date_arrivee = etapes_info.get('date_arrivee')
    date_depart = etapes_info.get('date_depart')
    
    
    
    # Si l'une des dates est manquante, retourner 0
    if not date_arrivee or not date_depart:
        return 0
    
    try:
        # Convertir les dates en objets datetime
        arrivee = datetime.strptime(date_arrivee, date_format)
        depart = datetime.strptime(date_depart, date_format)
        
        # Calculer la différence en jours
        duree = (arrivee - depart).days
        return max(0, duree)  # Retourner 0 si la durée est négative
    except ValueError:
        # Gérer les erreurs de format
        return 0

# Fonction pour obtenir le pays à partir des coordonnées géographiques
def get_country_from_coords(lat, lon):
    if lat is None or lon is None:
        return None
    try:
        url = f'https://api.opencagedata.com/geocode/v1/json?q={lat}+{lon}&key=e43125a0985a4ce392c822eaf2435275'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            components = data['results'][0]['components']
            return components.get('country')
    except Exception as e:
        print(f"Erreur : {e}")
    return None

# Fonction pour ajouter le pays à chaque étape
def add_country_to_steps(json_file, output_file):
    # Charger les données JSON
    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Parcourir chaque entrée et chaque étape
    for entry in data:
        for step in entry.get('etapes', []):
            lat = step.get('latitude')
            lon = step.get('longitude')
            step['pays'] = get_country_from_coords(lat, lon)

    # Sauvegarder les données mises à jour dans un nouveau fichier
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
    print(f"Mise à jour terminée. Fichier sauvegardé sous {output_file}")

def ajouter_images_aux_explorateurs(fichier_explorateurs, fichier_images, fichier_sortie):
    # Charger le fichier explorateurs.json
    with open(fichier_explorateurs, 'r', encoding='utf-8') as f:
        explorateurs_data = json.load(f)

    # Charger le fichier images.json
    with open(fichier_images, 'r', encoding='utf-8') as f:
        images_data = json.load(f)

    # Créer un dictionnaire pour regrouper les images par titre de livre
    images_dict = {}
    for item in images_data:
        titre = item['livre']['titre']
        images_dict[titre] = item['images']

    # Ajouter le bloc "images" à chaque livre dans explorateurs.json
    for explorateur in explorateurs_data:
        livre_titre = explorateur['livre']['titre']

        # Vérifier si des images correspondent au livre
        explorateur['images'] = images_dict.get(livre_titre, [])

    # Sauvegarder le fichier mis à jour
    with open(fichier_sortie, 'w', encoding='utf-8') as f:
        json.dump(explorateurs_data, f, ensure_ascii=False, indent=4)

    print(f"Mise à jour du fichier '{fichier_sortie}' avec les images réussie.")

def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def process_etapes(etapes, date_of_birth):
    categorie_transport_count = {}
    categorie_difficulty_count = {}
    pays_count = {}
    distance_totale = calculer_distance_totale(etapes)
    etapes_null = sum(1 for e in etapes if e.get('latitude') is None or e.get('longitude') is None)

    lieu_depart, date_depart, age_depart = "Not specified", "Not specified", 0
    date_arrivee, age_arrivee = "Not specified", 0

    if etapes:
        first_step = etapes[0]
        lieu_depart = first_step.get('lieu_depart', 'Not specified')
        date_depart = first_step.get('date_depart', 'Not specified')
        date_depart_validated = validate_date(date_depart)
        if date_depart_validated != "format date invalide" and date_of_birth != "format date invalide":
            age_depart = calculate_age(date_of_birth, date_depart_validated)

    if len(etapes) > 1:
        last_step = etapes[-1]
        date_arrivee = last_step.get('date_arrivee', 'Not specified')
        date_arrivee_validated = validate_date(date_arrivee)
        if date_arrivee_validated != "format date invalide" and date_of_birth != "format date invalide":
            age_arrivee = calculate_age(date_of_birth, date_arrivee_validated)

    for etape in etapes:
        transport = etape.get('categorie_transport', 'Unknown')
        if transport != 'Not specified':
            categorie_transport_count[transport] = categorie_transport_count.get(transport, 0) + 1

        difficulty = etape.get('categorie_difficulty', 'Unknown')
        if difficulty != 'Not specified':
            categorie_difficulty_count[difficulty] = categorie_difficulty_count.get(difficulty, 0) + 1

        pays = etape.get('pays', 'Unknown')
        if pays and pays != 'Not specified':
            pays_count[pays] = pays_count.get(pays, 0) + 1

    return {
        'lieu_depart': lieu_depart,
        'date_depart': date_depart,
        'age_depart': age_depart,
        'date_arrivee': date_arrivee,
        'age_arrivee': age_arrivee,
        'distance_totale': distance_totale,
        'etapes_null': etapes_null,
        'categorie_transport_count': categorie_transport_count,
        'categorie_difficulty_count': categorie_difficulty_count,
        'pays_count': pays_count
    }

def create_dataframes(data):
    small_books_data = []
    books_data = []

    for entry in data:
        livre = entry.get('livre', {})
        date_of_birth = validate_date(livre.get('date_naissance_auteur', 'Not specified'))
        annee_livre = livre.get('annee', 'Not specified')
        annee_livre_start = int(str(annee_livre).split('-')[0].strip())
        etapes = entry.get('etapes', [])
        
        etapes_info = process_etapes(etapes, date_of_birth)
        
        small_books_data.append({
            'Author': livre.get('auteur', 'Not specified'),
            'Title': livre.get('titre', 'Not specified') + ' \\cite{' + livre.get('citation', 'Not specified') + '}'
        })

        book_entry = {
            'Title': livre.get('titre', 'Not specified'),
            'Year of the Journey': annee_livre,
            'Start Year': annee_livre_start,
            'Author': livre.get('auteur', 'Not specified'),
            'Date of birth': livre.get('date_naissance_auteur', 'Not specified'),
            'Place of birth': livre.get('lieu_naissance_auteur', 'Not specified'),
            'Date of death': livre.get('date_mort_auteur', 'Not specified'),
            'Place of death': livre.get('lieu_mort_auteur', 'Not specified'),
            'Nationality': livre.get('nationalite_auteur', 'Not specified'),
            'Activities': livre.get('activites_auteur', 'Not specified'),
            'Language': livre.get('langage', 'Not specified'),
            'URL': livre.get('url', 'Not specified'),
            'Citation': livre.get('citation', 'Not specified'),
            'Departure date': etapes_info['date_depart'],
            'Departure Age': etapes_info['age_depart'],
            'Arrival date': etapes_info['date_arrivee'],
            'Arrival Age': etapes_info['age_arrivee'],
            'Travel duration in days': calculer_duree(etapes_info),
            'Money': livre.get('argent', 'Not specified'),
            'Goal': livre.get('objectif', 'Not specified'),
            'Success': livre.get('succes', 'Not specified'),
            'Number of steps': len(etapes),
            'Number of images': len(entry.get('images', [])),
            'Steps with null coordinates in %': round(100 * etapes_info['etapes_null'] / len(etapes), 2) if etapes else 0,
            'Total distance traveled (km)': etapes_info['distance_totale']
        }

        for key, value in etapes_info['categorie_transport_count'].items():
            book_entry[f'Transport_{key}'] = int(value)

        for key, value in etapes_info['categorie_difficulty_count'].items():
            book_entry[f'Difficulty_{key}'] = int(value)

        for key, value in etapes_info['pays_count'].items():
            book_entry[f'Country_{key}'] = int(value)

        books_data.append(book_entry)

    return pd.DataFrame(books_data).sort_values(by='Title'), pd.DataFrame(small_books_data).sort_values(by=['Author', 'Title'])

def export_to_latex(df, title, latex_file):
    with open(latex_file, 'w', encoding='utf-8') as tex_file:
        tex_file.write("\\begin{table}[H]\n")
        tex_file.write("%\\tablesize{\\small}\n")
        tex_file.write("\\caption{"+title+"}\n")
        tex_file.write("%\\isPreprints{\\centering}{} % Only used for preprints\n")
        tex_file.write("\\footnotesize\n")
        tex_file.write("\\begin{tabularx}{\\textwidth}{" + "C" * len(df.columns) + "}\n")
        tex_file.write("\\toprule\n")

        tex_file.write(" & ".join([f"\\textbf{{{col}}}" for col in df.columns]) + "\\\\\n")
        tex_file.write("\\midrule\n")

        for _, row in df.iterrows():
            tex_file.write(" & ".join([str(val) for val in row.values]) + "\\\\\n")

        tex_file.write("\\bottomrule\n")
        tex_file.write("\\end{tabularx}\n")
        tex_file.write("\\end{table}\n")

def perform_pca(df, output_dir="pca_results"):
    import os
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    from sklearn.decomposition import PCA
    from sklearn.preprocessing import StandardScaler

    os.makedirs(output_dir, exist_ok=True)

    # Step 1: Prepare data
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df_numeric = df[numeric_cols].fillna(0)

    # print(f"Columns normalized: {df_numeric.columns.tolist()}")

    # Standardize data
    scaler = StandardScaler()
    data_scaled = scaler.fit_transform(df_numeric)

    # Step 2: Apply PCA
    pca = PCA()
    principal_components = pca.fit_transform(data_scaled)

    # Step 3: Explained variance
    explained_variance = pca.explained_variance_ratio_
    cum_explained_variance = np.cumsum(explained_variance)

    variance_df = pd.DataFrame({
        "Component": [f"PC{i+1}" for i in range(len(explained_variance))],
        "Explained Variance": explained_variance,
        "Cumulative Variance": cum_explained_variance
    })
    variance_df.to_csv(f"{output_dir}/explained_variance.csv", index=False)

    # Step 4: Individuals' coordinates
    individuals_df = pd.DataFrame(
        principal_components, 
        columns=[f"PC{i+1}" for i in range(len(explained_variance))]
    )
    individuals_df.to_csv(f"{output_dir}/individuals_coordinates.csv", index=False)

    # Step 5: Variable contributions (loadings)
    loadings = pca.components_.T
    loadings_df = pd.DataFrame(
        loadings,
        columns=[f"PC{i+1}" for i in range(len(explained_variance))],
        index=numeric_cols
    )
    loadings_df.to_csv(f"{output_dir}/variables_contributions.csv")

    # Step 6: Equations of principal components
    equations = []
    for i in range(len(explained_variance)):
        component_loadings = loadings_df[f"PC{i+1}"]
        equation = f"PC{i+1} = " + " + ".join(
            [f"({coef:.3f})*{var}" for var, coef in component_loadings.items()]
        )
        equations.append(equation)

    # Save equations to a text file
    with open(f"{output_dir}/pca_equations.txt", "w") as eq_file:
        eq_file.write("Equations of Principal Components:\n\n")
        eq_file.write("\n".join(equations))

    # Step 7: Visualizations
    # Explained variance plot
    plt.figure(figsize=(10, 6))
    plt.bar(range(1, len(explained_variance) + 1), explained_variance, alpha=0.7, label='Individual')
    plt.step(range(1, len(cum_explained_variance) + 1), cum_explained_variance, where='mid', label='Cumulative')
    plt.xlabel('Principal Components')
    plt.ylabel('Explained Variance')
    plt.legend()
    plt.title('Explained Variance by Principal Components')
    plt.savefig(f"{output_dir}/explained_variance.png")
    plt.close()

    # Correlation circle plot
    plt.figure(figsize=(10, 8))
    plt.scatter(loadings[:, 0], loadings[:, 1], color='b')
    for i, var in enumerate(numeric_cols):
        plt.text(loadings[i, 0], loadings[i, 1], var, color='red', fontsize=12, ha='center', va='center')
    plt.axhline(0, color='black', linewidth=1)
    plt.axvline(0, color='black', linewidth=1)
    plt.xlabel('PC1')
    plt.ylabel('PC2')
    plt.grid(True)
    plt.savefig(f"{output_dir}/correlation_circle.png")
    plt.close()

    # Step 8: Summary text file
    results_txt = [
        "PCA Results:\n",
        "Explained Variance by Component:\n",
        variance_df.to_string(index=False),
        "\n\nTop Variables Contributing to PC1:\n",
        loadings_df["PC1"].sort_values(ascending=False).head(5).to_string(),
        "\n\nTop Variables Contributing to PC2:\n",
        loadings_df["PC2"].sort_values(ascending=False).head(5).to_string(),
        "\n\nEquations of Principal Components:\n",
        "\n".join(equations)
    ]
    
    with open(f"{output_dir}/pca_summary.txt", "w") as f:
        f.writelines("\n".join(results_txt))

    return individuals_df, loadings_df

def perform_afc(df, output_dir="pca_results"):
    import os
    import pandas as pd
    import matplotlib.pyplot as plt
    import prince

    os.makedirs(output_dir, exist_ok=True)

    # Étape 1 : Préparer les données
    df = df.fillna(0)  # Remplacer les valeurs manquantes par 0

    # Mettre la colonne Author comme index
    df.set_index("Author", inplace=True)

    # Filtrer les colonnes contenant uniquement des entiers
    integer_columns = df.select_dtypes(include=['number']).columns
    df_contingency = df[integer_columns]
    columns_to_remove = ["Steps with null coordinates in %", "Total distance traveled (km)"]
    df_contingency = df_contingency.drop(columns=columns_to_remove, errors='ignore')

    # Ajouter une étape pour agréger par auteurs (si nécessaire)
    df_contingency = aggregate_by_authors(df_contingency)

    # Supprimer les lignes et colonnes contenant uniquement des zéros
    df_contingency = df_contingency.loc[df_contingency.sum(axis=1) > 0]  # Supprimer les lignes nulles
    df_contingency = df_contingency.loc[:, df_contingency.sum(axis=0) > 0]  # Supprimer les colonnes nulles

    # print(f"Columns normalized: {df_contingency.columns.tolist()}")
    
    # Vérifier que la matrice n'est pas vide après filtrage
    if df_contingency.empty:
        raise ValueError("La matrice de contingence est vide après suppression des lignes/colonnes nulles.")

    # Étape 2 : Appliquer l'AFC
    afc = prince.CA(n_components=2)
    afc = afc.fit(df_contingency)

    # Résultats
    row_coords = afc.row_coordinates(df_contingency)
    col_coords = afc.column_coordinates(df_contingency)
    
    # Exporter les équations des dimensions
    equations = []
    for dim in range(col_coords.shape[1]):
        equation = f"Dim{dim+1} = " + " + ".join(
            [f"({coef:.3f})·{var}" for var, coef in zip(col_coords.index, col_coords.iloc[:, dim])]
        )
        equations.append(equation)

    # Écrire les équations dans un fichier
    with open(f"{output_dir}/afc_equations.txt", "w") as f:
        for i, eq in enumerate(equations):
            f.write(f"Equation for Dimension {i+1}:\n{eq}\n\n")

    # Écrire les résultats dans un fichier
    with open(f"{output_dir}/afc_results.txt", "w") as f:
        f.write("Coordonnées des lignes (Rows):\n")
        f.write(row_coords.to_string())
        f.write("\n\nCoordonnées des colonnes (Columns):\n")
        f.write(col_coords.to_string())

    # Visualisation
    plt.figure(figsize=(10, 8))

    # Lignes (individus)
    plt.scatter(row_coords.iloc[:, 0], row_coords.iloc[:, 1], label='Rows', color='blue')
    for i, txt in enumerate(row_coords.index):
        plt.annotate(txt, (row_coords.iloc[i, 0], row_coords.iloc[i, 1]), color='blue', fontsize=8)

    # Colonnes (variables)
    plt.scatter(col_coords.iloc[:, 0], col_coords.iloc[:, 1], label='Columns', color='red')
    for i, txt in enumerate(col_coords.index):
        text_to_display = txt.split('_')[-1]
        plt.annotate(text_to_display, (col_coords.iloc[i, 0], col_coords.iloc[i, 1]), color='red', fontsize=8)

    # Ajouter des axes et une légende
    plt.axhline(0, color='gray', linewidth=0.8, linestyle='--')
    plt.axvline(0, color='gray', linewidth=0.8, linestyle='--')
    plt.title("Correspondence analysis: Representation of rows and columns")
    plt.xlabel("Dimension 1")
    plt.ylabel("Dimension 2")
    plt.legend()
    plt.grid(True)
    plt.savefig(f"{output_dir}/correspondence_analysis.png")
    plt.close()

def perform_dendrogram(df, k=5):
    # Sélection des données numériques et gestion des valeurs manquantes
    df_numeric = df.select_dtypes(include=[np.number])
    df_numeric.fillna(df_numeric.mean(), inplace=True)

    # normalized_columns = df_numeric.columns.tolist()
    # print(f"Columns normalized: {normalized_columns}")

    # Normalisation des données
    scaler = StandardScaler()
    df_scaled = scaler.fit_transform(df_numeric)

    # Clustering hiérarchique
    Z = linkage(df_scaled, method='ward')

    # Affichage du dendrogramme
    plt.figure(figsize=(20, 8))
    dendrogram(Z, labels=df["Title"].apply(shorten_title).values, leaf_rotation=90, leaf_font_size=9, link_color_func=lambda k: "black")
    plt.ylabel("Distance")
    y_cutoff = 12.5
    plt.axhline(y=y_cutoff, color='r', linestyle='--', label=f"Cutoff threshold (y={y_cutoff})")
    plt.legend()
    plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.16)
    plt.savefig(r"C:\xampp\htdocs\explorateurs\Mapping the Past\results\dendrogram_title.png")
    plt.close()

    # Regroupement en clusters
    hierarchical_clusters = fcluster(Z, y_cutoff, criterion='distance')
    df_numeric["Hierarchical_Cluster"] = hierarchical_clusters
    df["Hierarchical_Cluster"] = hierarchical_clusters

    # Sauvegarde des résultats hiérarchiques
    df_numeric.groupby("Hierarchical_Cluster").agg(["mean", "std", "min", "max"]).to_csv(r"C:\xampp\htdocs\explorateurs\Mapping the Past\results\cluster_summary.csv")
    df.to_csv(r"C:\xampp\htdocs\explorateurs\Mapping the Past\results\clusters_filtered.csv", index=False)

    # Analyse k-means
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    df_numeric["KMeans_Cluster"] = kmeans.fit_predict(df_scaled)
    df["KMeans_Cluster"] = df_numeric["KMeans_Cluster"]

    # Sauvegarde des résultats k-means
    df_numeric.groupby("KMeans_Cluster").agg(["mean", "std", "min", "max"]).to_csv(r"C:\xampp\htdocs\explorateurs\Mapping the Past\results\kmeans_summary.csv")
    df.to_csv(r"C:\xampp\htdocs\explorateurs\Mapping the Past\results\clusters_kmeans.csv", index=False)

    # Export des centroïdes (paramètres de la formule) pour K-Means
    num_features = kmeans.cluster_centers_.shape[1]  # Nombre de colonnes utilisées dans KMeans
    feature_names = df_numeric.columns[:num_features]  # Assurer la correspondance des noms de colonnes

    kmeans_coeffs = pd.DataFrame(kmeans.cluster_centers_, columns=feature_names)
    kmeans_coeffs.to_csv(r"C:\xampp\htdocs\explorateurs\Mapping the Past\results\kmeans_coefficients.csv", index=False)

    # Génération du fichier LaTeX avec la formule
    with open(r"C:\xampp\htdocs\explorateurs\Mapping the Past\results\kmeans_formula.tex", "w") as f:
        f.write("\\begin{equation}\n")
        f.write("    \\text{Cluster Center} = ")
        terms = []
        for col, coef in zip(feature_names, kmeans.cluster_centers_.mean(axis=0)):  # Moyenne sur tous les clusters
            terms.append(f"{coef:.3f} \\cdot {col}")
        f.write(" + ".join(terms) + "\n")
        f.write("\\end{equation}\n")

    print("Clustering terminé et fichiers exportés.")

def shorten_title(title):
    words = title.split()
    if len(words) > 3:
        return f"{words[0]}\n {words[1]}\n[...] {words[-1]}"
    return title

def aggregate_by_authors(_df):
    columns_to_min = ['Start Year', 'Departure Age', 'Travel duration in days']
    columns_to_sum = [col for col in _df.columns if col not in columns_to_min]
    agg_dict = {col: 'sum' for col in columns_to_sum}
    for col in columns_to_min:
        agg_dict[col] = 'min'
        
    return _df.groupby("Author").agg(agg_dict)

def prepare_data(df):
    df = df.fillna(0)
    categorical_num_columns = [
        'Departure Age', 'Start Year', 'Number of steps', 'Number of images', 
        'Total distance traveled (km)', 'Travel duration in days'
    ]
    df_selected = df[['Author'] + categorical_num_columns].copy()
    df_selected.set_index("Author", inplace=True)
    df_selected = aggregate_by_authors(df_selected)
    return df_selected, categorical_num_columns

def save_histograms(df, columns, output_dir):
    for col in columns:
        plt.figure(figsize=(8, 5))
        filtered_data = df[df[col] != 0][col]
        sns.histplot(filtered_data, kde=True, bins=40, color='orange')
        plt.xlabel(col, fontsize=20)
        plt.ylabel('Frequency', fontsize=20)
        plt.tick_params(axis='both', labelsize=16)
        plt.tight_layout()
        plt.savefig(f"{output_dir}/distribution_{col.replace(' ', '_').lower()}.png")
        plt.close()

def save_pie_charts(df, columns, output_dir):
    for col in columns:
        if col in df.columns:
            plt.figure(figsize=(8, 8))

            # Filtrer les valeurs dont le label est une chaîne vide
            value_counts = df[col].value_counts()
            filtered_counts = value_counts[value_counts.index != '']

            # Préparer les labels avec des retours à la ligne
            labels = [label.replace(' ', '\n') for label in filtered_counts.index]

            # Création du diagramme en anneau
            filtered_counts.plot.pie(
                labels=labels,
                autopct='%1.1f%%',
                startangle=90,
                wedgeprops={'width': 0.4},
                pctdistance=0.85,
                labeldistance=1.2,
                textprops={'fontsize': 8}
            )

            plt.title(f"Distribution of {col}")
            plt.ylabel('')
            plt.tight_layout()
            plt.savefig(f"{output_dir}/distribution_{col.replace(' ', '_').lower()}.png")
            plt.close()

def save_correlation_heatmap(df, columns, output_dir):
    plt.figure(figsize=(12, 8))
    correlation_matrix = df[columns].corr()
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt='.2f', annot_kws={"size": 16})
    plt.title('Correlation matrix of numerical columns', fontsize=24)
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/correlation_matrix_numerical_columns.png")
    plt.close()

def save_scatter_plots(df, x_col, y_col, output_file):
    if x_col in df.columns and y_col in df.columns:
        df_filtered = df[(df[x_col] != 0) & (df[y_col] != 0)]
        plt.figure(figsize=(8, 5))
        sns.regplot(data=df_filtered, x=x_col, y=y_col, scatter_kws={'alpha': 0.7}, line_kws={'color': 'red'}, ci=None)
        plt.title(f"{y_col} vs {x_col}", fontsize=18)
        plt.xlabel(x_col, fontsize=16)
        plt.ylabel(y_col, fontsize=16)
        plt.tick_params(axis='both', labelsize=14)
        plt.tight_layout()
        plt.savefig(output_file)
        plt.close()

def generate_visualizations(df, output_dir="dir"):
    os.makedirs(output_dir, exist_ok=True)
    
    plt.style.use('seaborn-v0_8-darkgrid')
    sns.set_palette('muted')
    
    df_selected, categorical_num_columns = prepare_data(df)
    
    save_histograms(df_selected, categorical_num_columns, output_dir)
    save_pie_charts(df, ['Nationality', 'Language', 'Activities'], output_dir)
    save_correlation_heatmap(df_selected, categorical_num_columns, output_dir)
    
    save_scatter_plots(df_selected, 'Total distance traveled (km)', 'Travel duration in days', f"{output_dir}/correlation_distance_duration.png")
    save_scatter_plots(df_selected, 'Departure Age', 'Travel duration in days', f"{output_dir}/correlation_departure_age_duration.png")

def create_geojson(json_file):
    geojson = {
        "type": "FeatureCollection",
        "features": []
    }
    num = 0
    for entry in json_file:
        livre = entry.get("livre", {})
        for step in entry.get("etapes", []):
            num = num + 1
            if step["latitude"] is not None and step["longitude"] is not None:
                feature = {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [step["longitude"], step["latitude"]]
                    },
                    "properties": {
                        "num": num,
                        "titre_livre": livre.get("titre", None),
                        "annee": str(livre.get("annee", None)),
                        "auteur": livre.get("auteur", None),
                        "date_naissance_auteur": livre.get("date_naissance_auteur", None),
                        "lieu_naissance_auteur": livre.get("lieu_naissance_auteur", None),
                        "date_mort_auteur": livre.get("date_mort_auteur", None),
                        "lieu_mort_auteur": livre.get("lieu_mort_auteur", None),
                        "nationalite_auteur": livre.get("nationalite_auteur", None),
                        "activites_auteur": livre.get("activites_auteur", None),
                        "objectif": livre.get("objectif", None),
                        "argent": livre.get("argent", None),
                        "succes": livre.get("succes", None),
                        "langage": livre.get("langage", None),
                        "url": livre.get("url", None),
                        "citation": livre.get("citation", None),
                        "lieu_depart": step.get("lieu_depart", None),
                        "description": step.get("description", None),
                        "date_depart": step.get("date_depart", None),
                        "moyen_transport": step.get("moyen_transport", None),
                        "difficultes_rencontrees": step.get("difficultes_rencontrees", None),
                        "nourriture": step.get("nourriture", None),
                        "source": step.get("source", None),
                        "categorie_transport": step.get("categorie_transport", None),
                        "categorie_difficulty": step.get("categorie_difficulty", None),
                        "pays": step.get("pays", None)
                    }
                }
                geojson["features"].append(feature)

    # print(num)
    
    with open(r'C:\Users\jb\Desktop\Travail\Afrique\sig\data\explorateurs.geojson', "w", encoding="utf-8") as f:
        json.dump(geojson, f, ensure_ascii=False, indent=4)

    print("Fichier GeoJSON créé : explorateurs.geojson")

def export_books_to_excel(json_file, excel_file, latex_file):
    data = load_json(json_file)
    df, small_df = create_dataframes(data)
    df.to_excel(excel_file, index=False)
    
    output_dir = r"C:\xampp\htdocs\explorateurs\Mapping the Past\results"
    components_df = perform_pca(df, output_dir=output_dir)
    perform_afc(df)
    generate_visualizations(df, output_dir=output_dir)
    perform_dendrogram(df)
    
    # profile = ProfileReport(df, title="Profil YData")
    # profile.to_file("rapport_ydata.html")
    
    # print(f"Exportation excel terminée : {excel_file}")
    # export_to_latex(small_df, 'Authors and book titles involved in the study.\\label{tab1}', latex_file)
    # print(f"Exportation latex terminée : {latex_file}")
    
    create_geojson(data)

# Exemple d'utilisation
if __name__ == "__main__":
    try:
        opencage_key = 'e43125a0985a4ce392c822eaf2435275'
        filepath = 'explorateurs.json'

        # geolocator, opencage_geocoder = init_geolocators(opencage_key)
        # stats = process_explorateurs(filepath, geolocator, opencage_geocoder)
        
        # json_file = 'explorateurs.json'
        # output_file = 'explorateurs_avec_pays.json'
        # add_country_to_steps(json_file, output_file)
        
        # Placez votre code ici
        export_books_to_excel('explorateurs_updated.json', 'livres_sans_etapes.xlsx', r'C:\xampp\htdocs\explorateurs\Mapping the Past\methods\table_book.tex')
        
        # ajouter_images_aux_explorateurs('explorateurs.json', 'images.json', 'explorateurs_updated.json')
        
        # Exemple d'utilisation avec un fichier JSON
        # with open('explorateurs.json', 'r', encoding='utf-8') as file:
            # data = json.load(file)

        # updated_category_data = add_transport_category(data)
        # updated_data = add_difficulties_category(updated_category_data)

        # with open('explorateurs.json', 'w', encoding='utf-8') as file:
            # json.dump(updated_data, file, ensure_ascii=False, indent=4)
        
        # resultat = lister_nourritures(filepath)
        # with open("fichier.txt", "w", encoding="utf-8") as fichier:
            # for element in resultat:
                # fichier.write(element + "\n")
        
        # print(stats)
        # replace_images_with_urls("https://www.gutenberg.org/cache/epub/73291/pg73291-images.html")
        input("Appuyez sur Entrée pour quitter...")

    except Exception as e:
        print(f"Une erreur est survenue : {e}")
        input("Appuyez sur Entrée pour quitter...")


    
