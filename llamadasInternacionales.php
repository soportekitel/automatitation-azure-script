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
	
	$inicio=$argv[1];
	$fin=$argv[2];
	
	$hora_inicio=date("Y/m/d ").$inicio.":00:00";
	$hora_fin=date("Y/m/d ").$fin.":59:59";
	
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
	$MAILSUBJECT="Informe de llamadas Extranjero PROCOBRO MAS 300 SEGUNDOS ".fecha_visible($hora_inicio)."\n";
	$MAILBODY="Se adjunta informe de llamadas al Extranjero en el día actual\n";

  
	$archivo_excel="/tmp/LlamadasExtranjero_AZURE".date("d-m-Y").".xls";
	$workbook = new writeexcel_workbook($archivo_excel);
	$worksheet_buzon = &$workbook->addworksheet("Llamadas");
	
	
	$ultima_linea_buzon=0;
	
	$worksheet_buzon->write($ultima_linea_buzon,0,"Fecha");
	$worksheet_buzon->write($ultima_linea_buzon,1,"Hora");
	$worksheet_buzon->write($ultima_linea_buzon,2,"Teléfono");
	$worksheet_buzon->write($ultima_linea_buzon,3,"Destino");
	$worksheet_buzon->write($ultima_linea_buzon,4,"Duración");
	$ultima_linea_buzon++;
	
	
	$ultima_linea_otras++;
	
	$query="select calldate,src,lastapp,dst,billsec from asteriskcdrdb.cdr  where calldate between \"".$hora_inicio."\" and \"".$hora_fin."\"  and billsec>300 and  disposition ='Answered' and dst like '00%'";
	//$query="select calldate,src,lastapp,dst,billsec from asteriskcdrdb.cdr  where calldate between \"".$hora_inicio."\" and \"".$hora_fin."\"  and billsec>600 and  disposition ='Answered'";
	$result=mysql_query($query,$link);
	while ($row=mysql_fetch_row($result)) {
		$calldate=$row[0];
		$telefono=$row[1];
		$lastapp=$row[2];
		$dst=$row[3];
		$billsec=$row[4];
		
				$worksheet_buzon->write($ultima_linea_buzon,0,fecha_visible($calldate));
				$worksheet_buzon->write($ultima_linea_buzon,1,substr($calldate,11));
				$worksheet_buzon->write_string($ultima_linea_buzon,2,$telefono);
				$worksheet_buzon->write_string($ultima_linea_buzon,3,$dst);
			    $worksheet_buzon->write_string($ultima_linea_buzon,4,$billsec);
				$ultima_linea_buzon++;
				
			
	}
		
	$workbook->close();
	
	if ($ultima_linea_buzon>1)
	{
	
	
	
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
		
	   
		$mail->addAttachment($archivo_excel);         // Add attachments
		$mail->isHTML(true);                                  // Set email format to HTML
		
		$mail->Subject = $MAILSUBJECT;
		$mail->Body    = $MAILBODY;
			
		if(!$mail->send()) {
			echo 'Message could not be sent.';
			echo 'Mailer Error: ' . $mail->ErrorInfo;
		} 
	}
	unlink($archivo_excel);

?>
