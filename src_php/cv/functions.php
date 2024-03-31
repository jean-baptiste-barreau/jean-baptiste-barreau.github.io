<?php
function showMenu($_data) 
{
	$l_space = "10px";
	foreach ($_data as $tag => $categorie) 
	{
		echo '<span style="margin-bottom: ' . $l_space . ';"><span class="fr" style="text-align: center;"><a href="#' . strtolower($tag) . '" class="button-menu">' . $categorie['nom_fr'] . '</a></span></span>';
		echo '<span style="margin-bottom: ' . $l_space . ';"><span class="en" style="text-align: center;"><a href="#' . strtolower($tag) . '" class="button-menu">' . $categorie['nom_en'] . '</a></span></span>';
	}
}

function showImages($_imagesArray, $_maxHeight) 
{
	if(isset($_imagesArray['images']))
	{
		$l_imagesArray = $_imagesArray['images'];
		$i = 0;
		if($_maxHeight == 0) { echo '<table><tr>'; shuffle($l_imagesArray); }
		foreach ($l_imagesArray as $image) 
		{
			$l_maxHeight = ($_maxHeight > 0) ? 'max-height: 100px;' : '';
			if(($_maxHeight == 0) && (($i % 4) == 0) && ($i > 0) ) { echo '</tr><tr>'; }
			if($_maxHeight == 0) { echo '<td>'; }
			echo '<div class="image-container"><a href="' . $image['url'] .'" target="_blank"><img src="cv/imgs/min/' . $image['img'] . '" class="image-hover-effect" style="max-width: 100%; '.$l_maxHeight.'"/></a></div>';
			if($_maxHeight == 0) { echo '</td>'; }
			$i++;
		}
		if($_maxHeight == 0) { echo '</tr></table>'; }
	}
}

function showEmployment($_data) 
{
	echo '<section class="employments" id="employment"><h2 class="fr">'.  $_data['Employment']['nom_fr'] .'</h2><h2 class="en">'.  $_data['Employment']['nom_en'] .'</h2>';
	$l_timelineData = array();
	foreach ($_data['Employment']['categories'] as $categorie) 
	{
		echo '<div class="nested-list">';
		echo '<center><h3 class="fr">'.  $categorie['nom_fr'] .'</h3><h3 class="en">'.  $categorie['nom_en'] .'</h3></center><ul>';
		foreach ($categorie['periodes'] as $periode) 
		{
			echo '<li>' . $periode['nom'] . '<ul>';
			foreach ($periode['postes'] as $poste) 
			{
				$l_institution_link_fr = ($poste['institution_url'] != '') ? '<a href="' . $poste['institution_url'] .'" target="_blank" class="content-link">' . $poste['institution_fr'] . '</a>' : $poste['institution_fr'];
				echo '<li>';
				echo '<table><tr><td class="first-cell">';
				$l_intitule = '<span class="fr"><b>' .  $poste['intitule_fr'] . '</b>, ' . $l_institution_link_fr;
				$l_intitule .= ($poste['institution_fr'] != '') ? ' / ' : '';
				$l_intitule .= '<a href="' . $poste['lieu_url'] .'" target="_blank" class="content-link">' . $poste['lieu_fr'] . '</a></span>';
				$l_institution_link_en = ($poste['institution_url'] != '') ? '<a href="' . $poste['institution_url'] .'" target="_blank" class="content-link">' . $poste['institution_fr'] . '</a>' : $poste['institution_en'];
				$l_intitule .= '<span class="en"><b>' .  $poste['intitule_en'] . '</b>, ' . $l_institution_link_en;
				$l_intitule .= ($poste['institution_fr'] != '') ? ' / ' : '';
				$l_intitule .= '<a href="' . $poste['lieu_url'] .'" target="_blank" class="content-link">' . $poste['lieu_en'] . '</a></span>';
				echo $l_intitule;
				echo '<ul>';
				foreach ($poste['missions'] as $mission) 
				{
					echo '<li><span class="fr">'.  $mission['intitule_fr'] .'</span><span class="en">'.  $mission['intitule_en'] .'</span></li>';
				}
				echo '</ul>';
				echo '</td><td class="second-cell">';
				showImages($poste, 100);
				echo '</td></tr></table>';
				echo '</li>';
				if(isset($l_timelineData[$periode['nom']]))
				{	
					array_push($l_timelineData[$periode['nom']], $l_intitule);
				}
				else
				{	
					$l_timelineData[$periode['nom']] = array($l_intitule);
				}
			}
			echo '</ul></li>';
		}
		echo '</ul></div>';
	}
	echo showMap($_data,'Employment',array('lieu_fr'));
	echo showTimeline($l_timelineData,'Employment',' - ');
	echo '</section>';
}

