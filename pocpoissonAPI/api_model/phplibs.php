<?php
// Retrieves datas from POST or GET, with custom cases for API Key in header
function get_GETORPOST($key){
	if(isset($_REQUEST[$key]))return $_REQUEST[$key];
	if(isset($_GET[$key]))return $_GET[$key];
	if(isset($_POST[$key]))return $_POST[$key];
	if("key"==$key and isset(getallheaders()["X-Api-Key"])) return getallheaders()["X-Api-Key"];
	return NULL;
}

// Retrieves data from all available sources (get_GETORPOST + priority to php SESSION)
function custom_get($key){
	if(!isset($_SESSION)){
		session_start();
	}
	if(isset($_SESSION[$key]))return $_SESSION[$key];
	return get_GETORPOST($key);
}

// Previously use for session availability
function check_for_mat_id(){
	if(null!=get_GETORPOST('mat_id') or null!=get_GETORPOST('key')){
		session_start();
		session_destroy();
	}
}

// Session cleaner : if a new parameter provided differs from the one existing is session data, everything is cleared.
function session_cleaner(){
	$ck = array("mat_id", "key");
	foreach ($ck as $k){ 
		if(get_GETORPOST($k)!=null && get_GETORPOST($k)!=custom_get($k)){
			session_destroy();
			session_start();
	}}
}

// Checks if the user exists
function check_user($mat_id, $conn = null){
		$dyn_build_connect = dyn_build_connect($conn);
		$qp = "SELECT current_score FROM poc.users WHERE mat_id=$1";
		$result = pg_query_params($dyn_build_connect['connection'], $qp, array($mat_id));
		if (!$result or pg_num_rows($result)==0){
			dyn_close_connect($dyn_build_connect);
			return false ;
		}
		while ($row = pg_fetch_row($result)){
			dyn_close_connect($dyn_build_connect);
			return true ;
		}
	}
// Checks if the user exists and if the credentials are ok
function check_user_pwd($mat_id, $password, $conn = null){
		$dyn_build_connect = dyn_build_connect($conn);
		$qp = "SELECT true FROM poc.users WHERE mat_id=$1 AND pass=md5($2)";
		$result = pg_query_params($dyn_build_connect['connection'], $qp, array($mat_id, $password));
		if (!$result or pg_num_rows($result)==0) {
		  dyn_close_connect($dyn_build_connect);
		  seterror(401, $detail = "Unable to identify the user.", $pointer = "check_password_wscore", $instance = "Client code : $mat_id");
	      return false;
		}
		while ($row = pg_fetch_row($result)) {
		  dyn_close_connect($dyn_build_connect);
		  return true;
		}
	}
	
// Gets an encoded md5pass, for recording of passwords while creating a new user
function get_md5pass($pass, $conn = null){
		$dyn_build_connect = dyn_build_connect($conn);
		$qp = "SELECT md5($1)";
		$result = pg_query_params($dyn_build_connect['connection'], $qp, array($pass));
		if (!$result or pg_num_rows($result)==0) {
		    dyn_close_connect($dyn_build_connect);
			return false ;
		}
		while ($row = pg_fetch_row($result)){
		    dyn_close_connect($dyn_build_connect);
			return $row[0] ;
		}
		
	}

// Gets user score (with password, cause in previous job this function was used to check credentials)
function check_password_wscore($mat_id, $password,$conn = null ){
		$dyn_build_connect = dyn_build_connect($conn);
		$qp = "SELECT current_score FROM poc.users WHERE mat_id=$1 AND pass=md5($2)";
		$result = pg_query_params($dyn_build_connect['connection'], $qp, array($mat_id, $password));
		if (!$result or pg_num_rows($result)==0) {
		  dyn_close_connect($dyn_build_connect);
	      seterror(401, $detail = "Unable to identify the user.", $pointer = "check_password_wscore", $instance = "Client code : $mat_id");
		}
		while ($row = pg_fetch_row($result)) {
		  dyn_close_connect($dyn_build_connect);
		  return $row[0];
		}
	}

