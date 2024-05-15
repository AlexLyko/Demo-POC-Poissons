<?php
include "../conf/conf.php";

class User
{
	// Local variables declaration
	// Number of provided properties
	private $properties_nb = 0;
	// Are the connection data ok ?
	private $connection_ok = false;
	// Fields required for connection ?
	private $required = array('user_id','pwd');
	// Connection properties
	private $connection_properties = array();
	// Mapping between inputs and connection data
	private $properties_mapping = array('user_id' => 'mat_id','pwd' => 'key');
	// Status of the user instance ("NOPE", "Check if can connect", "Can connect", "Try creating", "Ready"...)
	public $status = "NOPE";
	// Was the user previously in the database ?
	public $already_exists = false;
	
	// Destroy session and properties
	public function decon(){
		session_destroy();
		$this->connection_properties = null ;
	}
	// Get user id
	public function id(){
		return $this->connection_properties['user_id'];
	}
	
	// Get user score
	public function score(){
			return check_password_wscore($this->connection_properties['user_id'],$this->connection_properties['pwd']);
	}
	
	// Add score to the the previous one (in database)
	public function add_score($add_score){
		// Security checks
		$mat_id = $this->connection_properties['user_id'];
		$conn = pgconnect();
		if(null==$add_score){
			  seterror(401, $detail = "Parameter addscore is missing.", $pointer = "update_user_wscore", $instance = "Client code : $mat_id.");
		}
		// Writing in database
		$n_score = array();
		$n_score ["previous_score"] = check_password_wscore($mat_id, $this->connection_properties['pwd'],$conn);
		$n_score ["new_score"] = $n_score ["previous_score"] + $add_score;
		$data = array('current_score'=>$n_score ["new_score"]);
		$conditions = array('mat_id'=>$mat_id);
		$res = pg_update($conn, "poc.users", $data, $conditions);
		if (!$res) {
			seterror(503, $detail = "Unable to modify the user.", $pointer = "update_user_wscore", $instance = "Client code : $mat_id.");
		}
		pg_close($conn);
		return $n_score;
	}
	
	// Check whether the connection data are ok
	// Tries to create the new user if credentials are ok ande user doesn't exist
	public function check_connection(){
		// Retrieving data info
		foreach ($this->properties_mapping as $k1 => $k2) {
			$var_k = custom_get($k2);
			if($var_k!=null){$this->connection_properties[$k1] = $var_k ;}
		}
		$this->properties_nb = count(array_intersect_key(array_flip($this->required), $this->connection_properties))  ;
		if ($this->properties_nb !== count($this->required)){
			seterror(401, $detail = "Unable to identify the user (missing parameters).", $pointer = "API user call", $instance = "Info not available.");
		}
		// Set the connexion to dB
		$conn = pgconnect();
		// Check if user exists
		if (isset($this->connection_properties['user_id'])){
			$this->already_exists = check_user($this->connection_properties['user_id'], $conn);
		}else{
			seterror(401, $detail = "Unable to identify the user.", $pointer = "API user call", $instance = "Info not available.");
		}
		// If exists, try to open a connection
		if ($this->already_exists) {
			$this->status = "Check if can connect";
			$connection_ok = check_user_pwd($this->connection_properties['user_id'],$this->connection_properties['pwd']);
			if($connection_ok){
				$this->status = "Can connect";
				$this->load_into_session();
			}
		// If doesn't exist and key is valid, try to create a new one
		} else {
			$this->status = "Try creating";
			$this->create();
		}
	}
	
	// Update php session datas
	public function load_into_session(){
		if(!isset($_SESSION)){
			session_start();
		}
		$_SESSION["mat_id"]= $this->connection_properties['user_id'];
		$_SESSION["key"]= $this->connection_properties['pwd'];
		$this->status = "Ready";
	}
	// Create a nex user in database
	public function create(){
		$var = 0 ;
		$conn = pgconnect();
		$mat_id = $this->connection_properties['user_id'];
		// Security checks
		global $generic_api_key;
		if ($generic_api_key !== $this->connection_properties['pwd']){
			session_destroy();
			seterror(401, $detail = "API key is not valid.", $pointer = "create_user", $instance = "Client code : $mat_id.");
			return;
		}
		if(check_user($mat_id, $conn)){
			seterror(401, $detail = "Existing user.", $pointer = "create_user", $instance = "Client code : $mat_id.");
			pg_close($conn);
			session_destroy();
		}
		// Writing in database
		$data = array('mat_id'=>$mat_id, 'pass'=> get_md5pass($this->connection_properties['pwd'], $conn), "current_score" => 0);
		$res = pg_insert($conn, "poc.users", $data);
		if (!$res) {
			seterror(503, $detail = "Unable to modify the user.", $pointer = "create_user", $instance = "Client code : $mat_id.");
		}
		pg_close($conn);
		$this->load_into_session();
	}
	
	// Delete the suer
	public function delete(){
		$var = 0 ;
		$conn = pgconnect();
		$mat_id = $this->connection_properties['user_id'];
		// Security checks
		global $generic_api_key;
		if ($generic_api_key !== $this->connection_properties['pwd']){
			session_destroy();
			seterror(401, $detail = "API key is not valid.", $pointer = "create_user", $instance = "Client code : $mat_id.");
			return;
		}
		if(!check_user($mat_id, $conn)){
			seterror(401, $detail = "Non existing user.", $pointer = "create_user", $instance = "Client code : $mat_id.");
			pg_close($conn);
			session_destroy();
		}
		// Writing in database
		$data = array('mat_id'=>$mat_id, 'pass'=> get_md5pass($this->connection_properties['pwd'], $conn));
		$res = pg_delete($conn, "poc.users", $data);
		if (!$res) {
			seterror(503, $detail = "Unable to delete the user.", $pointer = "create_user", $instance = "Client code : $mat_id.");
		}
		pg_close($conn);
		$this->load_into_session();
	}

	// Get questions
	public question get_questions(){
		$conn = pgconnect();
		$qp = "SELECT json_agg(row_to_json(questions.*, true)) FROM poc.questions WHERE mat_id = $1";
			$result = pg_query_params($conn, $qp, array($this->connection_properties['user_id']));
			if (!$result or pg_num_rows($result)==0) {
				seterror(503, $detail = "Unable to identify the user.", $pointer = "get_questions", $instance = "Client code : $mat_id.");
				pg_close($conn);
			}
			while ($row = pg_fetch_row($result)) {
			  $n_q_id = $row[0];
			}
		pg_close($conn);
		return $n_q_id;
	}
	
	// By default, during object instanciation session is cleaned and credential are tested
	function __construct() {
		if(!isset($_SESSION)){
					session_start();
				}
		session_cleaner();
		$this::check_connection();
    }
}
// Unit test
/*
$user = new User();
if(null !==(get_GETORPOST('add_score'))){
	$user->add_score(get_GETORPOST('add_score'));
	echo $user->score();
}
if(null !==(get_GETORPOST('delete'))){
	$user->delete();
}
*/
?>