#!/usr/bin/php
<?php 
	require_once "include/excel/class.writeexcel_workbook.inc.php";
	require_once "include/excel/class.writeexcel_worksheet.inc.php";
	require_once "include/PHPMailer/PHPMailerAutoload.php";
	error_reporting(0);
	
	
	
	$DB_USER="root";
	$DB_PASS="$$5gdaCd13$$";
	$DB_HOST="localhost";
	$link=mysql_connect($DB_HOST,$DB_USER,$DB_PASS) or die ("Error: ".mysql_error());
	
	$MAILDEST="informes@kitel.es";
	#$MAILDEST2="soporte@kitel.es";
	
	$MAILSERV="smtp.dondominio.com";
	$MAILFROM="informes@kitel.es";
	$MAILUSER="informes@kitel.es";
	$MAILPASS="5gdaCd13?";
	$NUMCANALES = shell_exec("asterisk -vvvvvrx 'core show channels' | grep channels");
	$MEMORIAUSADA = shell_exec("vmstat -s -S M | grep -ie 'used memory'");
	
	$posicioncanal=strpos($NUMCANALES," ");
	$canal=substr($NUMCANALES,0,$posicioncanal);
	$posicionmemoria=strpos($MEMORIAUSADA," M");
	$memoria=substr($MEMORIAUSADA,0,$posicionmemoria);
	
	$MAILSUBJECT="Informe de canales " .date("d-m-Y H:m:s")."\n";
	$MAILBODY="Informacion a ".date("d-m-Y H:m:s")." El numero de canales activos : ".$canal." Memoria en uso:".$memoria." M de 15779 M\n";
		


	if ($canal>390){
	
	//Envio de mail
	
	$mail = new PHPMailer;
	
	//$mail->SMTPDebug = 3;
	
	$mail->isSMTP();                                      // Set mailer to use SMTP
	$mail->Host = $MAILSERV;  // Specify main and backup SMTP servers
	$mail->SMTPAuth = true;                               // Enable SMTP authentication
	$mail->Username = $MAILUSER;                 // SMTP username
	$mail->Password = $MAILPASS;                           // SMTP password
	$mail->SMTPSecure = 'tls';                            // Enable TLS encryption, `ssl` also accepted
	//$mail->SMTPSecure = 'ssl';
	$mail->Port = 587;                                    // TCP port to connect to
	
	$mail->setFrom($MAILFROM);
	$mail->addAddress($MAILDEST);
	

      // Add attachments
	$mail->isHTML(true);                                  // Set email format to HTML
	
	$mail->Subject = $MAILSUBJECT;
	$mail->Body    = $MAILBODY;
		
	if(!$mail->send()) {
		echo 'Message could not be sent.';
		echo 'Mailer Error: ' . $mail->ErrorInfo;
	} 
	
	}

 else
 {
	 echo 'CANALES LIBRES';
 }


?>