// Connects to database
function pgconnect(){
	global $connexion_string ;
	$db_connect = $connexion_string;
	$conn = pg_pconnect($db_connect);
	if (!$conn) {
	  print('{"error":"The database is unreachable."}') ; # throw new Exception("The database is unreachable.");
	  seterror(503, $detail = "The database is unreachable.", $pointer = "Db connection", $instance = "Client code : not available.");
	}
	return $conn ;
}

// Helps to chose, if the database connection stays opened or is close in the end of function call while connectiong or writing in db
function dyn_build_connect($conn){
	if ($conn==null) {
			return array('connection' => pgconnect(), 'reset_conn' => $reset_conn = true);
		}
	return array('connection' => $conn, 'reset_conn' => $reset_conn = false); 
}

// Helps to chose, if the database connection stays opened or is close in the end of function call while closing the db
function dyn_close_connect($conn_arr){
	if($conn_arr['reset_conn']){pg_close($conn_arr['connection']);}
}
// Set headers of the PHP page
function setheaders(){
	header('Content-Type: application/json');
}


// Generic error management
function seterror($errorcode, $detail = null, $pointer = null, $instance = null, $fatal = true){
	 switch ($errorcode) {
                    case 100: $errormessage= 'Continue'; break;
                    case 101: $errormessage= 'Switching Protocols'; break;
                    case 200: $errormessage= 'OK'; break;
                    case 201: $errormessage= 'Created'; break;
                    case 202: $errormessage= 'Accepted'; break;
                    case 203: $errormessage= 'Non-Authoritative Information'; break;
                    case 204: $errormessage= 'No Content'; break;
                    case 205: $errormessage= 'Reset Content'; break;
                    case 206: $errormessage= 'Partial Content'; break;
                    case 300: $errormessage= 'Multiple Choices'; break;
                    case 301: $errormessage= 'Moved Permanently'; break;
                    case 302: $errormessage= 'Moved Temporarily'; break;
                    case 303: $errormessage= 'See Other'; break;
                    case 304: $errormessage= 'Not Modified'; break;
                    case 305: $errormessage= 'Use Proxy'; break;
                    case 400: $errormessage= 'Bad Request'; break;
                    case 401: $errormessage= 'Unauthorized'; break;
                    case 402: $errormessage= 'Payment Required'; break;
                    case 403: $errormessage= 'Forbidden'; break;
                    case 404: $errormessage= 'Not Found'; break;
                    case 405: $errormessage= 'Method Not Allowed'; break;
                    case 406: $errormessage= 'Not Acceptable'; break;
                    case 407: $errormessage= 'Proxy Authentication Required'; break;
                    case 408: $errormessage= 'Request Time-out'; break;
                    case 409: $errormessage= 'Conflict'; break;
                    case 410: $errormessage= 'Gone'; break;
                    case 411: $errormessage= 'Length Required'; break;
                    case 412: $errormessage= 'Precondition Failed'; break;
                    case 413: $errormessage= 'Request Entity Too Large'; break;
                    case 414: $errormessage= 'Request-URI Too Large'; break;
                    case 415: $errormessage= 'Unsupported Media Type'; break;
                    case 500: $errormessage= 'Internal Server Error'; break;
                    case 501: $errormessage= 'Not Implemented'; break;
                    case 502: $errormessage= 'Bad Gateway'; break;
                    case 503: $errormessage= 'Service Unavailable'; break;
                    case 504: $errormessage= 'Gateway Time-out'; break;
                    case 505: $errormessage= 'HTTP Version not supported'; break;
                    default:
                        exit('Unknown http status code "' . htmlentities($code) . '"');
                    break;
                }
	http_response_code($errorcode);
	$problem = array(
		"type" => (empty($_SERVER['HTTPS']) ? 'http' : 'https') . "://$_SERVER[HTTP_HOST]$_SERVER[REQUEST_URI]/$errorcode",
		"detail" => $detail,
		"title" => $errormessage,
		"status" => $errorcode,
		"instance" => $instance
	);
	echo json_encode($problem);
	if ($fatal == true) { exit ; }
}



?>