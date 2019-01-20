<?php
	require 'vendor/autoload.php';
	require 'includes/config.php';
	require 'includes/common.php';
	
	$log = new Katzgrau\KLogger\Logger('logs/');
	
	// Component Tests
	//$log->info('Returned a million search results'); echo 'ok!'; exit();
	//sendAlerts(); exit();
	
	if(!$_SESSION['authenticated']) {
		$log->info("[authentication][".$_SERVER['REMOTE_ADDR']."], [".$_GET."]");
		header('Location: login.php');
		die();
	}
	
	$devices = array();
	if (file_exists($data."devices.json"))
		$devices = json_decode(file_get_contents($data."devices.json"), true);
		
	if (isset($_POST['mac'])) {	
		$key = $_POST['mac'];
		if ($_POST['action'] == "Update") {
			$devices[$key]['group'] = $_POST['group'];
			$devices[$key]['deviceid'] = $_POST['deviceid'];
			$log->info("[updated][$key][".$devices[$key]['ip']."], ".$devices[$key]['group'].':'.$devices[$key]['deviceid']);
		} elseif ($_POST['action'] == "Authorize") {
			$devices[$key]['status'] = 1;
			$log->info("[authorized][$key][".$devices[$key]['ip']."], ".$devices[$key]['group'].':'.$devices[$key]['deviceid']);
		} elseif ($_POST['action'] == "Block") {
			$devices[$key]['status'] = 0;
			$log->info("[blocked][$key][".$devices[$key]['ip']."], ".$devices[$key]['group'].':'.$devices[$key]['deviceid']);
		} elseif ($_POST['action'] == "Delete") {
			$log->info("[deleted][$key][".$devices[$key]['ip']."], ".$devices[$key]['group'].':'.$devices[$key]['deviceid']);
			unset($devices[$key]);
		}

		// Save Status
		file_put_contents($data."devices.json", json_encode($devices, JSON_PRETTY_PRINT));
	}

	// Sort by Group
	$devices = sortmulti($devices, 'group');

	// Get list of groups
	$group = '';
	$groups = array();
	foreach ($devices as $key => $value) {
		if($value["status"] == 1) {
			if($value['group'] != $group) {
				$group = $value['group'];
				$groups[$group] = 1;
			} else {
				$groups[$group]++;
			}
		}
	}
	//print_r($groups);
	//exit();
	
	//$devices = natsort2d($devices);
	//$devices = sortBySubValueStr($devices, 'group');
	//var_dump($devices);
	//exit();
?>
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="https://code.jquery.com/mobile/1.4.5/jquery.mobile-1.4.5.min.css">
<script src="https://code.jquery.com/jquery-1.11.3.min.js"></script>
<script src="https://code.jquery.com/mobile/1.4.5/jquery.mobile-1.4.5.min.js"></script>
</head>
<body>

