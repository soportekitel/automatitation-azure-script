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
		$hora_inicio=date("Y/m/d ",strtotime("-7 day")).$inicio.":00:00";
		
	} else {
		$hora_inicio=date("Y/m/d ",strtotime("-1 day")).$inicio.":00:00";
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
	$MAILSUBJECT="Informe de llamadas ".gethostname();
	$MAILBODY="Se adjunta informe de llamadas de ".gethostname()." entre ".$hora_inicio." y ".$hora_fin."\n";
		


	$fechainicio=date("d/m/Y ",strtotime("-7 day"));
	$fechainicio2=str_replace("/", "-", $fechainicio);
	$archivo_excel="/tmp/Llamadas ".gethostname()." entre ".str_replace("/", "-",fecha_visible($hora_inicio))." y ".str_replace("/", "-",fecha_visible($hora_fin)).".xls";

	
	$workbook = new writeexcel_workbook($archivo_excel);
	$worksheet_Entrantes = &$workbook->addworksheet("Entrantes");
	$worksheet_Salientes = &$workbook->addworksheet("Salientes");

	$ultima_linea_Entrantes=0;
	$ultima_linea_Salientes=0;
	$worksheet_Entrantes->write($ultima_linea_Entrantes,0,"Fecha");
	$worksheet_Entrantes->write($ultima_linea_Entrantes,1,"Hora");
	$worksheet_Entrantes->write($ultima_linea_Entrantes,2,"Teléfono");
	$worksheet_Entrantes->write($ultima_linea_Entrantes,3,"Destino");
	$worksheet_Entrantes->write($ultima_linea_Entrantes,4,"Tiempo");
	$worksheet_Entrantes->write($ultima_linea_Entrantes,5,"Estado");
	$ultima_linea_Entrantes++;
	
	$worksheet_Salientes->write($ultima_linea_Salientes,0,"Fecha/Hora");
	$worksheet_Salientes->write($ultima_linea_Salientes,1,"Hora");
	$worksheet_Salientes->write($ultima_linea_Salientes,2,"Teléfono");
	$worksheet_Salientes->write($ultima_linea_Salientes,3,"Destino");
	$worksheet_Salientes->write($ultima_linea_Salientes,4,"Tiempo");
    $worksheet_Salientes->write($ultima_linea_Salientes,5,"Estado");
	$ultima_linea_Salientes++;
	
//	$query="select calldate, src, dst, billsec, disposition  from asteriskcdrdb.cdr  where channel like '%bubbl%' and clid not like '%OFICI%' and calldate >=\"".$hora_inicio."\" and calldate<\"".$hora_fin."\"";
	if ($result = mysqli_query($link, "select calldate, src, dst, billsec, disposition  from asteriskcdrdb.cdr  where channel like '%bubbl%' and clid not like '%OFICI%' and calldate >=\"".$hora_inicio."\" and calldate<\"".$hora_fin."\""))
		{
       
				while ($row=mysqli_fetch_row($result))
				{
					$calldate=$row[0];
					$src=$row[1];
					$dst=$row[2];
					$billsec=$row[3];
					$disposition=$row[4];
					$worksheet_Entrantes->write($ultima_linea_Entrantes,0,fecha_visible($calldate));
					$worksheet_Entrantes->write($ultima_linea_Entrantes,1,substr($calldate,11));
					$worksheet_Entrantes->write($ultima_linea_Entrantes,2,$src);
					$worksheet_Entrantes->write($ultima_linea_Entrantes,3,$dst);
					$worksheet_Entrantes->write($ultima_linea_Entrantes,4,$billsec);
					$worksheet_Entrantes->write($ultima_linea_Entrantes,5,$disposition);
					$ultima_linea_Entrantes++;
				
				}					
		mysqli_free_result($result);
	}
 	//$query="select calldate, src, dst, billsec, disposition from asteriskcdrdb.cdr where outbound_cnum > 1 and calldate >=\"".$hora_inicio."\" and calldate<\"".$hora_fin."\"";
       if ($result = mysqli_query($link, "select calldate, src, dst, billsec, disposition from asteriskcdrdb.cdr where outbound_cnum > 1 and calldate >=\"".$hora_inicio."\" and calldate<\"".$hora_fin."\""))
		{
       
				while ($row=mysqli_fetch_row($result))
				{
					$calldate=$row[0];
					$src=$row[1];
					$dst=$row[2];
					$billsec=$row[3];
					$disposition=$row[4];

                    $worksheet_Salientes->write($ultima_linea_Salientes,0,fecha_visible($calldate));
                	$worksheet_Salientes->write($ultima_linea_Salientes,1,substr($calldate,11));
                    $worksheet_Salientes->write($ultima_linea_Salientes,2,$src);
                    $worksheet_Salientes->write($ultima_linea_Salientes,3,$dst);
                    $worksheet_Salientes->write($ultima_linea_Salientes,4,$billsec);
                    $worksheet_Salientes->write($ultima_linea_Salientes,5,$disposition);
                    $ultima_linea_Salientes++;
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
