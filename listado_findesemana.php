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
	
	$hora_inicio=date("Y/m/d ",strtotime("-3 day")).$inicio.":00:00";
		
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
	
	$MAILSUBJECT="Listado Fin de semana  ".gethostname()." del ".fecha_visible($hora_inicio)." ".hora_visible($hora_inicio)." al ".fecha_visible($hora_fin)." ".hora_visible($hora_fin)."\n";
	$MAILBODY="Se adjunta listado de todas las llamadas de ".gethostname()." entre ".fecha_visible($hora_inicio)." ".hora_visible($hora_inicio)." y ".fecha_visible($hora_fin)." ".hora_visible($hora_fin)."\n";
		


	$archivo_excel="/tmp/listado_llamadas_findesemana_".gethostname().".xls";
	$workbook = new writeexcel_workbook($archivo_excel);
	$worksheet_buzon = &$workbook->addworksheet("Llamadas");

	
	$ultima_linea_buzon=0;

	$worksheet_buzon->write($ultima_linea_buzon,0,"Fecha");
	$worksheet_buzon->write($ultima_linea_buzon,1,"Hora");
	$worksheet_buzon->write($ultima_linea_buzon,2,"Teléfono");
	$worksheet_buzon->write($ultima_linea_buzon,3,"Destino");
	$worksheet_buzon->write($ultima_linea_buzon,4,"Clid");
	$worksheet_buzon->write($ultima_linea_buzon,5,"Estado");
	$worksheet_buzon->write($ultima_linea_buzon,6,"Duración");
	$ultima_linea_buzon++;
	
	
	


if ($result = mysqli_query($link, "select calldate,src,lastapp,dst,clid,disposition,duration from asteriskcdrdb.cdr c1 where  c1.calldate>=\"".$hora_inicio."\" and c1.calldate<\"".$hora_fin."\" and src<>'912529523'"))
		{
         
			while ($row=mysqli_fetch_row($result)) {
				$calldate=$row[0];
				$telefono=$row[1];
				$lastapp=$row[2];
				$dst=$row[3];
				$did=$row[4];
				$estado=$row[5];
				$duration=$row[6];
	
				$worksheet_buzon->write($ultima_linea_buzon,0,fecha_visible($calldate));
				$worksheet_buzon->write($ultima_linea_buzon,1,substr($calldate,11));
				$worksheet_buzon->write_string($ultima_linea_buzon,2,$telefono);
				$worksheet_buzon->write_string($ultima_linea_buzon,3,$dst);
				$worksheet_buzon->write_string($ultima_linea_buzon,4,$did);
				$worksheet_buzon->write_string($ultima_linea_buzon,5,$estado);
				$worksheet_buzon->write_string($ultima_linea_buzon,6,$duration);
				$ultima_linea_buzon++;
			}	
		mysqli_free_result($result);
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
