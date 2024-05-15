<?php
	// Chaîne de caractères : paramètres de connexion PG
	global $connexion_string ;
	// Ordre python lancement commande génération 10questions, version 1
	global $py_cmd_questions ;
	// Ordre python lancement commande génération 10questions, version 2
	global $py_cmd_questions2 ;
	// Ordre python lancement commande génération 10questions, version 3
	global $py_cmd_questions3 ;
	// Chemin vers le fichier de fonctions PHP partagées
	global $php_libs;
	// API key générique transmise par l'administrateur
	global $generic_api_key;
	// Nombre d'images transmises pour "reconnaître les erreur"
	global $correction_nb_url;
	
	// Clé API de connexion
	$generic_api_key = "";
	// Ordre de connexion à la base de données
	$connexion_string = "";
	// Ordre d'exécution Python
	$py_cmd_questions = "";
	// Répertoire de chargement des bibliothèques PHP
	$php_libs = "../api_model/phplibs.php";
	// Nombre d'URL retrounée pour l'interface d'aide aux utilisateurs (auto correction)
	$correction_nb_url = 10 ;
	
	include $php_libs ;
?>
