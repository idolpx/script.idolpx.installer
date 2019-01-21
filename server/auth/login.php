<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="https://code.jquery.com/mobile/1.4.5/jquery.mobile-1.4.5.min.css">
<script src="https://code.jquery.com/jquery-1.11.3.min.js"></script>
<script src="https://code.jquery.com/mobile/1.4.5/jquery.mobile-1.4.5.min.js"></script>
</head>
<body>

	<div data-role="page" id="login">
		<div data-role="header">
			<h1>idolpx Installer</h1>
		</div>

		<div data-role="content" data-inset="true">
			<div style="margin:10%">
			<fieldset>
				<form method="post" id="loginForm" action="index.php">
					<li class="ui-field-contain">
						<input type="password" name="a" value="" placeholder="Password" />
					</li>
					<input type="submit" value="Login" data-role="button" data-theme="b" />
				</form>
			</fieldset>
			</div>
		</div>
	</div>

</body>
</html>