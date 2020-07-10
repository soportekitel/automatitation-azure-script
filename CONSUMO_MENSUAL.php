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
	
	
	
	
	$mes_anterior = date('m', strtotime('-1 month'));
	$anio_anterior = date('Y', strtotime('-1 year'));
	$mes=date('m');
	$anio=date('Y');
	if (date('m') == "01")
	{
		$hora_inicio=$anio_anterior."-12-01 00:00:00";
		$hora_fin=$anio_anterior."-12-31 23:59:59";
	}
	else
	{
		$hora_inicio=$anio."-".$mes_anterior."-01 00:00:00";
		$hora_fin=$anio."-".$mes_anterior."-31 23:59:59";
	}	
	
	
	$DB_USER="admin";
	$DB_PASS="$$5gdaCd13$$";
	$DB_HOST="localhost";
	$link=mysql_connect($DB_HOST,$DB_USER,$DB_PASS) or die ("Error: ".mysql_error());
	
	$MAILDEST="silvia.martinez@kitel.es";
	
	$MAILSERV="smtp.dondominio.com";
	$MAILFROM="informes@kitel.es";
	$MAILUSER="informes@kitel.es";
	$MAILPASS="5gdaCd13?";
	
	$MAILSUBJECT="CONSUMO GRUPO DIGITAL del ".$hora_inicio." al ".$hora_fin."\n";
	$MAILBODY="Se adjunta informe de Consumo de GRUPO DIGITAL ";
		
 	

	$archivo_excel="/tmp/consumo GRUPO DIGITAL_".$hora_inicio.".xls";
	$workbook = new writeexcel_workbook($archivo_excel);
	$worksheet_llamadas_fijos8 = &$workbook->addworksheet("Fijos 8");
	$ultima_linea_fijos8=0;
	$duracion_fijos8=0;
	$worksheet_llamadas_fijos8->write($ultima_linea_fijos8,0,"Fecha");
	$worksheet_llamadas_fijos8->write($ultima_linea_fijos8,1,"Origen");
	$worksheet_llamadas_fijos8->write($ultima_linea_fijos8,2,"Destino");
	$worksheet_llamadas_fijos8->write($ultima_linea_fijos8,3,"Estado");
	$worksheet_llamadas_fijos8->write($ultima_linea_fijos8,4,"Duracion");
	$ultima_linea_fijos8++;
	
	$query="SELECT calldate, src, dst, disposition, billsec,channel FROM asteriskcdrdb.cdr where   calldate between \"".$hora_inicio."\" and \"".$hora_fin."\" and disposition ='Answered' and src<>'912529523' and  disposition ='Answered' and dst >= '81%' and dst <= '899%'";
	
	$result=mysql_query($query,$link);
	
	while ($row=mysql_fetch_row($result)) {
		$calldate=$row[0];
		$telefono=$row[1];
		$dst=$row[2];
		$estado=$row[3];
		$duracion=$row[4];
		$worksheet_llamadas_fijos8->write_string($ultima_linea_fijos8,0,$calldate);
		$worksheet_llamadas_fijos8->write_string($ultima_linea_fijos8,1,$telefono);
		$worksheet_llamadas_fijos8->write_string($ultima_linea_fijos8,2,$dst);
		$worksheet_llamadas_fijos8->write_string($ultima_linea_fijos8,3,$estado);
		$worksheet_llamadas_fijos8->write_string($ultima_linea_fijos8,4,$duracion);
		$duracion_fijos8=$duracion_fijos8+intval($duracion);
		$ultima_linea_fijos8++;
				
			
	}
		
	
	
	$worksheet_llamadas_fijos9 = &$workbook->addworksheet("Fijos 9");
	$ultima_linea_fijos9=0;
	$duracion_fijos9=0;
	$worksheet_llamadas_fijos9->write($ultima_linea_fijos9,0,"Fecha");
	$worksheet_llamadas_fijos9->write($ultima_linea_fijos9,1,"Origen");
	$worksheet_llamadas_fijos9->write($ultima_linea_fijos9,2,"Destino");
	$worksheet_llamadas_fijos9->write($ultima_linea_fijos9,3,"Estado");
	$worksheet_llamadas_fijos9->write($ultima_linea_fijos9,4,"Duracion");
	$ultima_linea_fijos9++;
	
	$query="SELECT calldate, src, dst, disposition, billsec,channel FROM asteriskcdrdb.cdr where   calldate between \"".$hora_inicio."\" and \"".$hora_fin."\" and disposition ='Answered' and src<>'912529523'  and dst >= '91%' and dst <= '999%'";
	echo "sql:".$query."\n";
	
	$result=mysqli_query($query,$link);
	echo "resultado:".mysql_num_rows($result)." filas\n";
	while ($row=mysql_fetch_row($result)) {
		$calldate=$row[0];
		$telefono=$row[1];
		$dst=$row[2];
		$estado=$row[3];
		$duracion=$row[4];
		$worksheet_llamadas_fijos9->write_string($ultima_linea_fijos9,0,$calldate);
		$worksheet_llamadas_fijos9->write_string($ultima_linea_fijos9,1,$telefono);
		$worksheet_llamadas_fijos9->write_string($ultima_linea_fijos9,2,$dst);
		$worksheet_llamadas_fijos9->write_string($ultima_linea_fijos9,3,$estado);
		$worksheet_llamadas_fijos9->write_string($ultima_linea_fijos9,4,$duracion);
		$ultima_linea_fijos9++;
		$duracion_fijos9=$duracion_fijos9+intval($duracion);
		
		echo "num".$worksheet_llamadas_fijos9."\n";	
			
	}
	
	$worksheet_totales= &$workbook->addworksheet("TOTALES");
	$worksheet_totales->write(0,0,"TIPO");
	$worksheet_totales->write(0,1,"LLAMADAS");
	$worksheet_totales->write(0,2,"SEGUNDOS");
	$worksheet_totales->write(1,0,"Fijos 8");
	$worksheet_totales->write(1,1,$ultima_linea_fijos8);
	$worksheet_totales->write(1,2,$duracion_fijos8);
	$worksheet_totales->write(2,0,"Fijos 9");
	$worksheet_totales->write(2,1,$ultima_linea_fijos9);
	$worksheet_totales->write(2,2,$duracion_fijos9);
				
			
	$workbook->close();
	
	//Envio de mail
	
	$mail = new PHPMailer;
	
	//$mail->SMTPDebug = 3;
	
	$mail->isSMTP();                                      // Set mailer to use SMTP
	$mail->Host = $MAILSERV;  // Specify main and backup SMTP servers
	$mail->SMTPAuth = true;                               // Enable SMTP authentication
	$mail->Username = $MAILUSER;                 // SMTP username
	$mail->Password = $MAILPASS;                           // SMTP password
	//$mail->SMTPSecure = 'tls';                            // Enable TLS encryption, `ssl` also accepted
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

?>
