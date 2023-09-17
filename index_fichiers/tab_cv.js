// Fonction pour afficher l'onglet actif
function showTab(tabNumber) {
	// Masquer tous les contenus d'onglets
	var tabContents = document.querySelectorAll('.tab-content');
	tabContents.forEach(function(content) {
		content.classList.remove('active');
	});

	// Afficher le contenu de l'onglet sélectionné
	document.getElementById('tab' + tabNumber).classList.add('active');
}

// Par défaut, afficher le premier onglet
showTab(1);