function showProjects($_data) 
{
	echo '<section class="projects" id="projects"><h2 class="fr">'.  $_data['Projects']['nom_fr'] .'</h2><h2 class="en">'.  $_data['Projects']['nom_en'] .'</h2>';
	$l_timelineData = array();
	foreach ($_data['Projects']['categories'] as $categorie) 
	{
		echo '<div class="nested-list">';
		echo '<center><h3 class="fr">'.  $categorie['nom_fr'] . ' (' . count($categorie['projets']) . ')</h3><h3 class="en">'.  $categorie['nom_en'] .' (' . count($categorie['projets']) . ')</h3></center><ul>';
		foreach ($categorie['projets'] as $projet) 
		{
			$l_projet_infos_fr = $projet['periode'] . ' | ';
			$l_projet_infos_en = $projet['periode'] . ' | ';
			switch ($projet['statut']) {
				case 'member':
					$l_projet_infos_fr .= 'Membre du ';
					$l_projet_infos_en .= 'Member of the ';
					break;
				case 'coleader':
					$l_projet_infos_fr .= 'Co-responsable du ';
					$l_projet_infos_en .= 'Co-leader of the ';
					break;
				default:
					break;
			}
			$l_projet_name_fr = '<b>' . $projet['nom_fr'] . '</b>';
			$l_intitule_tl_fr = (isset($projet['url'])) ? '<a href="' . $projet['url'] . '" target="_blank" class="content-link">' . $l_projet_name_fr . '</a>' : $l_projet_name_fr;
			$l_projet_infos_fr .= $l_intitule_tl_fr;
			$l_projet_name_en = '<b>' . $projet['nom_en'] . '</b>';
			$l_intitule_tl_en = (isset($projet['url'])) ? '<a href="' . $projet['url'] . '" target="_blank" class="content-link">' . $l_projet_name_en . '</a>' : $l_projet_name_en;
			$l_projet_infos_en .= $l_intitule_tl_en;
			$l_projet_infos_fr .= (isset($projet['manager_fr'])) ? ', géré par <a href="' . $projet['manager_url'] . '" target="_blank" class="content-link">' . $projet['manager_fr'] . '</a>' : '';
			$l_projet_infos_en .= (isset($projet['manager_en'])) ? ', managed by <a href="' . $projet['manager_url'] . '" target="_blank" class="content-link">' . $projet['manager_en'] . '</a>' : '';
			$l_projet_infos_fr .= (isset($projet['funder_fr'])) ? ', financé par ' . $projet['funder_fr'] . '</a>' : '';
			$l_projet_infos_en .= (isset($projet['funder_en'])) ? ', funded by ' . $projet['funder_en'] . '</a>' : '';
			
			$l_projet_infos_fr .= ": " . $projet['desc_fr'];
			$l_projet_infos_en .= ": " . $projet['desc_en'];
			
			$l_projet_infos_fr .= " <i>(";
			$l_projet_infos_en .= " <i>(";
			foreach ($projet['people'] as $people) 
			{
				$l_personne = ($people['number'] > 1) ? "personnes" : "personne";
				$l_projet_infos_fr .= $people['country_fr'] . ': ' . $people['number'] . ' ' . $l_personne . ', ';
				$l_projet_infos_en .= $people['country_en'] . ': ' . $people['number'] . ' people, ';
			}
			$l_projet_infos_fr .= ")</i>";
			$l_projet_infos_en .= ")</i>";
			echo '<li>';
			echo '<table><tr><td class="first-cell">';
			echo '<span class="fr">'. str_replace(', )', ')', $l_projet_infos_fr) . '</span><span class="en">'.  str_replace(', )', ')', $l_projet_infos_en) .'</span>';
			echo '</td><td class="second-cell">';
			showImages($projet, 100);
			echo '</td></tr></table>';
			echo '</li>';
			if(isset($l_timelineData[$projet['periode']]))
			{	
				array_push($l_timelineData[$projet['periode']], '<span class="fr">'. ucfirst($l_intitule_tl_fr) . '</span><span class="en">'. ucfirst($l_intitule_tl_en) . '</span>');
			}
			else
			{	
				$l_timelineData[$projet['periode']] = array('<span class="fr">'. ucfirst($l_intitule_tl_fr) . '</span><span class="en">'. ucfirst($l_intitule_tl_en) . '</span>');
			}
		}
		echo '</ul></div>';
	}
	echo showTimeline($l_timelineData,'Projects',' - ');
	echo '</section>';
}

function getReferencesCount($_bb, $_data) 
{
	$l_result = $_bb->Select(array('author' => 'barreau', 'type' => 'article'))+$_bb->Select(array('author' => 'barreau', 'type' => 'Inbook'))+$_bb->Select(array('author' => 'barreau', 'type' => 'inproceedings'))+$_bb->Select(array('author' => 'barreau', 'type' => 'incollection'))+$_bb->Select(array('author' => 'barreau', 'type' => 'poster'))+$_bb->Select(array('author' => 'barreau', 'type' => 'Misc'));
	return $l_result;
}

