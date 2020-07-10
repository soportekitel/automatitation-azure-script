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
	if ($inicio=="" || $fin=="") {
		echo "Uso ".$argv[0]." hora_inicio hora_fin\n";
		exit(1);
	}
	
	if ($inicio>=$fin) {
		$hora_inicio=date("Y/m/d ",strtotime("-1 day")).$inicio.":00:00";
		
	} else {
		$hora_inicio=date("Y/m/d ").$inicio.":00:00";
	}
	$hora_fin=date("Y/m/d ").$fin.":00:00";
	
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
	$MAILSUBJECT="Informe de llamadas de ".gethostname()." del ".fecha_visible($hora_inicio)." ".hora_visible($hora_inicio)." y ".fecha_visible($hora_fin)." ".hora_visible($hora_fin)."\n";
	$MAILBODY="Se adjunta informe de ".gethostname()." de llamadas a buzones de voz y llamadas perdidas entre ".fecha_visible($hora_inicio)." ".hora_visible($hora_inicio)." y ".fecha_visible($hora_fin)." ".hora_visible($hora_fin)."\n";
		


	$archivo_excel="/tmp/Llamadas perdidas ".date("d-m-Y H",strtotime("-1 day")).".xls";
	$workbook = new writeexcel_workbook($archivo_excel);
	$worksheet_buzon = &$workbook->addworksheet("Llamadas a Buzón de Voz");
	$worksheet_otras = &$workbook->addworksheet("Perdidas sin Buzón de Voz");
	$worksheet_colgadas = &$workbook->addworksheet("Perdidas Colgadas");
	
	$ultima_linea_buzon=0;
	$ultima_linea_otras=0;
	$ultima_linea_colgadas=0;
	$worksheet_buzon->write($ultima_linea_buzon,0,"Fecha");
	$worksheet_buzon->write($ultima_linea_buzon,1,"Hora");
	$worksheet_buzon->write($ultima_linea_buzon,2,"Teléfono");
	$worksheet_buzon->write($ultima_linea_buzon,3,"Destino");
	$worksheet_buzon->write($ultima_linea_buzon,4,"Teléfono de Destino");
	$ultima_linea_buzon++;
	
	$worksheet_otras->write($ultima_linea_otras,0,"Fecha");
	$worksheet_otras->write($ultima_linea_otras,1,"Hora");
	$worksheet_otras->write($ultima_linea_otras,2,"Teléfono");
	$worksheet_otras->write($ultima_linea_otras,3,"Destino");
	$worksheet_otras->write($ultima_linea_otras,4,"Teléfono de Destino");
	$ultima_linea_otras++;
	
	$worksheet_colgadas->write($ultima_linea_colgadas,0,"Fecha");
	$worksheet_colgadas->write($ultima_linea_colgadas,1,"Hora");
	$worksheet_colgadas->write($ultima_linea_colgadas,2,"Teléfono");
	$worksheet_colgadas->write($ultima_linea_colgadas,3,"Destino");
	$worksheet_colgadas->write($ultima_linea_colgadas,4,"Teléfono de Destino");
	$ultima_linea_colgadas++;
	
	
	$query="select calldate,src,lastapp,dst,clid from asteriskcdrdb.cdr c1 where (c1.dst like \"%vm%\" or c1.lastapp like \"%Playback%\" or (c1.lastapp like \"%Hangup%\" and billsec=0)) and c1.calldate>=\"".$hora_inicio."\" and c1.calldate<\"".$hora_fin."\" and not exists (select * from asteriskcdrdb.cdr c2 where c2.dst=c1.src and c2.calldate>c1.calldate and left(c1.calldate,10)=left(c2.calldate,10)) and src<>'912529523'";
	
	echo $query;
	if ($result = mysqli_query($link, "select calldate,src,lastapp,dst,clid from asteriskcdrdb.cdr c1 where (c1.dst like \"%vm%\" or c1.lastapp like \"%Playback%\" or (c1.lastapp like \"%Hangup%\" and billsec=0)) and c1.calldate>=\"".$hora_inicio."\" and c1.calldate<\"".$hora_fin."\" and not exists (select * from asteriskcdrdb.cdr c2 where c2.dst=c1.src and c2.calldate>c1.calldate and left(c1.calldate,10)=left(c2.calldate,10)) and src<>'912529523'"))
		{
			while ($row=mysqli_fetch_row($result)) {
				$calldate=$row[0];
				$telefono=$row[1];
				$lastapp=$row[2];
				$dst=$row[3];
				$did=$row[4];
				switch ($lastapp) {
					case "VoiceMail": {
						$worksheet_buzon->write($ultima_linea_buzon,0,fecha_visible($calldate));
						$worksheet_buzon->write($ultima_linea_buzon,1,substr($calldate,11));
						$worksheet_buzon->write_string($ultima_linea_buzon,2,$telefono);
						$worksheet_buzon->write_string($ultima_linea_buzon,3,$dst);
						$worksheet_buzon->write_string($ultima_linea_buzon,4,$did);
						$ultima_linea_buzon++;
						
						break;
					}
					case "Hangup":
					{
						$worksheet_colgadas->write($ultima_linea_colgadas,0,fecha_visible($calldate));
						$worksheet_colgadas->write($ultima_linea_colgadas,1,substr($calldate,11));
						$worksheet_colgadas->write_string($ultima_colgadas_buzon,2,$telefono);
						$worksheet_colgadas->write_string($ultima_colgadas_buzon,3,$dst);
						$worksheet_colgadas->write_string($ultima_colgadas_buzon,4,$did);
						$ultima_linea_colgadas++;
						
						break;
					}
					default: {
						$worksheet_otras->write($ultima_linea_otras,0,fecha_visible($calldate));
						$worksheet_otras->write($ultima_linea_otras,1,substr($calldate,11));
						$worksheet_otras->write_string($ultima_linea_otras,2,$telefono);
						$worksheet_otras->write_string($ultima_linea_otras,3,$dst);
						$worksheet_otras->write_string($ultima_linea_otras,4,$did);
						$ultima_linea_otras++;
						
						break;
					}
				}
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
