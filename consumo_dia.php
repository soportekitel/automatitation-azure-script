#!/usr/bin/php
<?php 
	require_once "include/excel/class.writeexcel_workbook.inc.php";
	require_once "include/excel/class.writeexcel_worksheet.inc.php";
	require_once "include/PHPMailer/PHPMailerAutoload.php";
	error_reporting(0);
	
	function query($query) {
		global $link;
		echo $query."<br/>";
		return mysql_query($query,$link);
	}
	
	function fecha_visible($entrada) {
		return substr($entrada,8,2)."/".substr($entrada,5,2)."/".substr($entrada,0,4);
	}
	
	function hora_visible($entrada) {
		return substr($entrada,11);
	}
	$dia=$argv[1];
	$mes=$argv[2];
	$anio=$argv[3];
	
	
	$hora_inicio=$anio."-".$mes."-".$dia." 00:00:00";
		
	$hora_fin=$anio."-".$mes."-".$dia." 23:59:59";
	
	$DB_USER="root";
	$DB_PASS="$$5gdaCd13$$";
	$DB_HOST="localhost";
	$DB_BASE="asteriskcdrdb";
	$link = mysqli_connect($DB_HOST, $DB_USER, $DB_PASS,$DB_BASE);

	/* comprobar la conexión */
	if (mysqli_connect_errno()) {
		printf("Falló la conexión: %s\n", mysqli_connect_error());
		exit();
	}
	
	$MAILDEST="soporte@contigoo.es";
	
	$MAILSERV="smtp.dondominio.com";
	$MAILFROM="informes@kitel.es";
	$MAILUSER="informes@kitel.es";
	$MAILPASS="5gdaCd13?";
	
	$MAILSUBJECT="TOTALES de la ".gethostname()." del dia ".$dia." del mes ".$mes."\n";
	$MAILBODY="Se adjunta informe de TOTALES de ".gethostname()." DEL DIA ".$dia."  del mes de ".$mes."\n";
		
 	

	$archivo_excel="/tmp/consumo TOTALES ".gethostname()."_".$dia." mes ".$mes.".xls";
	$workbook = new writeexcel_workbook($archivo_excel);
	$worksheet_llamadas = &$workbook->addworksheet("llamadas");
	
	$ultima_linea_llamadas=0;
	
	
	$worksheet_llamadas->write($ultima_linea_llamadas,0,"Llamadas");
	$worksheet_llamadas->write($ultima_linea_llamadas,1,"Segundos");
	
	$ultima_linea_llamadas++;
   
	if ($result = mysqli_query($link, "SELECT count(billsec),sum(billsec) FROM asteriskcdrdb.cdr where   calldate between \"".$hora_inicio."\" and \"".$hora_fin."\" and disposition ='Answered' and src<>'912529523' and length(dst)>6"))
		{
       
			while ($row=mysqli_fetch_row($result)) {
				$llamada=$row[0];
				$segundos=$row[1];
				
				
				
					
						$worksheet_llamadas->write_string($ultima_linea_llamadas,0,$llamada);
						$worksheet_llamadas->write_string($ultima_linea_llamadas,1,$segundos);
						
						$ultima_linea_llamadas++;
						
						
						
				
					
			}
		}
	
				
			
	$workbook->close();
	
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
	//$mail->addAddress($MAILDEST2);	
  //  $mail->addAddress($MAILDEST3);
	$mail->addAttachment($archivo_excel);         // Add attachments
	$mail->isHTML(true);                                  // Set email format to HTML
	
	$mail->Subject = $MAILSUBJECT;
	$mail->Body    = $MAILBODY;
		
	if(!$mail->send()) {
		echo 'Message could not be sent.';
		echo 'Mailer Error: ' . $mail->ErrorInfo;
	} 
	
	unlink($archivo_excel);
    mysqli_close($link);
?>