function showPublications($_bb, $_data) 
{
	echo '<section class="publications" id="publications"><h2 class="fr">'.  $_data['Publications']['nom_fr'] .'</h2><h2 class="en">'.  $_data['Publications']['nom_en'] .'</h2>';
	echo '<div class="tabs">';
	$i = 1;
	foreach ($_data['Publications']['onglets'] as $onglet)
	{
		echo '<div class="tab" onclick="showTab(' . $i . ')"><span class="fr">' . $onglet['nom_fr'] . '</span><span class="en">' . $onglet['nom_en'] . '</span></div>';
		$i++;
	}
    echo '</div>';
	echo '<div class="tab-content" id="tab1">';
	echo '<script>function toggleText(id) {
				  var textElement = document.getElementById(\'abstract-\' + id);
				  var buttonElement = document.getElementById(\'button-\' + id);
				  if (textElement.style.display === \'none\') {
					textElement.style.display = \'block\';
					buttonElement.innerText = \'-\';
				  } else {
					textElement.style.display = \'none\';
					buttonElement.innerText = \'+\';
				  }
				}</script>';
	echo '<center><h3 class="fr">' . getReferencesCount($_bb, $_data) . ' références / ' . count(showCoauthorsArray($_bb)) . ' coauteurs</h3><h3 class="en">' . getReferencesCount($_bb, $_data) . ' references / ' . count(showCoauthorsArray($_bb)) . ' co-authors</h3></center>';
	showPublicationsCategory($_bb,'Articles de journaux','Journal Articles','article');
	showPublicationsCategory($_bb,'Chapitres de livre','Book Chapters','Inbook');
	showPublicationsCategory($_bb,'Actes de colloque','Conference Proceedings','inproceedings');
	showPublicationsCategory($_bb,'Rapports','Reports','incollection');
	showPublicationsCategory($_bb,'Posters','Posters','poster');
	showPublicationsCategory($_bb,'Articles de magazine','Magazine articles','Misc');
	showIllustrations($_data);
	echo '</div>';
	echo '<div class="tab-content" id="tab2"><br>';
	showImages($_data['Publications'],0);
	echo '</div>';
	echo '<script src="./tab_cv.js"></script>';
	echo showPublicationsMap($_bb, $_data);
	echo showTimeline(getArticlesDates($_bb, $_data),"Publications",",");
	echo '</section>';
}

function showPublicationsCategory($_bb,$_frenchTitle,$_englishTitle,$_type) 
{
	$_bb->ResetBibliography();
	$_bb->SetBibliographyStyle('numeric');
	$_bb->SetBibliographyOrder(array('year' => 'd', 'author' => 'a', 'title' => 'a'));
	$l_count = $_bb->Select(array('author' => 'barreau', 'type' => $_type));
	echo '<center><h3 class="fr">' . $_frenchTitle . ' (' . $l_count . ')</h3><h3 class="en">' . $_englishTitle . ' (' . $l_count . ")</h3></center>";
	$_bb->PrintBibliography(); 
}

function showCoauthorsArray($_bb) 
{
	$_bb->ResetBibliography();
	$_bb->SetBibliographyStyle('numeric');
	$_bb->SetBibliographyOrder(array('year' => 'd', 'author' => 'a', 'title' => 'a'));
	$_bb->Select(array('author' => 'barreau'));
	$l_coauthors = array();
	foreach($_bb->used as $key => $info)
	{
		if($info['ref'] === false)
			continue;
		$entry = isset($info['entry']) ? $info['entry'] : $_bb->GetEntry($key);
		foreach(explode(" and ", $entry['author']) as $l_author)
		{
			if(isset($l_coauthors[$l_author]))
			{	
				$l_coauthors[$l_author] += 1;
			}
			else
			{	
				$l_coauthors[$l_author] = 1;
			}
		}
	}
	arsort($l_coauthors);
	unset($l_coauthors["Barreau, J.B."]);
	
	return $l_coauthors;
}

function getArticlesCoords($_bb, $_data) 
{
	$_bb->ResetBibliography();
	$_bb->SetBibliographyStyle('numeric');
	$_bb->SetBibliographyOrder(array('year' => 'd'));
	$_bb->Select(array('author' => 'barreau'));
	$l_ArticlesCoords = array();
	foreach($_bb->used as $key => $info)
	{
		if($info['ref'] === false)
			continue;
		$entry = isset($info['entry']) ? $info['entry'] : $_bb->GetEntry($key);
		if(isset($entry['address']))
		{
			foreach(explode("; ", $entry['address']) as $l_coord)
			{
				if(verifierCoordonnees($l_coord))
				{
					$l_title = strip_tags($_bb->refPrinter->BibliographyEntryStr($entry, $_bb->used[$key]));
					$l_title = str_replace(array("\r", "\n"), '', $l_title);
					$l_title = preg_replace('/\[\d+\]\s*/', '', $l_title);
					$l_title = str_replace('Barreau, J.B.', '<b>Barreau, J.B.</b>', $l_title);
					if(isset($entry['url']))
					{	
						$l_title = str_replace($entry['title'], '<a href=\"' . $entry['url'] . '\" target=\"_blank\">' . $entry['title'] . '</a>', $l_title);
					}

					if(isset($l_ArticlesCoords[$l_coord]))
					{	
						array_push($l_ArticlesCoords[$l_coord], $l_title);
					}
					else
					{	
						$l_ArticlesCoords[$l_coord] = array($l_title);
					}
				}
			}
		}
	}
	
	getIllustrationsData($_data, "coord_geo", $l_ArticlesCoords);
	
	return $l_ArticlesCoords;
}

function getArticlesDates($_bb, $_data) 
{
	$_bb->ResetBibliography();
	$_bb->SetBibliographyStyle('numeric');
	$_bb->SetBibliographyOrder(array('year' => 'd'));
	$_bb->Select(array('author' => 'barreau'));
	$l_ArticlesDates = array();
	foreach($_bb->used as $key => $info)
	{
		if($info['ref'] === false)
			continue;
		$entry = isset($info['entry']) ? $info['entry'] : $_bb->GetEntry($key);
		if(isset($entry['x-localreference']))
		{
			foreach(explode("; ", $entry['x-localreference']) as $l_dates)
			{
				$l_title = strip_tags($_bb->refPrinter->BibliographyEntryStr($entry, $_bb->used[$key]));
				$l_title = str_replace(array("\r", "\n"), '', $l_title);
				$l_title = preg_replace('/\[\d+\]\s*/', '', $l_title);
				$l_title = str_replace('Barreau, J.B.', '<b>Barreau, J.B.</b>', $l_title);
				if(isset($entry['url']))
				{	
					$l_title = str_replace($entry['title'], '<a href=\"' . $entry['url'] . '\" target=\"_blank\">' . $entry['title'] . '</a>', $l_title);
				}

				if(isset($l_ArticlesDates[$l_dates]))
				{	
					array_push($l_ArticlesDates[$l_dates], $l_title);
				}
				else
				{	
					$l_ArticlesDates[$l_dates] = array($l_title);
				}
			}
		}
	}
	
	getIllustrationsData($_data, "dates", $l_ArticlesDates);
	
	return $l_ArticlesDates;
}

function getIllustrationsData($_data, $_field, array &$_array)
{
	foreach($_data["Publications"]["categories_autres"]["illustrations"] as $value)
	{
		if(isset($value[$_field]))
		{
			preg_match('/<a.*?>(.*?)<\/a>/', $value["article"], $matches);
			$l_title = (isset($matches[1])) ? $matches[1] : '';
			
			preg_match('/^(.*?)<a\s+href/s', $value["article"], $matches);
			$l_authors = (isset($matches[1])) ? $matches[1] : '';
			
			preg_match('/<a\s+href="([^"]*)"/', $value["article"], $matches);
			$l_lien = (isset($matches[1])) ? $matches[1] : '';
			
			preg_match('/<\/i>(.*)/', $value["article"], $matches);
			$l_infos = (isset($matches[1])) ? $matches[1] : '';
			
			$l_text = str_replace('<i>','',$l_authors) . ' ' . str_replace($l_title, '<a href=\"' . $l_lien . '\" target=\"_blank\">' . $l_title . '</a>', $l_title) . ' ' . $l_infos;
			
			if(isset($_array[$value[$_field]]))
			{	
				array_push($_array[$value[$_field]], $l_text);
			}
			else
			{	
				$_array[$value[$_field]] = array($l_text);
			}
		}
	}
}

function verifierCoordonnees($chaine) 
{
    $regex = '/^[-+]?([1-8]?\d(\.\d+)?|90(\.0+)?),\s*[-+]?(180(\.0+)?|((1[0-7]\d)|([1-9]?\d))(\.\d+)?)$/';
    if (preg_match($regex, $chaine)) 
	{
        return true;
    } 
	else 
	{
        return false;
    }
}

function showIllustrations($_data) 
{
	echo '<center><h3 class="fr">'.  $_data['Publications']['categories_autres']['nom_fr'] .' (' . count($_data['Publications']['categories_autres']['illustrations']) . ')</h3><h3 class="en">'.  $_data['Publications']['categories_autres']['nom_en'] .' (' . count($_data['Publications']['categories_autres']['illustrations']) . ')</h3></center><table class="bibtex-biblio">';
	$i = 1;
	foreach ($_data['Publications']['categories_autres']['illustrations'] as $illustration) 
	{
		$l_illustration_infos = '<tr id="cnpao2014" class="bibtex-entry bibtex-numeric">
		<td class="bibtex-reference bibtex-numeric"><span class="bibtex-list bibtex-numeric"><span class="bibtex-list-start">[</span><span class="bibtex-ref bibtex-key-cnpao2014">' . $i . '</span><span class="bibtex-list-end">]</span></span></td>
		<td class="bibtex-citation"><span class="bibtex-misc">' . $illustration['article'] . '</span></td>
	</tr>';
		echo str_replace(', )', ')', $l_illustration_infos);
		$i++;
	}
	echo '</tbody></table>';
}

function showTeaching($_data) 
{
	echo '<section class="teaching" id="teaching"><h2 class="fr">'.  $_data['Teaching']['nom_fr'] .'</h2><h2 class="en">'.  $_data['Teaching']['nom_en'] .'</h2>';
	$l_timelineData = array();
	foreach ($_data['Teaching']['categories'] as $categorie) 
	{
		echo '<div class="nested-list">';
		echo '<center><h3 class="fr">'.  $categorie['nom_fr'] . ' (' . count($categorie['cours']) . ')</h3><h3 class="en">'.  $categorie['nom_en'] .' (' . count($categorie['cours']) . ')</h3></center><ul>';
		foreach ($categorie['cours'] as $cours) 
		{
			$l_teaching_infos_fr = $cours['periode'] . ' | ';
			$l_teaching_infos_en = $cours['periode'] . ' | ';
			$l_teaching_infos_fr .= '<b>' . $cours['statut_fr'] . '</b>';
			$l_teaching_infos_en .= '<b>' . $cours['statut_en'] . '</b>';
			$l_teaching_infos_fr .= ', <i><a href="' . $cours['school_url'] . '" target="_blank" class="content-link">' . $cours['school_fr'] . '</a></i>';
			$l_teaching_infos_en .= ', <i><a href="' . $cours['school_url'] . '" target="_blank" class="content-link">' . $cours['school_en'] . '</a></i>';
			$l_teaching_infos_fr .= ', <a href="' . $cours['intitule_url'] . '" target="_blank" class="content-link">' . $cours['intitule_fr'] . '</a>';
			$l_teaching_infos_en .= ', <a href="' . $cours['intitule_url'] . '" target="_blank" class="content-link">' . $cours['intitule_en'] . '</a>';
			$l_teaching_infos_fr .= ': ' . $cours['desc_fr'];
			$l_teaching_infos_en .= ': ' . $cours['desc_en'];
			$l_teaching_infos_fr .= ' (' . $cours['nbre_heures'] . 'h)';
			$l_teaching_infos_en .= ' (' . $cours['nbre_heures'] . 'h)';
			echo '<li>';
			echo '<table><tr><td class="first-cell">';
			echo '<span class="fr">'.  str_replace(', )', ')', $l_teaching_infos_fr) .'</span><span class="en">'.  str_replace(', )', ')', $l_teaching_infos_en) .'</span>';
			echo '</td><td class="second-cell">';
			showImages($cours,100);
			echo '</td></tr></table>';
			echo '</li>';
			
			$l_tl_periodes = explode(", ", $cours['periode']);
			foreach ($l_tl_periodes as $periode) 
			{
				$l_periode = preg_replace('/\d{2}\/|\/\d{2}/', '', $periode);
				if (preg_match('/^\d{4}$/', $l_periode)) 
				{
					$l_periode = $l_periode . " - " . ($l_periode+1);
				}
				else
				{
					preg_match('/(\d{4}) - (\d{4})/', $l_periode, $matches);
					$debut = intval($matches[1]);
					$fin = intval($matches[2]);
					if($debut == $fin)
					{
						$l_periode = sprintf("%04d - %04d", $debut, $fin+1);
					}
				}
				$l_intitule = '<span class="fr">'.  str_replace(', )', ')', substr($l_teaching_infos_fr, strpos($l_teaching_infos_fr, "<b>"))) .'</span><span class="en">'. str_replace(', )', ')', substr($l_teaching_infos_en, strpos($l_teaching_infos_en, "<b>"))) .'</span>';
				if(isset($l_timelineData[$l_periode]))
				{	
					array_push($l_timelineData[$l_periode], $l_intitule);
				}
				else
				{	
					$l_timelineData[$l_periode] = array($l_intitule);
				}
				
			}
		}
		echo '</ul></div>';
	}
	echo showMap($_data,'Teaching',array('school_fr'));
	echo showTimeline($l_timelineData,'Teaching',' - ');
	echo '</section>';
}

function showStudent($_data) 
{
	echo '<section class="student" id="students"><h2 class="fr">'.  $_data['Students']['nom_fr'] .'</h2><h2 class="en">'.  $_data['Students']['nom_en'] .'</h2>';
	$l_timelineData = array();
	foreach ($_data['Students']['categories'] as $categorie) 
	{
		echo '<div class="nested-list">';
		echo '<center><h3 class="fr">'.  $categorie['nom_fr'] . ' (' . count($categorie['student']) . ')</h3><h3 class="en">'.  $categorie['nom_en'] .' (' . count($categorie['student']) . ')</h3></center><ul>';
		foreach ($categorie['student'] as $student) 
		{
			$l_student_infos_fr = $student['periode'] . ' | ';
			$l_student_infos_en = $student['periode'] . ' | ';
			$l_student_infos_fr .= $student['nom'] . ' (';
			$l_student_infos_en .= $student['nom'] . ' (';
			$l_student_infos_fr .= '<a href="' . $student['diplome_url'] . '" target="_blank" class="content-link">' . $student['diplome_fr'] . '</a>), ';
			$l_student_infos_en .= '<a href="' . $student['diplome_url'] . '" target="_blank" class="content-link">' . $student['diplome_en'] . '</a>), ';
			$l_student_infos_fr .= '<i>' . $student['titre'] . '</i>. Direction: ';
			$l_student_infos_en .= '<i>' . $student['titre'] . '</i>. Direction: ';
			foreach ($student['direction'] as $direction) 
			{
				$l_student_infos_fr .= $direction['nom'] . ', ';
				$l_student_infos_en .= $direction['nom'] . ', ';
			}
			$l_student_infos_fr .= '.';
			$l_student_infos_en .= '.';
			if(isset($student['supervision']))
			{
				$l_student_infos_fr .= ' / Supervision: ';
				$l_student_infos_en .= ' / Supervision: ';
				foreach ($student['supervision'] as $supervision) 
				{
					$l_student_infos_fr .= $supervision['nom'] . ', ';
					$l_student_infos_en .= $supervision['nom'] . ', ';
				}
			}
			$l_student_infos_fr .= '.';
			$l_student_infos_en .= '.';
			$l_student_infos_fr = rtrim(str_replace(array(', )', ', /', ', .', 'BARREAU Jean-Baptiste'), array(')', ' /', '', '<b>BARREAU Jean-Baptiste</b>'), $l_student_infos_fr), '.');
			$l_student_infos_en = rtrim(str_replace(array(', )', ', /', ', .', 'BARREAU Jean-Baptiste'), array(')', ' /', '', '<b>BARREAU Jean-Baptiste</b>'), $l_student_infos_en), '.');
			echo '<li>';
			echo '<table><tr><td class="first-cell">';
			echo '<span class="fr">'.  $l_student_infos_fr .'</span><span class="en">'.  $l_student_infos_en .'</span>';
			echo '</td><td class="second-cell">';
			showImages($student,100);
			echo '</td></tr></table>';
			echo '</li>';
			
			$l_periode = $student['periode'];
			if (preg_match('/^\d{4}$/', $l_periode)) 
			{
				$l_periode = $l_periode . " - " . ($l_periode+1);
			}
			$l_intitule = '<span class="fr">'.  substr($l_student_infos_fr, strpos($l_student_infos_fr, " | ")+3) .'</span><span class="en">'.  substr($l_student_infos_en, strpos($l_student_infos_en, " | ")+3) .'</span>';
			if(isset($l_timelineData[$l_periode]))
			{	
				array_push($l_timelineData[$l_periode], $l_intitule);
			}
			else
			{
				$l_timelineData[$l_periode] = array($l_intitule);
			}
			
		}
		echo '</ul></div>';
	}
	echo showMap($_data,'Students',array('diplome_fr'));
	echo showTimeline($l_timelineData,'Students',' - ');
	echo '</section>';
}

function showSkills($_data) 
{
	echo '<section class="skills" id="skills"><h2 class="fr">'.  $_data['Skills']['nom_fr'] .'</h2><h2 class="en">'.  $_data['Skills']['nom_en'] .'</h2>';
	foreach ($_data['Skills']['skill_cat'] as $skill_cat) 
	{
		echo '<div class="nested-list">';
		$l_skill_infos_fr = '<b><u>' . $skill_cat['skill_cat_fr'] . ' (' . count($skill_cat['skill']) . ')</u></b>: ';
		$l_skill_infos_en = '<b><u>' . $skill_cat['skill_cat_en'] . ' (' . count($skill_cat['skill']) . ')</u></b>: ';
		foreach ($skill_cat['skill'] as $skill) 
		{
			$l_skill_infos_fr .= $skill['name_fr'] . ' | ';
			$l_skill_infos_en .= $skill['name_en'] . ' | ';
			
		}
		echo '<span class="fr">'.  $l_skill_infos_fr .'</span><span class="en">'.  $l_skill_infos_en .'</span>';
		echo '</div>';
	}
	echo '</section>';
}

function showReviewing($_data) 
{
	echo '<section class="reviewing" id="reviewing"><h2 class="fr">'.  $_data['Reviewing']['nom_fr'] .'</h2><h2 class="en">'.  $_data['Reviewing']['nom_en'] .'</h2>';
	foreach ($_data['Reviewing']['reviews'] as $review) 
	{
		echo '<div class="nested-list">';
		$l_reviewing_infos_fr = $review['periode'] . ' | ';
		$l_reviewing_infos_en = $review['periode'] . ' | ';
		$l_reviewing_infos_fr .= '<a href="' . $review['journal_url'] . '" target="_blank" class="content-link">' . $review['journal'] . '</a>';
		$l_reviewing_infos_en .= '<a href="' . $review['journal_url'] . '" target="_blank" class="content-link">' . $review['journal'] . '</a>';
		echo '<table><tr><td class="first-cell">';
		echo '<span class="fr">'.  $l_reviewing_infos_fr .'</span><span class="en">'.  $l_reviewing_infos_en .'</span>';
		echo '</td><td class="second-cell">';
		showImages($review,100);
		echo '</td></tr></table>';
		echo '</div>';
	}
	echo '</section>';
}

function showEvents($_data) 
{
	echo '<section class="event" id="events"><h2 class="fr">'.  $_data['Events']['nom_fr'] .'</h2><h2 class="en">'.  $_data['Events']['nom_en'] .'</h2>';
	foreach ($_data['Events']['event'] as $event) 
	{
		echo '<div class="nested-list">';
		$l_event_infos_fr = $event['periode'] . ' | ';
		$l_event_infos_en = $event['periode'] . ' | ';
		$l_event_infos_fr .= '<a href="' . $event['url'] . '" target="_blank" class="content-link">' . $event['intitule_fr'] . '</a>';
		$l_event_infos_en .= '<a href="' . $event['url'] . '" target="_blank" class="content-link">' . $event['intitule_en'] . '</a>';
		echo '<table><tr><td class="first-cell">';
		echo '<span class="fr">'.  $l_event_infos_fr .'</span><span class="en">'.  $l_event_infos_en .'</span>';
		echo '</td><td class="second-cell">';
		showImages($event,100);
		echo '</td></tr></table>';
		echo '</div>';
	}
	echo '</section>';
}

function showAwards($_data) 
{
	echo '<section class="awards" id="awards"><h2 class="fr">'.  $_data['Awards']['nom_fr'] .'</h2><h2 class="en">'.  $_data['Awards']['nom_en'] .'</h2>';
	foreach ($_data['Awards']['award'] as $award) 
	{
		echo '<div class="nested-list">';
		$l_award_infos_fr = $award['periode'] . ' | ';
		$l_award_infos_en = $award['periode'] . ' | ';
		$l_award_infos_fr .= '<a href="' . $award['url'] . '" target="_blank" class="content-link">' . $award['intitule_fr'] . '</a>, ' . $award['lieu_fr'];
		$l_award_infos_en .= '<a href="' . $award['url'] . '" target="_blank" class="content-link">' . $award['intitule_en'] . '</a>, ' . $award['lieu_en'];
		echo '<table><tr><td class="first-cell"><li>';
		echo '<span class="fr">'.  $l_award_infos_fr .'</span><span class="en">'.  $l_award_infos_en .'</span>';
		echo '</td><td class="second-cell">';
		showImages($award,100);
		echo '</td></tr></table>';
		echo '</div>';
	}
	echo '</section>';
}

function showDiffusions($_data) 
{
	echo '<section class="diffusion" id="diffusions"><h2 class="fr">'.  $_data['Diffusions']['nom_fr'] .'</h2><h2 class="en">'.  $_data['Diffusions']['nom_en'] .'</h2>';
	foreach ($_data['Diffusions']['categories'] as $categorie) 
	{
		echo '<div class="nested-list">';
		echo '<center><h3 class="fr">'.  $categorie['nom_fr'] . ' (' . count($categorie['diffusion']) . ')</h3><h3 class="en">'.  $categorie['nom_en'] .' (' . count($categorie['diffusion']) . ')</h3></center><ul>';
		foreach ($categorie['diffusion'] as $diffusion) 
		{
			$l_diffusion_infos_fr = $diffusion['periode'] . ' | ';
			$l_diffusion_infos_en = $diffusion['periode'] . ' | ';
			$l_diffusion_infos_fr .= '<a href="' . $diffusion['url'] . '" target="_blank" class="content-link">' . $diffusion['intitule_fr'] . '</a>';
			$l_diffusion_infos_en .= '<a href="' . $diffusion['url'] . '" target="_blank" class="content-link">' . $diffusion['intitule_en'] . '</a>';
			echo '<table><tr><td class="first-cell"><li>';
			echo '<span class="fr">'.  $l_diffusion_infos_fr .'</span><span class="en">'.  $l_diffusion_infos_en .'</span>';
			echo '</td><td class="second-cell">';
			showImages($diffusion,100);
			echo '</td></tr></table>';
			echo '</li>';
		}
		echo '</ul></div>';
	}
	echo '</section>';
}

function showEducations($_data) 
{
	echo '<section class="education" id="educations"><h2 class="fr">'.  $_data['Educations']['nom_fr'] .'</h2><h2 class="en">'.  $_data['Educations']['nom_en'] .'</h2>';
	$l_timelineData = array();
	foreach ($_data['Educations']['categories'] as $categorie) 
	{
		echo '<div class="nested-list">';
		echo '<center><h3 class="fr">'.  $categorie['nom_fr'] . ' (' . count($categorie['education']) . ')</h3><h3 class="en">'.  $categorie['nom_en'] .' (' . count($categorie['education']) . ')</h3></center><ul>';
		foreach ($categorie['education'] as $education) 
		{
			$l_education_infos_fr = $education['periode'] . ' | ';
			$l_education_infos_en = $education['periode'] . ' | ';
			$l_education_infos_fr .= '<a href="' . $education['url'] . '" target="_blank" class="content-link">' . $education['intitule_fr'] . '</a>';
			$l_education_infos_en .= '<a href="' . $education['url'] . '" target="_blank" class="content-link">' . $education['intitule_en'] . '</a>';
			$l_education_infos_fr .= str_replace(array('<link>','</link>'),array('<a href="' . $education['info_url'] . '" target="_blank" class="content-link">','</a>'),$education['info_fr']);
			$l_education_infos_en .= str_replace(array('<link>','</link>'),array('<a href="' . $education['info_url'] . '" target="_blank" class="content-link">','</a>'),$education['info_en']);
			echo '<table><tr><td class="first-cell"><li>';
			echo '<span class="fr">'.  $l_education_infos_fr .'</span><span class="en">'.  $l_education_infos_en .'</span>';
			echo '</td><td class="second-cell">';
			showImages($education,100);
			echo '</td></tr></table>';
			echo '</li>';
			if(isset($l_timelineData[$education['periode']]))
			{	
				array_push($l_timelineData[$education['periode']], '<span class="fr">'.  $l_education_infos_fr .'</span><span class="en">'.  $l_education_infos_en .'</span>');
			}
			else
			{	
				$l_timelineData[$education['periode']] = array('<span class="fr">'.  $l_education_infos_fr .'</span><span class="en">'.  $l_education_infos_en .'</span>');
			}
		}
		echo '</ul></div>';
	}
	echo showMap($_data,'Educations',array('intitule_fr'));
	//print_r($l_timelineData);
	echo showTimeline($l_timelineData,'Educations',' - ');
	echo '</section>';
}

$g_MapLayer = "L.tileLayer('http://tile.thunderforest.com/landscape/{z}/{x}/{y}.png?apikey=72c10d6d09604887a954ad8b7e9a8162', {attribution: ''});";
//$g_MarkerIcon = "L.icon({iconUrl: 'cv/imgs/min/marker.png', iconSize: [10, 20], iconAnchor: [5, 10], popupAnchor: [0, 0]});";
$l_rayon = 6;
$l_stroke_width = 1;
$l_fill_opacity = 0.8;
$l_fill_color = "#FF5733";
$l_stroke_color = "#000000";
$g_MarkerIcon = "L.divIcon({
    className: 'circle-icon',
    html: '<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"" . 2*$l_rayon . "\" height=\"" . 2*$l_rayon . "\"><circle cx=\"" . $l_rayon . "\" cy=\"" . $l_rayon . "\" r=\"" . ($l_rayon-$l_stroke_width+1) . "\" fill=\"" . $l_fill_color . "\" fill-opacity=\"" . $l_fill_opacity . "\"/></svg>'
});";

