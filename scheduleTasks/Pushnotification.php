<?php
while(true) {
	// create a new cURL resource
	$ch = curl_init();
	// set URL and other appropriate options
	curl_setopt($ch, CURLOPT_URL, "http://ec2-54-200-38-8.us-west-2.compute.amazonaws.com/api/v1/user/task-notification/");
	curl_setopt($ch, CURLOPT_HEADER, 0);
	curl_exec($ch);
	// close cURL resource, and free up system resources
	curl_close($ch);
	sleep(1);
	echo "happy";
}
?>
