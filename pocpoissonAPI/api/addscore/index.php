<?php
// alexandre.liccardi@ofb.gouv.fr
// update 7/01/2024
include "../../apimodel/serie.php";
$user = new User();
if(null !==(get_GETORPOST('add_score'))){
	$user->add_score(get_GETORPOST('add_score'));
	echo $user->score();
}
?>