<div data-role="page" id="authorized">
	<div data-role="header">
		<h1>idolpx Installer</h1>
		<div data-role="navbar">
			<ul>
				<li><a href="#authorized">Authorized</a></li>
				<li><a href="#blocked">Blocked</a></li>	
				<li><a href="#unknown">Unknown</a></li>
			</ul>
		</div>
	</div>

	<div data-role="main" class="ui-content">
		<h1>Authorized</h1>
		<div data-role="collapsible-set" data-theme="a" data-content-theme="a" data-filter="true">
			<?php
				// Display Authorized
				foreach ($groups as $group => $gcount) {
			?>
			<div data-role="collapsible">
				<h1><?php if(strlen($group) == 0) echo "unknown"; ?> <?php echo $group; ?><span class="ui-li-count"><?php echo $gcount; ?></span></h1>
				<p>
					<div data-role="collapsible-set" data-theme="a" data-content-theme="a">
						<?php
							// Display Authorized
							foreach ($devices as $key => $value) {
								if($value["status"] == 1 && $value["group"] == $group) {
						?>
						<div data-role="collapsible">
						  <h1><?php if(strlen($value["deviceid"]) == 0) echo "unknown"; ?> <?php echo $value["deviceid"]; ?> (<?php echo $value["config_ver"]; ?>)</h1>
						  <p>
							<div class="device <?php if(strlen($value["deviceid"]) == 0) echo "unknown"; ?>">
								<form method="post">
									<div class="ui-field-contain">
										<input type="hidden" name="mac" value="<?php echo $key; ?>" />

										<li class="ui-field-contain">
											<label for="madd">MAC Address:</label>
											<input type="text" name="madd" value="<?php echo $key; ?>" />
										</li>

										<li class="ui-field-contain">
											<label for="ipadd">IP Address:</label>
											<input type="text" name="ipadd" value="<?php echo $value["ip"]; ?>" />
										</li>

										<li class="ui-field-contain">
											<label for="lastseen">Last Seen:</label>
											<input type="text" name="lastseen" value="<?php echo date("m-d-Y g:i a", $value['lastcheck']); ?>" />
										</li>

										<li class="ui-field-contain">
											<label for="vendor">Vendor:</label>
											<input type="text" name="vendor" value="<?php echo $value["vendor"]; ?>" />
										</li>

										<li class="ui-field-contain">
											<label for="os">Operating System:</label>
											<input type="text" name="os" value="<?php echo $value["os"]; ?>" />
										</li>

										<li class="ui-field-contain">
											<label for="group">Group</label>		
											<input type="text" name="group" value="<?php echo $value["group"]; ?>" />
										</li>

										<li class="ui-field-contain">
											<label for="deviceid">Device ID</label>
											<input type="text" name="deviceid" value="<?php echo $value["deviceid"]; ?>" />
										</li>

										<li class="ui-field-contain">
											<label for="kodi_ver">Kodi Version</label>
											<input type="text" name="kodi_ver" value="<?php echo $value["kodi_ver"]; ?>" />
										</li>

										<li class="ui-field-contain">
											<label for="config_ver">Config Version</label>
											<input type="text" name="config_ver" value="<?php echo $value["config_ver"]; ?>" />
										</li>
										
										<li class="ui-field-contain">
											<input type="submit" name="action" value="Update" />
											<input type="submit" name="action" value="Block" />
											<input type="submit" name="action" value="Delete" />
										</li>
									</div>
								</form>
							</div>
						  </p>
						</div>
						<?php 
									$authorized_count = $authorized_count + 1;
								}
							} 
						?>
					</div>
				</p>
			</div>
			<?php } ?>
		</div>
		<div data-role="footer" data-position="fixed">
			<h1></h1>
		</div>
	</div>
</div>

<div data-role="page" id="blocked">
  <div data-role="header">
    <h1>idolpx Installer</h1>
    <div data-role="navbar">
      <ul>
        <li><a href="#authorized">Authorized</a></li>
        <li><a href="#blocked">Blocked</a></li>	
        <li><a href="#unknown">Unknown</a></li>
      </ul>
    </div>
  </div>

  <div data-role="main" class="ui-content">
	<h1>Blocked</h1>
	<div data-role="collapsible-set" data-theme="a" data-content-theme="a" data-filter="true">
		<?php
			// Display Blocked
			foreach ($devices as $key => $value) {
				if($value["status"] == 0) {
		?>
		<div data-role="collapsible">
		  <h1><?php if(strlen($value["deviceid"]) == 0) echo "unknown"; ?> <?php echo $value["deviceid"]; ?></h1>
		  <p>
			<div class="device <?php if(strlen($value["deviceid"]) == 0) echo "unknown"; ?>">
				<form method="post">
					<div class="ui-field-contain">
						<input type="hidden" name="mac" value="<?php echo $key; ?>" />

						<li class="ui-field-contain">
							<label for="madd">MAC Address:</label>
							<input type="text" name="madd" value="<?php echo $key; ?>" />
						</li>

						<li class="ui-field-contain">
							<label for="ipadd">IP Address:</label>
							<input type="text" name="ipadd" value="<?php echo $value["ip"]; ?>" />
						</li>

						<li class="ui-field-contain">
							<label for="lastseen">Last Seen:</label>
							<input type="text" name="lastseen" value="<?php echo date("m-d-Y g:i a", $value['lastcheck']); ?>" />
						</li>

						<li class="ui-field-contain">
							<label for="vendor">Vendor:</label>
							<input type="text" name="vendor" value="<?php echo $value["vendor"]; ?>" />
						</li>

						<li class="ui-field-contain">
							<label for="os">Operating System:</label>
							<input type="text" name="os" value="<?php echo $value["os"]; ?>" />
						</li>

						<li class="ui-field-contain">
							<label for="group">Group</label>		
							<input type="text" name="group" value="<?php echo $value["group"]; ?>" />
						</li>

						<li class="ui-field-contain">
							<label for="deviceid">Device ID</label>
							<input type="text" name="deviceid" value="<?php echo $value["deviceid"]; ?>" />
						</li>

						<li class="ui-field-contain">
							<label for="kodi_ver">Kodi Version</label>
							<input type="text" name="kodi_ver" value="<?php echo $value["kodi_ver"]; ?>" />
						</li>

						<li class="ui-field-contain">
							<label for="config_ver">Config Version</label>
							<input type="text" name="config_ver" value="<?php echo $value["config_ver"]; ?>" />
						</li>
						
						<li class="ui-field-contain">
							<input type="submit" name="action" value="Update" />
							<input type="submit" name="action" value="Authorize" />
							<input type="submit" name="action" value="Delete" />
						</li>
					</div>
				</form>
			</div>
		  </p>
		</div>
		<?php 
					$authorized_count = $authorized_count + 1;
				}
			} 
		?>
	</div>
  </div>
  <div data-role="footer" data-position="fixed">
    <h1></h1>
  </div>