function showPublicationsMap($_bb, $_data) 
{
	$l_result = "";
	$l_result .= '<br><center><div id="mapPublications" style="width: 100%; height: 400px;"></div></center>
	<script type="text/javascript">';
	$l_result .= "var mapPublications = L.map('mapPublications').setView([43.46728568599081, 12.335241045245624], 4);";
	global $g_MapLayer, $g_MarkerIcon;
	$l_result .= "var mapLayer = " . $g_MapLayer;
	$l_result .= "mapLayer.addTo(mapPublications);";
	$l_result .= "var layerGroupPublications = L.featureGroup().addTo(mapPublications);";
	$l_result .= "var customIconPublications = " . $g_MarkerIcon;
	foreach(getArticlesCoords($_bb, $_data) as $CoordGeo => $TitleArray) 
	{
		if(isset($CoordGeo))
		{
			$l_result .= "var markerPublications = L.marker([" . $CoordGeo . "], {icon: customIconPublications}).addTo(mapPublications);";
			$l_result .= 'var popup = L.popup().setContent("<div>'.getPopupTitle($TitleArray).'</div>");';
			$l_result .= 'popup.options.maxWidth = "800";';
			$l_result .= 'markerPublications.bindPopup(popup);';
			$l_result .= 'layerGroupPublications.addLayer(markerPublications);';
		}	
	}
	
	$l_result .= "mapPublications.fitBounds(layerGroupPublications.getBounds());";
	$l_result .= "</script>";
	return $l_result;
}

