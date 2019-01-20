<?php
error_reporting(E_ERROR | E_PARSE);
session_start();
header("Access-Control-Allow-Origin: *");

// Set your admin password here
$password = 'password';

// Check Authentication Password
if (isset($_POST['a'])) {
	if ($_POST['a'] == $password) {
		$_SESSION['authenticated'] = true;
	} else {
		$_SESSION['authenticated'] = false;
	}
}

// Application Variables
$isWindows = false;
if (strtoupper(substr(PHP_OS, 0, 3)) === 'WIN') {
    $isWindows = true;
}

$data = dirname(__FILE__) . DIRECTORY_SEPARATOR . '..' . DIRECTORY_SEPARATOR . 'data' . DIRECTORY_SEPARATOR;

$smtp_host = "smtp.domain.com";
$smtp_user = "email@address.com";
$smtp_pass = "password";

$alert_from = "email@address.com";
$alert_email = "1112223333@smsgateway.com";  // Email to SMS gateway address (https://en.wikipedia.org/wiki/SMS_gateway)

$debug = @$_GET['debug'];
?>
