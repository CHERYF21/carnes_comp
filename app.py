from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file
# from obtener_nombre import obtener_nombre_sede
from datetime import datetime, timedelta
from flask_mysqldb import MySQL
from functools import wraps
import csv
import json



TIEMPO_DE_INACTIVIDAD = 120

app = Flask(__name__)
# conexión a la base de datos
app.config['MYSQL_HOST'] = '192.168.33.251'
app.config['MYSQL_USER'] = 'miguelos'
app.config['MYSQL_PASSWORD'] = 'Mosorio2022$'
app.config['MYSQL_DB'] = 'comp_carnes'
# app.config['MYSQL_HOST'] = '127.0.0.1'
# app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_PASSWORD'] = 'Wmurillo66*'
# app.config['MYSQL_DB'] = 'comp_carnes'

# inicia la base de datos
mysql = MySQL(app)
app.secret_key = 'L4v4quit4*'

# Bloquear rutas si no esta logeado!
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'loggedin' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# inicio de sesion
@app.route('/', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'sede' in request.form:
        username = request.form['username']
        password = request.form['password']
        sede = request.form['sede']
        cur = mysql.connection.cursor()
        cur.execute(
            'SELECT * FROM user_carnes WHERE username = %s AND password = %s AND sede = %s', (username, password, sede))
        account = cur.fetchone()
        print(account)
        cur.close()
        if account:
            session['loggedin'] = True
            session['id'] = account[0]
            # Aquí se establece el nombre de usuario en la sesión
            session['username'] = account[1]
            session['cargo'] = account[3]
            session['sede'] = account[4]
            return redirect(url_for('compensacion'))
        else:
            msg = 'Usuario o contraseña incorrectos'
            cur.close()
    return render_template('inicioSesion.html', msg=msg)

# Cierre de sesion

# Actualiza la marca de tiempo en cada solicitud
@app.before_request
def actualizar_ultima_actividad():
    session.permanent = True
    session.modified = True
    session['ultima_actividad'] = datetime.now()

# Verifica si ha pasado el tiempo de inactividad permitido
@app.before_request
def verificar_timeout():
    ultima_actividad = session.get('ultima_actividad')
    if ultima_actividad is not None:
        tiempo_transcurrido = datetime.now() - ultima_actividad
        if tiempo_transcurrido > timedelta(seconds=TIEMPO_DE_INACTIVIDAD):
            # Si ha pasado el tiempo de inactividad, cierra la sesión del usuario
            session.pop('loggedin', None)
            session.pop('id', None)
            session.pop('username', None)

@app.route('/login/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

# Registrar usuario


@app.route('/registrar', methods=['POST'])
def registro():
    msg = ""
    success = False
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_confirm = request.form['passwordConfirm']
        cargo = request.form['cargo']
        sede = request.form['sede']

        # Validar que las contraseñas coincidan
        if password != password_confirm:
            return jsonify({'success': False, 'msg': 'Las contraseñas no coinciden'})
        try:
            cur = mysql.connection.cursor()
            cur.execute('SELECT id from user_carnes WHERE username=%s',(username,))
            exist_user = cur.fetchone()
            
            if exist_user:
                return jsonify({'success':False, 'msg':'nombre de usuario en uso'})
            
            cur.execute("INSERT INTO user_carnes (username, password, cargo, sede) VALUES (%s, %s, %s, %s)",
                        (username, password, cargo, sede))
            mysql.connection.commit()
            cur.close()
            msg = "Usuario registrado con éxito!"
            success = True
        except Exception as e:
            msg = str(e)
        finally:
            return jsonify({'success': success, 'msg': msg})
        


@app.route('/compensacion')
@login_required
def compensacion():
        return render_template('views/compensacion.html')
    
@app.route('/formUser')
@login_required
def formUser():
    return render_template('views/formUser.html')
 


@app.route('/registrosCarnes')
@login_required
def registrosCarnes():
    return render_template('views/registrosCarnes.html')


@app.route('/generar_datos_grafico', methods=['GET'])
@login_required
def generar_datos_grafico():
    
    cur = mysql.connection.cursor()
    id_co = session['sede']
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    # Convertir fechas a formato YYYY-MM-DD
    fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d").strftime("%Y%m%d")
    fecha_fin = datetime.strptime(fecha_fin, "%Y-%m-%d").strftime("%Y%m%d")

    # Consulta la base de datos para obtener los datos de productividad por caja en el rango de fechas especificado
    cur.execute('''SELECT id_caja, COUNT(*) AS productividad FROM cajeros 
                        WHERE id_co = %s AND fecha_dcto >= %s AND fecha_dcto <= %s 
                        GROUP BY id_caja''', (id_co, fecha_inicio, fecha_fin))
    cajas_productividad = cur.fetchall()

    # Procesa los datos para la gráfica
    cajas_nombres = []
    productividad = []

    for caja in cajas_productividad:
        cajas_nombres.append(caja[0])
        productividad.append(caja[1])

    cur.close()

    # Crear datos en el formato adecuado para Chart.js para productividad por registros
    productividad_data = {
        'labels': cajas_nombres,
        'datasets': [
            {
                'label': 'Productividad por Registros',
                'data': productividad,
                'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                'borderColor': 'rgba(75, 192, 192, 1)',
                'borderWidth': 1,
                'type': 'bar'
            }
        ]
    }

    # Convertir los datos a JSON
    productividad_data_json = json.dumps(productividad_data)

    return productividad_data_json                    


@app.route('/tablas')
@login_required
def tablaRegistros():
    return render_template('views/tablaRegistros.html')

@app.route('/cards')
@login_required
def cards():
    return render_template('views/cardsDashboard.html')

@app.route('/tablauser', methods=['GET'])
@login_required
def tablaUsers():
    return render_template('views/tableUsers.html')


@app.route('/generar_datos', methods=['GET'])
@login_required
def generar_datos():
    if 'loggedin' not in session:
        return jsonify({'status': 'fail', 'message': 'Unauthorized'}), 401

    id_co = session.get('sede')
    
    if not id_co:
        app.logger.error("ID de la sede no encontrado en la sesión.")
        return jsonify({'status': 'fail', 'message': 'ID de la sede no encontrado en la sesión'}), 400

    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')

    if not fecha_inicio or not fecha_fin:
        return jsonify({'status': 'fail', 'message': 'Debes ingresar la fecha'}), 400

    app.logger.info(f'Received dates - Fecha Inicio: {fecha_inicio}, Fecha Fin: {fecha_fin}')

    
        # Convertir fechas al formato necesario
    fecha_inicio_dt = datetime.strptime(fecha_inicio, "%Y-%m-%d")
    fecha_fin_dt = datetime.strptime(fecha_fin, "%Y-%m-%d")
    fecha_inicio_str = fecha_inicio_dt.strftime("%Y%m%d")
    fecha_fin_str = fecha_fin_dt.strftime("%Y%m%d")
        
        # Determinar el tope de registros basado en el día del mes
    dias_mes = fecha_inicio_dt.day
    tabla_tope_registros = 'tope_mes_30' if dias_mes == 30 else 'tope_mes_31'
        
        # Realizar consulta para obtener el tope de registros
    cur = mysql.connection.cursor()
    cur.execute(
        #'SELECT {} FROM topes_sede WHERE nombre_sedes = {}' .format(tabla_tope_registros, id_co))
    'SELECT ' + tabla_tope_registros + ' FROM topes_sede WHERE nombre_sedes = \'' + id_co + '\'')
    tope_registros = cur.fetchone()[0]
    print(tope_registros)
    cur.close()
        
    
    try:
        cur = mysql.connection.cursor()
        query = '''SELECT NombreTienda, NombreVendedor, SUM(Peso) AS PesoTotal,
                   ROUND((SUM(Peso) / %s) * 100 , 2) AS Porcentaje 
                   FROM registroAuxiliar 
                   WHERE NombreTienda = %s AND Fecha >= %s AND Fecha <= %s 
                   GROUP BY NombreTienda, NombreVendedor
                   ORDER BY PesoTotal DESC'''
        cur.execute(query, (tope_registros, id_co, fecha_inicio_str, fecha_fin_str))
        cajas_productividad = cur.fetchall()
        print(cajas_productividad)
        cur.close()

        registros = [{
            'NombreTienda': caja[0],
            'NombreVendedor': caja[1],
            'PesoTotal': caja[2],
            'Porcentaje': caja[3]
        } for caja in cajas_productividad]

        return jsonify({'status': 'success', 'data': registros})
    except Exception as e:
        app.logger.error(f"Error processing request: {str(e)}")
        return jsonify({'status': 'fail', 'message': 'Error al consultar los datos'}), 500

@app.route('/actualizarUser', methods=['POST'])
def actualizarUser():
    if request.method == 'POST':
        cur = mysql.connection.cursor()

        username = request.form['username']
        password = request.form['password']
        password_confirm = request.form['passwordConfirm']
        cargo = request.form['cargo']
        sede = request.form['sede']

        # Validar que las contraseñas coincidan
        if password != password_confirm:
            return jsonify({'success': False, 'msg': 'Las contraseñas no coinciden'})

        try:
            # Obtener el ID del usuario por su nombre
            cur.execute("SELECT id FROM user_carnes WHERE username = %s", (username,))
            user_id = cur.fetchone()[0]
            # Actualizar el usuario utilizando el ID recuperado
            cur.execute("""
                        UPDATE user_carnes
                        SET password=%s, cargo=%s, sede=%s
                        WHERE id=%s
                        """,
                        ( password, cargo, sede, user_id))
            mysql.connection.commit()
            cur.close()
        except Exception as e:
            msg = str(e)
        finally:
            return redirect(url_for('dashboardContent'))
        

@app.route('/dashboardContent', methods=['GET'])
@login_required
def dashboardContent():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM user_carnes")
        users = cur.fetchall()
        cur.close()
        # lista de usuarios 
        user_list = []
        for user in users:
            user_dict = {
                'id':user[0],
                'username':user[1],
                'cargo':user[3],
                'sede':user[4]
            }
            user_list.append(user_dict)
     # funcion al auxiliar con mas ventas 
        cursor = mysql.connection.cursor()
        cursor.execute(
                '''select NombreVendedor, SUM(Peso) AS pesoTotal from registroauxiliar
                group by NombreVendedor
                order by pesoTotal desc
                limit 1;''')
        response = cursor.fetchall()
        cursor.close()
            
        aux_list = []
        for aux in response:
            aux_dict = {
                'NombreVendedor':aux[0],
                'pesoTotal':aux[1]
            }
            aux_list.append(aux_dict)
            
        # ventas del dia actual 
        cursor = mysql.connection.cursor()
        cursor.execute(''' 
                SELECT SUM(Peso) AS Total FROM registroauxiliar 
                WHERE DATE(Fecha) = CURDATE();
                ''')
        resp = cursor.fetchall()
        cursor.close()
        
        dia_list = []
        for dia in resp:
            dia_dict = {
                'Total':dia[0]
            }
            dia_list.append(dia_dict)
        # registros huerfanos 
        cursor = mysql.connection.cursor()
        cursor.execute('''
                select NombreTienda,count(ImporteTotal) AS total from datoscabecera 
                where NombreVendedor=""
                group by NombreTienda
                order by total desc ;
                       ''')
        response = cursor.fetchall()
        cursor.close()
        
        data_list = []
        for data in response:
            data_dict = {
                'NombreTienda':data[0],
                'total':data[1]
            }
            data_list.append(data_dict)
            
        return render_template('views/dashboardContent.html' , users = user_list, aux=aux_list, dia=dia_list, huerfanos=data_list)
    except Exception as e:
        print(f"Error:{e}")
        return "Error al obtener usuarios", 500

    


@app.route('/exportar_csv', methods=['POST'])
@login_required
def exportar_csv():
    id_co = session['sede']
    fecha_inicio = request.form.get('fecha_inicio')
    fecha_fin = request.form.get('fecha_fin')
    # convertir la fecha
    fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d").strftime("%Y%m%d")
    fecha_fin = datetime.strptime(fecha_fin, "%Y-%m-%d").strftime("%Y%m%d")
    #consulta para buscar la tope de registros
    cursor = mysql.connection.cursor()
    cursor.execute(
        'SELECT tope_mes_30 FROM topes_sede WHERE id_co = %s', (id_co,))
    tope_registros = cursor.fetchone()[0]
    cursor.close()

    cursor = mysql.connection.cursor()
    cursor.execute('''
        SELECT identificacion, MAX(nombres) as nombres, COUNT(identificacion) as cantidad_registros,
            ROUND((COUNT(identificacion) / %s) * 100, 2) as porcentaje
            FROM registro_mes 
            WHERE id_co = %s AND fecha_dcto >= %s AND fecha_dcto <= %s
            GROUP BY identificacion
            ORDER BY cantidad_registros DESC;
        ''', (tope_registros, id_co, fecha_inicio, fecha_fin))
    registros = cursor.fetchall()
    cursor.close()

    # Especifica el nombre del archivo CSV y su ubicación
    filename = 'registros.csv'

    # Especifica los encabezados de las columnas
    columnas = ['Cedula', 'Nombre', 'Registros', 'Porcentaje']

    # Escribe los datos en el archivo CSV
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(columnas)
        writer.writerows(registros)

    # Devuelve el archivo CSV como una respuesta para que el navegador lo descargue
    return send_file(filename, as_attachment=True)

    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=6400)