function getPopupTitle($_TitleArray)
{
	$l_text = "<ol>";
	foreach($_TitleArray as $Title) 
	{
		$Title = str_replace('+', '', $Title);
		$position = strpos($Title, "Résumé:");
		if ($position !== false) 
		{
			$Title = substr($Title, 0, $position + strlen("Résumé:"));
		}
		$l_text .= '<li>' . str_replace('Résumé:', '', $Title) . '</li>';
	}
	$l_text .= "</ol>";
	return $l_text;
}

function showMap($_data, $_Rubrique, $_PopupTitles) 
{
	$l_result = "";
	$l_result .= '<br><center><div id="map' . $_Rubrique . '" style="width: 60%; height: 400px;"></div></center>
	<script type="text/javascript">';
	$l_result .= "var map" . $_Rubrique . " = L.map('map" . $_Rubrique . "').setView([43.46728568599081, 12.335241045245624], 4);";
	global $g_MapLayer, $g_MarkerIcon;
	$l_result .= "var osmLayer" . $_Rubrique . " = " . $g_MapLayer;
	$l_result .= "osmLayer" . $_Rubrique . ".addTo(map" . $_Rubrique . ");";
	$l_result .= "var layerGroup" . $_Rubrique . " = L.featureGroup().addTo(map" . $_Rubrique . ");";
	$l_result .= "var customIcon" . $_Rubrique . " = " . $g_MarkerIcon;
	foreach(rechercherCoordGeo($_data[$_Rubrique], $_Rubrique, $_PopupTitles) as $CoordGeo) 
	{
		if(isset($CoordGeo))
		{
			$l_coords = explode("/", $CoordGeo);
			$l_result .= "var marker" . $_Rubrique . " = L.marker([" . $l_coords[0] . "], {icon: customIcon" . $_Rubrique . "}).addTo(map" . $_Rubrique . ");";
			$l_result .= 'marker' . $_Rubrique . '.bindPopup("<center>' . $l_coords[1] . '</center>");';
			$l_result .= 'layerGroup' . $_Rubrique . '.addLayer(marker' . $_Rubrique . ');';
		}	
	}
	$l_result .= "map" . $_Rubrique . ".fitBounds(layerGroup" . $_Rubrique . ".getBounds());";
	$l_result .= "</script>";
	return $l_result;
}

