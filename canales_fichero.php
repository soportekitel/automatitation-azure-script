#!/usr/bin/php
<?php 
	require_once "include/excel/class.writeexcel_workbook.inc.php";
	require_once "include/excel/class.writeexcel_worksheet.inc.php";
	require_once "include/PHPMailer/PHPMailerAutoload.php";
	error_reporting(0);
	
	
	
	$MAILDEST="soporte@contigoo.es";
	
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
	
	$MAILSUBJECT="Informe de canales ".gethostname()." ".date("Y-m-d H:i:s")."\n";
	$MAILBODY="Informacion del uso de canales de ".gethostname()." de la semana anterior";
	$MENSAJE= date("Y-m-d H:i:s")."/".$canal."/".str_replace(' ', '', $memoria)." \r\n";	
	if (($dia=="Saturday")or($dia=="Sunday"))
	{
		if ($canal>0)
		{
			if ($fp = fopen("/usr/local/infodes/bin/canales.txt", "a")){
				fwrite($fp, $MENSAJE);
				fclose($fp);
			}
		}
	}
    else
	{
		if ($fp = fopen("/usr/local/infodes/bin/canales.txt", "a")){
			fwrite($fp, $MENSAJE);
			fclose($fp);
		}
	}
	$archivo="/usr/local/infodes/bin/canales.txt";
	
	
	
	//$mail->SMTPDebug = 3;
	
	
	
   if ($dia=="Monday"){
		$hora=date(H);
		if ($hora=="06")
		{
			$mail = new PHPMailer;
		
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
			
			
			
			
			
			
				$mail->addAttachment($archivo);     
			// Add attachments
			$mail->isHTML(true);                                  // Set email format to HTML
		
			$mail->Subject = $MAILSUBJECT;
			$mail->Body    = $MAILBODY;
				
			if(!$mail->send()) {
				echo 'Message could not be sent.';
				echo 'Mailer Error: ' . $mail->ErrorInfo;
			}
		}
		
		
	}
	
	
	
	
	
	


?>