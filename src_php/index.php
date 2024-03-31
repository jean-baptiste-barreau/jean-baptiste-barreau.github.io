<?php
//https://vreeken.eu/prj/phpBibLib/
require_once 'cv/lib_bibtex/lib_bibtex.inc.php';
require_once 'cv/functions.php';
$jsonString = file_get_contents('cv/cv.json');
$data = json_decode($jsonString, true);

$Site = array();
$Site['bibtex'] = new Bibtex('cv/biblio.bib');
$bb = $Site['bibtex'];

//buttons: https://webdeasy.de/en/top-css-buttons-en/
?>

<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="Curriculum vitae de Jean-Baptiste Barreau">
  <meta name="keywords" content="Jean-Baptiste Barreau, curriculum vitae, 3D, modélisation, modeling, reconstruction, numérisation, digitization, photogrammétrie, photogrammetry, scanner laser, laser scanner, archéologie, archaeology, patrimoine culturel, cultural heritage, réalité virtuelle, RV, virtual reality, VR, réalité étendue, extended reality, XR, histoire, history, patrimoine, anthropologie, anthropology, recherche scientifique, scientific research, cnrs, Php, python">
  <!-- Inclure jQuery depuis le CDN de Google -->
<script src="./jquery.min.js"></script>
  <title>Jean-Baptiste Barreau - curriculum vitae</title>
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css"/>
	<script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
	<link href="https://cdnjs.cloudflare.com/ajax/libs/vis/4.21.0/vis.min.css" rel="stylesheet" type="text/css" />
  <script src="https://cdnjs.cloudflare.com/ajax/libs/vis/4.21.0/vis.min.js"></script>
  <link rel="stylesheet" href="./cv.css?v=37">
  <style type="text/css">
    .vis-item.blue {
	  border-width: 2px;
      border-style: solid;
	  background-color: rgba(0, 127, 255, 0.5);
	  border-color: rgba(0, 127, 255);
	  border-radius: 8px;
	}
	.vis-item.vis-selected.blue {
	  border-width: 2px;
      border-style: solid;
	  background-color: rgba(255, 87, 51, 0.8);
	  border-color: rgba(255, 87, 51);
	  border-radius: 8px;
	}
  </style>
</head>
<body>
  <main>
    <nav class="vertical-menu">
		<!-- <img src="cv/image_menu.jpg" width="100%"> -->
		<?php showMenu($data); ?>
		<center>
		<div class="lang-toggle">
		  <button onclick="switchLanguage('fr')" class="button-89">Français</button>&nbsp;&nbsp;&nbsp;&nbsp;
		  <button onclick="switchLanguage('en')" class="button-89">English</button>
		</div>
		</center>
    </nav>
    <div id="content">
	<section class="profile" id="profile">
	<table style="width: 100%; border-collapse: collapse; border: none;"><tr>
		<td style="border: none; border-right: 2px solid #007fff;">
		<img src="cv/photo_profil_bleue.png" style="width: 150px; object-fit: scale-down;">
		</td><td style="width: 35%; border: none; border-right: 2px solid #007fff;">
		<div class="details">
			<h3 class="no-spacing">Jean-Baptiste Barreau</h3>
			<span class="fr">Docteur-Ingénieur CNRS en développement, production, traitement et analyse de données<br>
			Thématiques de recherche: <b>3D, archéologie et patrimoine culturel</b></span>
			<span class="en">CNRS PhD-Engineer in development, production, data processing and analysis<br>
			Research topics: <b>3D, archaeology and cultural heritage</b></span>
            <a href="mailto:jean-baptiste.barreau@cnrs.fr" class="content-link">jean-baptiste.barreau@cnrs.fr</a><br><a href="mailto:Jean-Baptiste.Barreau@univ-nantes.fr" class="content-link">jean-baptiste.barreau@univ-nantes.fr</a><br>
			<a href="https://www.researchgate.net/profile/Jean_Baptiste_Barreau" target="_blank"><img src="https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/ResearchGate_icon_SVG.svg/2048px-ResearchGate_icon_SVG.svg.png" style="height:40px;"></a>
			<a href="https://www.webofscience.com/wos/author/record/JFA-7608-2023" target="_blank"><img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS_L0tkDZ0LWcnKigTmvdFLjR0kEHc1waiyfA&usqp=CAU" style="height:40px;"></a>
			<a href="https://orcid.org/0000-0002-8640-1053" target="_blank"><img src="https://upload.wikimedia.org/wikipedia/commons/thumb/0/06/ORCID_iD.svg/2048px-ORCID_iD.svg.png" style="height:40px;"></a>
			<a href="https://www.persee.fr/authority/1617254" target="_blank"><img src="https://www.persee.fr/static/persee.png" style="height:40px;"></a><br>
			Maison des Sciences de l'Homme Ange Guépin - UAR3491<br>5 Allée Jacques Berque 44000 Nantes, France
        </div>
		</td><td style="border: none;">
		<img src="cv/bandeau.jpg" style="width: 100%;">
		</td>
    </tr></table>
	</section>
	<?php 
	showEmployment($data);
	showEducations($data);
	showProjects($data);
	showPublications($bb,$data);
	showTeaching($data);
	showStudent($data);
	showSkills($data);
	showReviewing($data);
	showEvents($data);
	showDiffusions($data);
	showAwards($data);
	?>
	</div>
  </main>
  <script src="script_cv.js"></script>
</body>
</html>