function rechercherCoordGeo($_data, $_Rubrique, $_PopupTitles) {
    $coord_geo = [];
    
    foreach ($_data as $key => $value) 
	{
        if ($key === 'coord_geo') 
		{
            $l_title = "";
			foreach ($_PopupTitles as $title) 
			{
				$l_title .= $_data[$title] . "<br>";
			}
			$coord_geo[] = $value . "/" . $l_title;
        }
        elseif (is_array($value)) {
            if ($key !== $_Rubrique) {
                $coord_geo = array_merge($coord_geo, rechercherCoordGeo($value, $_Rubrique, $_PopupTitles));
            }
        }
    }
    
    return $coord_geo;
}

function showTimeline($_array,$_title,$_separator)
{
	$l_result = '<div id="timeline' . $_title . '"></div><div class="hoverBox" id="hoverBox' . $_title . '"></div>';
	$l_result .= "<script type=\"text/javascript\">
	  var items" . $_title . " = new vis.DataSet([";
	$i = 1;
	$l_min_date = date("Y");
	foreach($_array as $Dates => $TitleArray) 
	{
		if(isset($Dates))
		{
			$l_dates = explode($_separator, $Dates);
			if($l_dates[0] < $l_min_date) { $l_min_date = $l_dates[0]; }
			$l_result .= "{id: " . $i . ", content: '" . str_replace("'", "\'", getPopupTitle($TitleArray)) . "' , className: \"blue\", start: new Date(" .$l_dates[0] . ", 0),end: new Date(" . str_replace("...", date("Y"), $l_dates[1]) . ", 0)},";
			$i++;
		}	
	}
	$l_result .= "]);

	  function customDateFormatter(date, scale, step) {
		  const l_date = new Date(date);
		  let year = l_date.getFullYear();
		  return year;
	  }

	  var options" . $_title . " = {
		  min: new Date(" . $l_min_date . ", 0),
		  max: new Date(),
		  start: new Date(" . $l_min_date . ", 0),
		  end: new Date(),
		  editable: false,
		  template: function(item) {
			  return '';
		  },
		  format: {
			  minorLabels: customDateFormatter
		  }
	  };

	  var container" . $_title . " = document.getElementById('timeline" . $_title . "');
	  var timeline" . $_title . " = new vis.Timeline(container" . $_title . ", items" . $_title . ", options" . $_title . ");

	  timeline" . $_title . ".on('select', function(props) {
		  var selectedItems" . $_title . " = props.items;
		  if (selectedItems" . $_title . ".length > 0) {
			  var selectedItem" . $_title . " = items" . $_title . ".get(selectedItems" . $_title . "[0]);
			  var hoverBox" . $_title . " = document.getElementById('hoverBox" . $_title . "');
			  if (typeof selectedItem" . $_title . " !== 'undefined') {
				  hoverBox" . $_title . ".innerHTML = '<span><center>' + selectedItem" . $_title . ".start.getFullYear() + '/' + selectedItem" . $_title . ".end.getFullYear() + '</center>' + selectedItem" . $_title . ".content + '</span>';
				  hoverBox" . $_title . ".style.display = 'block';
			  }
		  }
	  });
	</script>";
	return $l_result;	
}
?>