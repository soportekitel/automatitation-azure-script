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



	
	
	$MAILDEST="silvia.martinez@kitel.es";
	
	$MAILSERV="smtp.dondominio.com";
	$MAILFROM="informes@kitel.es";
	$MAILUSER="informes@kitel.es";
	$MAILPASS="5gdaCd13?";
	
	$MAILSUBJECT="CONSUMO PBX_PRUEBAS del mes ".date('m', strtotime('-1 month'))."\n";
	$MAILBODY="Se adjunta informe de Consumo de PBX_PRUEBAS ";
		
 	

	$archivo_excel="/tmp/consumo PBX_PRUEBAS_".date('m', strtotime('-1 month')).".xls";
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
	

	
	if ($result = mysqli_query($link, "SELECT calldate, src, dst, disposition, billsec,channel FROM asteriskcdrdb.cdr where   calldate between \"".$hora_inicio."\" and \"".$hora_fin."\" and Length(dst)>6 and disposition ='Answered' and src<>'912529523' and  disposition ='Answered' and dst >= '81%' and dst <= '899%'")) {
   


    
	
	
	while ($row=mysqli_fetch_row($result)) {
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
		
	mysqli_free_result($result);
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
	
	if ($result = mysqli_query($link, "SELECT calldate, src, dst, disposition, billsec,channel FROM asteriskcdrdb.cdr where   calldate between \"".$hora_inicio."\" and \"".$hora_fin."\" and Length(dst)>6 and disposition ='Answered' and src<>'912529523' and  disposition ='Answered' and dst >= '91%' and dst <= '999%'")) 
	{
		


	
		while ($row=mysqli_fetch_row($result)) {
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
			
			
				
		}
		mysqli_free_result($result);
	}
	
	
	$worksheet_llamadas_900 = &$workbook->addworksheet("900");
	$ultima_linea_900=0;
	$duracion_900=0;
	$worksheet_llamadas_900->write($ultima_linea_900,0,"Fecha");
	$worksheet_llamadas_900->write($ultima_linea_900,1,"Origen");
	$worksheet_llamadas_900->write($ultima_linea_900,2,"Destino");
	$worksheet_llamadas_900->write($ultima_linea_900,3,"Estado");
	$worksheet_llamadas_900->write($ultima_linea_900,4,"Duracion");
	$ultima_linea_900++;
	

	
	if ($result = mysqli_query($link, "SELECT calldate, src, dst, disposition, billsec,channel FROM asteriskcdrdb.cdr where   calldate between \"".$hora_inicio."\" and \"".$hora_fin."\" and Length(dst)>6 and disposition ='Answered' and src<>'912529523' and  disposition ='Answered' and dst like '900%'")) {
    

	while ($row=mysqli_fetch_row($result)) {
		$calldate=$row[0];
		$telefono=$row[1];
		$dst=$row[2];
		$estado=$row[3];
		$duracion=$row[4];
		$worksheet_llamadas_900->write_string($ultima_linea_900,0,$calldate);
		$worksheet_llamadas_900->write_string($ultima_linea_900,1,$telefono);
		$worksheet_llamadas_900->write_string($ultima_linea_900,2,$dst);
		$worksheet_llamadas_900->write_string($ultima_linea_900,3,$estado);
		$worksheet_llamadas_900->write_string($ultima_linea_900,4,$duracion);
		$duracion_900=$duracion_900+intval($duracion);
		$ultima_linea_900++;
				
			
	}
		
	mysqli_free_result($result);
}
	
$worksheet_llamadas_90x = &$workbook->addworksheet("90X");
	$ultima_linea_90x=0;
	$duracion_90x=0;
	$worksheet_llamadas_90x->write($ultima_linea_90x,0,"Fecha");
	$worksheet_llamadas_90x->write($ultima_linea_90x,1,"Origen");
	$worksheet_llamadas_90x->write($ultima_linea_90x,2,"Destino");
	$worksheet_llamadas_90x->write($ultima_linea_90x,3,"Estado");
	$worksheet_llamadas_90x->write($ultima_linea_90x,4,"Duracion");
	$ultima_linea_90x++;
	

	
	if ($result = mysqli_query($link, "SELECT calldate, src, dst, disposition, billsec,channel FROM asteriskcdrdb.cdr where   calldate between \"".$hora_inicio."\" and \"".$hora_fin."\" and Length(dst)>6 and disposition ='Answered' and src<>'912529523' and  disposition ='Answered' and dst >= '901%' and dst <= '91%'")) {
   

	while ($row=mysqli_fetch_row($result)) {
		$calldate=$row[0];
		$telefono=$row[1];
		$dst=$row[2];
		$estado=$row[3];
		$duracion=$row[4];
		$worksheet_llamadas_90x->write_string($ultima_linea_90x,0,$calldate);
		$worksheet_llamadas_90x->write_string($ultima_linea_90x,1,$telefono);
		$worksheet_llamadas_90x->write_string($ultima_linea_90x,2,$dst);
		$worksheet_llamadas_90x->write_string($ultima_linea_90x,3,$estado);
		$worksheet_llamadas_90x->write_string($ultima_linea_90x,4,$duracion);
		$duracion_90x=$duracion_90x+intval($duracion);
		$ultima_linea_90x++;
				
			
	}
		
	mysqli_free_result($result);
}
		
$worksheet_llamadas_80x = &$workbook->addworksheet("80X");
	$ultima_linea_80x=0;
	$duracion_80x=0;
	$worksheet_llamadas_80x->write($ultima_linea_80x,0,"Fecha");
	$worksheet_llamadas_80x->write($ultima_linea_80x,1,"Origen");
	$worksheet_llamadas_80x->write($ultima_linea_80x,2,"Destino");
	$worksheet_llamadas_80x->write($ultima_linea_80x,3,"Estado");
	$worksheet_llamadas_80x->write($ultima_linea_80x,4,"Duracion");
	$ultima_linea_80x++;
	

	
	if ($result = mysqli_query($link, "SELECT calldate, src, dst, disposition, billsec,channel FROM asteriskcdrdb.cdr where   calldate between \"".$hora_inicio."\" and \"".$hora_fin."\" and Length(dst)>6 and disposition ='Answered' and src<>'912529523' and  disposition ='Answered' and dst >= '800%' and dst <= '809%'")) {
    

	while ($row=mysqli_fetch_row($result)) {
		$calldate=$row[0];
		$telefono=$row[1];
		$dst=$row[2];
		$estado=$row[3];
		$duracion=$row[4];
		$worksheet_llamadas_80x->write_string($ultima_linea_80x,0,$calldate);
		$worksheet_llamadas_80x->write_string($ultima_linea_80x,1,$telefono);
		$worksheet_llamadas_80x->write_string($ultima_linea_80x,2,$dst);
		$worksheet_llamadas_80x->write_string($ultima_linea_80x,3,$estado);
		$worksheet_llamadas_80x->write_string($ultima_linea_80x,4,$duracion);
		$duracion_80x=$duracion_80x+intval($duracion);
		$ultima_linea_80x++;
				
			
	}
		
	mysqli_free_result($result);
}
		
$worksheet_llamadas_moviles = &$workbook->addworksheet("Moviles");
	$ultima_linea_moviles=0;
	$duracion_moviles=0;
	$worksheet_llamadas_moviles->write($ultima_linea_moviles,0,"Fecha");
	$worksheet_llamadas_moviles->write($ultima_linea_moviles,1,"Origen");
	$worksheet_llamadas_moviles->write($ultima_linea_moviles,2,"Destino");
	$worksheet_llamadas_moviles->write($ultima_linea_moviles,3,"Estado");
	$worksheet_llamadas_moviles->write($ultima_linea_moviles,4,"Duracion");
	$ultima_linea_moviles++;
	

	
	if ($result = mysqli_query($link, "SELECT calldate, src, dst, disposition, billsec,channel FROM asteriskcdrdb.cdr where   calldate between \"".$hora_inicio."\" and \"".$hora_fin."\" and Length(dst)>6 and disposition ='Answered' and src<>'912529523' and  disposition ='Answered' and dst >= '6%' and dst <= '8%'")) {
   
	while ($row=mysqli_fetch_row($result)) {
		$calldate=$row[0];
		$telefono=$row[1];
		$dst=$row[2];
		$estado=$row[3];
		$duracion=$row[4];
		$worksheet_llamadas_moviles->write_string($ultima_linea_moviles,0,$calldate);
		$worksheet_llamadas_moviles->write_string($ultima_linea_moviles,1,$telefono);
		$worksheet_llamadas_moviles->write_string($ultima_linea_moviles,2,$dst);
		$worksheet_llamadas_moviles->write_string($ultima_linea_moviles,3,$estado);
		$worksheet_llamadas_moviles->write_string($ultima_linea_moviles,4,$duracion);
		$duracion_moviles=$duracion_moviles+intval($duracion);
		$ultima_linea_moviles++;
				
			
	}
		
	mysqli_free_result($result);
}	
$worksheet_llamadas_interna = &$workbook->addworksheet("Internacional");
	$ultima_linea_interna=0;
	$duracion_interna=0;
	$worksheet_llamadas_interna->write($ultima_linea_interna,0,"Fecha");
	$worksheet_llamadas_interna->write($ultima_linea_interna,1,"Origen");
	$worksheet_llamadas_interna->write($ultima_linea_interna,2,"Destino");
	$worksheet_llamadas_interna->write($ultima_linea_interna,3,"Estado");
	$worksheet_llamadas_interna->write($ultima_linea_interna,4,"Duracion");
	$ultima_linea_interna++;
	

	
	if ($result = mysqli_query($link, "SELECT calldate, src, dst, disposition, billsec,channel FROM asteriskcdrdb.cdr where   calldate between \"".$hora_inicio."\" and \"".$hora_fin."\" and Length(dst)>6 and disposition ='Answered' and src<>'912529523' and  disposition ='Answered' and dst like '00%'"))
		{
  
	while ($row=mysqli_fetch_row($result)) {
		$calldate=$row[0];
		$telefono=$row[1];
		$dst=$row[2];
		$estado=$row[3];
		$duracion=$row[4];
		$worksheet_llamadas_interna->write_string($ultima_linea_interna,0,$calldate);
		$worksheet_llamadas_interna->write_string($ultima_linea_interna,1,$telefono);
		$worksheet_llamadas_interna->write_string($ultima_linea_interna,2,$dst);
		$worksheet_llamadas_interna->write_string($ultima_linea_interna,3,$estado);
		$worksheet_llamadas_interna->write_string($ultima_linea_interna,4,$duracion);
		$duracion_interna=$duracion_interna+intval($duracion);
		$ultima_linea_interna++;
				
			
	}
		
	mysqli_free_result($result);
}	
	

	$worksheet_totales= &$workbook->addworksheet("TOTALES");
	$worksheet_totales->write(0,0,"TIPO");
	$worksheet_totales->write(0,1,"LLAMADAS");
	$worksheet_totales->write(0,2,"SEGUNDOS");
	$worksheet_totales->write(0,3,"MINUTOS");
	$worksheet_totales->write(1,0,"Fijos 8");
	$worksheet_totales->write(1,1,$ultima_linea_fijos8-1);
	$worksheet_totales->write(1,2,$duracion_fijos8);
	$worksheet_totales->write(1,3,$duracion_fijos8/60);
	$worksheet_totales->write(2,0,"Fijos 9");
	$worksheet_totales->write(2,1,$ultima_linea_fijos9-1);
	$worksheet_totales->write(2,2,$duracion_fijos9);
	$worksheet_totales->write(2,3,$duracion_fijos9/60);
	$worksheet_totales->write(3,0,"900");
	$worksheet_totales->write(3,1,$ultima_linea_900-1);
	$worksheet_totales->write(3,2,$duracion_900);	
	$worksheet_totales->write(3,3,$duracion_900/60);	
	$worksheet_totales->write(4,0,"90X");
	$worksheet_totales->write(4,1,$ultima_linea_90x-1);
	$worksheet_totales->write(4,2,$duracion_90x);	
	$worksheet_totales->write(4,3,$duracion_90x/60);
	$worksheet_totales->write(5,0,"80X");
	$worksheet_totales->write(5,1,$ultima_linea_80x-1);
	$worksheet_totales->write(5,2,$duracion_80x);	
	$worksheet_totales->write(5,3,$duracion_80x/60);
	$worksheet_totales->write(6,0,"Moviles");
	$worksheet_totales->write(6,1,$ultima_linea_moviles-1);
	$worksheet_totales->write(6,2,$duracion_moviles);
	$worksheet_totales->write(6,3,$duracion_moviles/60);
	$worksheet_totales->write(7,0,"Internacionales");
	$worksheet_totales->write(7,1,$ultima_linea_interna-1);
	$worksheet_totales->write(7,2,$duracion_interna);
	$worksheet_totales->write(7,3,$duracion_interna/60);
	$total_llamadas=$ultima_linea_fijos8-1+$ultima_linea_fijos9-1+$ultima_linea_900-1+$ultima_linea_90x-1+$ultima_linea_80x-1+$ultima_linea_moviles-1+$ultima_linea_interna-1;
	$total_segundos=$duracion_fijos8+$duracion_fijos9+$duracion_900+$duracion_90x+$duracion_80x+$duracion_moviles+$duracion_interna;
	
	$worksheet_totales->write(8,0,"Totales");
	$worksheet_totales->write(8,1,$total_llamadas);
	$worksheet_totales->write(8,2,$total_segundos);
	$worksheet_totales->write(8,3,$total_segundos/60);
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
