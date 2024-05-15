<?php
// alexandre.liccardi@ofb.gouv.fr
// update 7/01/2024
include "../../apimodel/serie.php";
$serie = new Serie(new User());
$serie->get_10(htmlspecialchars(get_GETORPOST("level")),htmlspecialchars(get_GETORPOST("profile")));

?>