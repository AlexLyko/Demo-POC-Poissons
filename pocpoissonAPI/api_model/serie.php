<?php
include "../user.php";

class Serie
{
	private $user ;
	private $level ="easy" ;
	private $profile = "basic" ;
	private $last_serie;
	
	//  Questions serie generator
	public function get_10($level,$profile){
		$this -> level = $level;
		$this -> profile = $profile;
		$this -> last_serie = $this->launchPy($this->user->id(),$level,$profile);
	}
	// Save question serie in database, from URL input parameters ($mode = "post") or from previous use of PHP method ($mode = "direct" or null)
	public function save($mode="direct"){
	//Settings for data input
	$mapping = array(
		"content" => "content",
		"score"   => "userscore",
		"estimated_difficulty" => "difficulty",
		"level" => "level",
		"profile" => "profile"
	);

	// Creating the new data for record
	$conn = pgconnect();
    $mat_id = $this->user->id();
	if("post"==$mode){
		foreach ($mapping as $key => $value) {
			$data = array('mat_id'=>$mat_id);
			if(get_GETORPOST($value)!==null)$data[$key]=get_GETORPOST($value);
		}
	}else{
		$data = array(
			'mat_id'=>$mat_id,
			"content" => $this -> last_serie,
			"score"   => 0,
			"estimated_difficulty" => 0,
			"level" => $this -> level,
			"profile" => $this -> profile
		);
	
	}
	
	// Feeding the database
	$res = pg_insert($conn, "poc.questions", $data);
	if (!$res) {
		seterror(503, $detail = "Unable to modify the user.", $pointer = "save_question", $instance = "Client code : $mat_id.");
	}
	// Retrieve the last serie id, immediatly commited in previous line
	$qp = "SELECT id_series FROM poc.questions WHERE mat_id=$1 ORDER BY created_at DESC LIMIT 1";
		$result = pg_query_params($conn, $qp, array($mat_id));
		if (!$result or pg_num_rows($result)==0) {
			pg_close($conn);
			seterror(402, $detail = "Unable to identify the user.", $pointer = "save_question", $instance = "Client code : $mat_id.");
			pg_close($conn);
		  
		}
		while ($row = pg_fetch_row($result)) {
		  $n_q_id = $row[0];
		}
	pg_close($conn);
	
	return $n_q_id;
	}

	// Python launchnig function
	private function launchPy($mat_id, $level,$profile="basic"){
		if($mat_id==null)seterror(401, $detail = "Parameter mat_id is missing.", $pointer = "10questions2", $instance = "Client code not available.");
		// Ordre défini en configuration
		global  $py_cmd_questions2 ;
		global $correction_nb_url ;
		// Exécution de la commande Python et passage d'arguments
		if (!in_array($level, array("easy", "medium", "expert"))) {
			seterror(401, $detail = "Parameter level is required and amongst 'easy', 'medium', 'expert'.", $pointer = "Command launcher", $instance = "Client code : $mat_id.");
		}
		if (!in_array($profile, array("basic", "head-on", "finisher", "hard","easy"))) {
			seterror(401, $detail = "The profile parameter provided is not authorized.", $pointer = "Command launcher", $instance = "Client code : $mat_id.");
		}
		$command = escapeshellcmd($py_cmd_questions2.' '.$level.' '.$profile.' '.$correction_nb_url);
		$output = shell_exec($command);
		echo $output;
		return $output;
	}
	
// By default, during object instanciation session is cleaned and credential are tested
	function __construct($user) {
		$this-> user = $user;
    }
}

// Unit test
/*
$serie = new Serie(new User());
$serie->get_10(htmlspecialchars(get_GETORPOST("level")),htmlspecialchars(get_GETORPOST("profile")));
$serie->save();
*/
?>