</div> 

<div data-role="page" id="unknown">
  <div data-role="header">
    <h1>idolpx Installer</h1>
    <div data-role="navbar">
      <ul>
        <li><a href="#authorized">Authorized</a></li>
        <li><a href="#blocked">Blocked</a></li>	
        <li><a href="#unknown">Unknown</a></li>
      </ul>
    </div>
  </div>

  <div data-role="main" class="ui-content">
	<h1>Unknown</h1>
	<div data-role="collapsible-set" data-theme="a" data-content-theme="a" data-filter="true">
		<?php
			// Display Unknown
			foreach ($devices as $key => $value) {
				if($value["status"] == -1) {
		?>
		<div data-role="collapsible">
		  <h1><?php if(strlen($value["deviceid"]) == 0) echo "unknown"; ?> <?php echo $value["deviceid"]; ?></h1>
		  <p>
			<div class="device <?php if(strlen($value["deviceid"]) == 0) echo "unknown"; ?>">
				<form method="post">
					<div class="ui-field-contain">
						<input type="hidden" name="mac" value="<?php echo $key; ?>" />

						<li class="ui-field-contain">
							<label for="madd">MAC Address:</label>
							<input type="text" name="madd" value="<?php echo $key; ?>" />
						</li>

						<li class="ui-field-contain">
							<label for="ipadd">IP Address:</label>
							<input type="text" name="ipadd" value="<?php echo $value["ip"]; ?>" />
						</li>

						<li class="ui-field-contain">
							<label for="lastseen">Last Seen:</label>
							<input type="text" name="lastseen" value="<?php echo date("m-d-Y g:i a", $value['lastcheck']); ?>" />
						</li>

						<li class="ui-field-contain">
							<label for="vendor">Vendor:</label>
							<input type="text" name="vendor" value="<?php echo $value["vendor"]; ?>" />
						</li>

						<li class="ui-field-contain">
							<label for="os">Operating System:</label>
							<input type="text" name="os" value="<?php echo $value["os"]; ?>" />
						</li>

						<li class="ui-field-contain">
							<label for="group">Group</label>		
							<input type="text" name="group" value="<?php echo $value["group"]; ?>" />
						</li>

						<li class="ui-field-contain">
							<label for="deviceid">Device ID</label>
							<input type="text" name="deviceid" value="<?php echo $value["deviceid"]; ?>" />
						</li>

						<li class="ui-field-contain">
							<label for="kodi_ver">Kodi Version</label>
							<input type="text" name="kodi_ver" value="<?php echo $value["kodi_ver"]; ?>" />
						</li>

						<li class="ui-field-contain">
							<label for="config_ver">Config Version</label>
							<input type="text" name="config_ver" value="<?php echo $value["config_ver"]; ?>" />
						</li>
						
						<li class="ui-field-contain">
							<input type="submit" name="action" value="Update" />
							<input type="submit" name="action" value="Authorize" />
							<input type="submit" name="action" value="Block" />
							<input type="submit" name="action" value="Delete" />
						</li>
					</div>
				</form>
			</div>
		  </p>
		</div>
		<?php 
				}
			}
		?>
	</div>
  </div>
  <div data-role="footer" data-position="fixed">
    <h1></h1>
  </div>
</div> 



<div data-role="page" id="details">
  <div data-role="main" class="ui-content">
    <a href="#fullList">Go to Page One</a>
  </div>
</div>

<script>
$("input[name=madd]").click(function(){
	//alert($(this).val());
	window.open("https://api.macvendors.com/"+$(this).val(), '_blank');
	return false;
});
$("input[name=ipadd]").click(function(){
	//alert($(this).val());
	window.open("https://db-ip.com/"+$(this).val(), '_blank');
	return false;
});
</script>

</body>
</html>
