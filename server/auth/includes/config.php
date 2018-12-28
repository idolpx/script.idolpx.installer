<?php
error_reporting(E_ERROR | E_PARSE);
session_start();
header("Access-Control-Allow-Origin: *");

// Application Variables
$isWindows = false;
if (strtoupper(substr(PHP_OS, 0, 3)) === 'WIN') {
    $isWindows = true;
}

dirname(__FILE__).'/../data/';

$smtp_host = "smtp.domain.com";
$smtp_user = "email@address.com";
$smtp_pass = "password";

$alert_from = "email@address.com";
$alert_email = "1112223333@smsgateway.com";  // Email to SMS gateway address (https://en.wikipedia.org/wiki/SMS_gateway)

$debug = @$_GET['debug'];
?>
