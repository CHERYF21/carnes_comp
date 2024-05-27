function buscarRegistros() {
    var fecha_inicio = $('#date1').val();
    var fecha_fin = $('#date2').val();
    var sede_admin = $('#sede').val();
    console.log('Fecha Inicio:', fecha_inicio, 'Fecha Fin:', fecha_fin);
    document.getElementById("loaderBuscar").style.display = "block";

    $.ajax({
        url: '/generar_datos',
        type: 'GET',
        data: {
            fecha_inicio: fecha_inicio,
            fecha_fin: fecha_fin,
            sede_admin: sede_admin
        },
        xhrFields: {
            withCredentials: true
        },
        crossDomain: true,
        success: function(response) {
            $('#tablaRegistros tbody').empty();
            document.getElementById("loaderBuscar").style.display = "none";

            if (response.status === 'success') {
                response.data.forEach(function(row) {
                    var newRow = '<tr>' +
                        '<td align="center">' + row.NombreTienda + '</td>' +
                        '<td align="center">' + row.NombreVendedor + '</td>' +
                        '<td align="center">' + row.PesoTotal + '</td>' +
                        '<td align="center">' + row.Porcentaje + '%</td>' +
                        '</tr>';
                    $('#tablaRegistros tbody').append(newRow);

                    if(response.ultima_insercion){
                        document.getElementById('ultimaActualizacion').textContent = response.ultima_insercion;
                    }

                });
                console.log(response.data);
            } else {
                console.error('Error en la respuesta:', response.message);
                alert('Error: ' + response.message);
            }
        },
        error: function(xhr, status, error) {
            document.getElementById("loaderBuscar").style.display = "none";
            console.error('Error al buscar registros:', error, 'Response:', xhr.responseText);
            alert('Error al buscar registros: ' + xhr.responseText);
        }
    });
}


function exportToExcel() {
    // Generar la solicitud para exportar a CSV
    document.getElementById("loaderExportar").style.display = "block";
    $.ajax({
        url: '/exportar_csv',
        type: 'POST',
        data: {
            fecha_inicio: $('#date1').val(),
            fecha_fin: $('#date2').val()
            
        },
        success: function(data) {
            // Redirigir al usuario para descargar el archivo CSV
            document.getElementById("loaderExportar").style.display = "none";
            var blob = new Blob([data], { type: 'text/csv' });
            var link = document.createElement('a');
            link.href = window.URL.createObjectURL(blob);
            link.download = 'registrosCarnes.csv';
            link.click();
        },
        error: function(xhr, status, error) {
            console.error('Error al exportar a CSV:', error);
            $('#exportarBtn').html('Exportar a Excel').prop('disabled', false);
        }
    });
}
