<?php
	$log = new Katzgrau\KLogger\Logger('auth/logs/');
	$log->info($_SERVER['QUERY_STRING']);
	
	if (disk_free_space($data) < 10240) {
		echo 'Out of disk space!';
		exit();
	}
	
	if($_SESSION['admin']) {

	}
	
	$oui = array();
	if (file_exists($data."oui.json"))
		$oui = json_decode(file_get_contents($data."oui.json"), true);
	
	$devices = array();
	if (file_exists($data."devices.json"))
		$devices = json_decode(file_get_contents($data."devices.json"), true);

	if (!empty($_SERVER['HTTP_X_FORWARDED_FOR'])) {
		$ip = $_SERVER['HTTP_X_FORWARDED_FOR'];
	} else {
		$ip = $_SERVER['REMOTE_ADDR'];
	}
		
	$mac = $_GET['d'];
	$os = $_GET['os'];
	$id = $_GET['id'];
	$kv = $_GET['kv'];
	$cv = $_GET['cv'];
	if(!isset($devices[$mac])) {
		$devices[$mac]['status'] = -1;
		$devices[$mac]['group'] = "";
		
		$vendor = str_replace(':', '', $mac);
		$vendor = substr($vendor, 0, 6);
		$vendor = $oui[$vendor];
		$devices[$mac]['vendor'] = $vendor;
		$devices[$mac]['os'] = $os;
	}
	$devices[$mac]['ip'] = $ip;
	$devices[$mac]['deviceid'] = $id;
	$devices[$mac]['kodi_ver'] = $kv;
	$devices[$mac]['config_ver'] = $cv;
	$devices[$mac]['lastcheck'] = time();
	$devices = natsort2d($devices);
	
	$alerts = array();

	// Set Alert for Blocked Devices
	if($devices[$mac]['status'] == 0) {
		if($debug)
			echo "Blocked Alert! : $mac, ".$devices[$mac]['ip'].':'.$devices[$mac]['vendor']."<br />\n";
		$log->info("[blocked][$mac][".$devices[$mac]['ip']."], ".$devices[$mac]['deviceid']);
		$alerts['blocked'][$mac] = time();
	}
	
	// Set Alert for Unknown Devices
	if($devices[$mac]['status'] == -1) {
		if($debug)
			echo "Unknown Alert! : $mac, ".$devices[$mac]['ip'].':'.$devices[$mac]['vendor']."<br />\n";
		$log->info("[unknown][$mac][".$devices[$mac]['ip']."], ".$devices[$mac]['deviceid']);
		$alerts['unknown'][$mac] = time();
	}
	
	// Save Status
	file_put_contents($data."devices.json", json_encode($devices, JSON_PRETTY_PRINT));
	
	// Send Notifications
	if(strlen($_POST['action']) == 0)
	if(isset($alerts['blocked']) || isset($alerts['unknown']))
		sendAlerts();
	
	// Block anyone that is not Authorized
	//if($devices[$mac]['status'] != 1)
	//	exit();
?>