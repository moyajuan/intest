# Importar librerías necesarias
import os
import firebase_admin
import matplotlib.pyplot as plt
import io
import base64
import numpy as np
from firebase_admin import credentials, db
from flask import Flask, render_template, redirect, url_for, request, session
from data.database import get_entries, insert_entry, update_entry, delete_entry, get_entries_by_id, create_database, insert_salida, get_salidas, delete_salida_from_db

# Inicialización de Firebase
cred = credentials.Certificate('serviceAccountKey.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://practica28-a1a4e-default-rtdb.firebaseio.com/'
})

# Crear la aplicación Flask
app = Flask(__name__)

# Configuración para manejar sesiones
app.secret_key = os.urandom(24)

# Crear la base de datos si no existe
create_database()

# Lista temporal de dispositivos (si se usa de ejemplo)
dispositivos = []

import logging

logging.basicConfig(level=logging.DEBUG)

def obtener_dispositivos():
    # Recupera los dispositivos desde Firebase
    ref = db.reference('dispositivos')
    dispositivos = ref.get()

    # Agrega un log para ver el resultado
    logging.debug(f"Dispositivos recuperados: {dispositivos}")

    if dispositivos is None:
        dispositivos = []  # Si no hay datos, se devuelve una lista vacía

    return dispositivos

# Función para agregar un dispositivo
def add_dispositivo(dispositivo):
    dispositivos.append(dispositivo)

# Funciones adicionales para obtener datos (reemplázalas según tu necesidad)
def get_mantenimientos():
    return []  # Lista vacía temporal

def get_reportes():
    return []  # Lista vacía temporal

# Función para insertar entradas en Firebase
def insert_entry_to_firebase(componente, num_parte, ubicacion_actual, Id_usuario, cantidad_entrada):
    ref = db.reference('/entradas')  # Referencia al nodo 'entradas'
    new_entry = {
        'componente': componente,
        'num_parte': num_parte,
        'ubicacion_actual': ubicacion_actual,
        'Id_usuario': Id_usuario,
        'cantidad_entrada': cantidad_entrada
    }
    ref.push(new_entry)  # Inserta los datos en Firebase

# Función para obtener las entradas desde Firebase
def get_entries_from_firebase():
    ref = db.reference('/entradas')
    entries = ref.get()  # Obtiene todas las entradas
    productos = []
    if entries:
        for key, value in entries.items():
            productos.append({
                'id': key,
                'componente': value['componente'],
                'num_parte': value['num_parte'],
                'ubicacion_actual': value['ubicacion_actual'],
                'Id_usuario': value['Id_usuario'],
                'cantidad_entrada': value['cantidad_entrada']
            })
    return productos


# Ruta de inicio
@app.route('/')
def index():
    if 'user' in session:
        return render_template('index.html')
    return redirect(url_for('login'))


# Ruta para la página principal (PGM)
@app.route('/pgm')
def pgm():
    return render_template('PGM.html')


########################### master list #########################################################################
# Ruta para mostrar la lista de dispositivos en PGM Master List
@app.route('/pgm_master_list', methods=['GET', 'POST'])
def pgm_master_list():
    dispositivos_ref = db.reference('dispositivos')
    dispositivos = dispositivos_ref.get()

    if request.method == 'POST':
        # Agregar dispositivo
        serial = request.form['serial']
        descripcion = request.form['descripcion']
        locacion = request.form['locacion']
        status = request.form['status']

        dispositivos_ref.child(serial).set({
            'serial': serial,
            'descripcion': descripcion,
            'locacion': locacion,
            'status': status
        })
        return redirect(url_for('pgm_master_list'))

    # Editar dispositivo
    if 'edit' in request.form:
        device_id = request.form['device_id']
        descripcion = request.form['descripcion']
        locacion = request.form['locacion']
        status = request.form['status']
        
        dispositivos_ref.child(device_id).update({
            'descripcion': descripcion,
            'locacion': locacion,
            'status': status
        })
        return redirect(url_for('pgm_master_list'))

    # Eliminar dispositivo
    if 'delete' in request.form:
        device_id = request.form['device_id']
        dispositivos_ref.child(device_id).delete()
        return redirect(url_for('pgm_master_list'))

    return render_template('pgm_master_list.html', dispositivos=dispositivos)

###########################fin de ruta masrter list ############################################################


#################################pagina de maintenance ############################################################
# Ruta para agregar mantenimiento
@app.route('/pgm/maintenance', methods=['GET', 'POST'])
def pgm_maintenance():
    if request.method == 'POST':
        # Obtén los datos del formulario para agregar un nuevo mantenimiento
        mantenimiento_data = {
            "no_orden": request.form.get('no_orden'),
            "equipo": request.form.get('equipo'),
            "fecha": request.form.get('fecha'),
            "frecuencia": request.form.get('frecuencia'),
            "detalles": request.form.get('detalles'),
            "diferencia": request.form.get('diferencia'),
            "tiempo": request.form.get('tiempo'),
            "tipo_mantenimiento": request.form.get('tipo_mantenimiento')
        }
        
        # Guardar los datos en Firebase Realtime Database
        mantenimientos_ref = db.reference('mantenimientos')
        mantenimientos_ref.push(mantenimiento_data)  # Usamos push para agregar un nuevo mantenimiento

    # Obtener todos los mantenimientos desde Realtime Database
    mantenimientos_ref = db.reference('mantenimientos')
    mantenimientos = mantenimientos_ref.get()  # Obtén los datos como un diccionario

    # Si no hay datos, asigna una lista vacía
    if mantenimientos is None:
        mantenimientos = []

    # Redirige a la página con la lista de mantenimientos
    return render_template('pgm_maintenance.html', mantenimientos=mantenimientos)


@app.route('/delete_maintenance/<id>', methods=['GET'])
def delete_maintenance(id):
    # Eliminar mantenimiento por ID en Realtime Database
    mantenimiento_ref = db.reference(f'mantenimientos/{id}')
    mantenimiento_ref.delete()

    # Redirige a la lista de mantenimientos después de eliminar
    return redirect(url_for('pgm_maintenance'))


@app.route('/edit_maintenance/<id>', methods=['GET', 'POST'])
def edit_maintenance(id):
    mantenimiento_ref = db.reference(f'mantenimientos/{id}')
    mantenimiento = mantenimiento_ref.get()

    if request.method == 'POST':
        # Actualiza los datos del mantenimiento
        updated_data = {
            "no_orden": request.form.get('no_orden'),
            "equipo": request.form.get('equipo'),
            "fecha": request.form.get('fecha'),
            "frecuencia": request.form.get('frecuencia'),
            "detalles": request.form.get('detalles'),
            "diferencia": request.form.get('diferencia'),
            "tiempo": request.form.get('tiempo'),
            "tipo_mantenimiento": request.form.get('tipo_mantenimiento')
        }

        mantenimiento_ref.update(updated_data)

        # Redirige a la lista de mantenimientos después de editar
        return redirect(url_for('pgm_maintenance'))

    return render_template('edit_maintenance.html', mantenimiento=mantenimiento)



############################fin de pagina de maintenace #########################################################

############################ pagina de audit reports ##########################################################
# Ruta para agregar reporte de auditoría
# Ruta para mostrar la página de reportes y manejar la creación de nuevos reportes
@app.route('/pgm/audit_reports', methods=['GET', 'POST'])
def pgm_audit_reports():
    if request.method == 'POST':
        # Crear un nuevo reporte
        new_report = {
            'no_orden': request.form['no_orden'],
            'equipo': request.form['equipo'],
            'fecha': request.form['fecha'],
            'reloj': request.form['reloj'],
            'empleado': request.form['empleado'],
            'imagen_empleado': request.form['imagen_empleado']
        }

        # Guardar el reporte en Firebase
        ref = db.reference('audit_reports')
        ref.push(new_report)

    # Obtener todos los reportes
    ref = db.reference('audit_reports')
    reportes = ref.get()

    # Mostrar los reportes en la página
    return render_template('pgm_audit_reports.html', reportes=reportes)

# Ruta para obtener un reporte específico para editar
@app.route('/pgm/audit_reports/get_report/<report_id>', methods=['GET'])
def get_report(report_id):
    ref = db.reference(f'audit_reports/{report_id}')
    report = ref.get()
    return jsonify(report)

@app.route('/pgm/audit_reports/delete_report/<report_id>', methods=['GET'])
def delete_report(report_id):
    ref = db.reference(f'audit_reports/{report_id}')
    ref.delete()
    return redirect(url_for('pgm_audit_reports'))

############################# fin de audit reports #############################################################

@app.route('/pgm/add_report', methods=['GET', 'POST'])
def add_report():
    if request.method == 'POST':
        no_orden = request.form.get('no_orden', '')
        equipo = request.form.get('equipo', '')
        fecha = request.form.get('fecha', '')
        reloj = request.form.get('reloj', '')
        empleado = request.form.get('empleado', '')
        imagen_empleado = request.form.get('imagen_empleado', None)

        # Procesa los datos y guárdalos, si es necesario, en una base de datos
        return redirect(url_for('pgm_audit_reports'))

    return render_template('add_report.html')


# Ruta para el inicio de sesión
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == 'juan' and password == '1234':
            session['user'] = username
            return redirect(url_for('index'))
        else:
            return '''
                <script>alert("Credenciales incorrectas. Intenta nuevamente."); window.location.href = "/login";</script>
            '''
    
    return render_template('login.html')


# Ruta para cerrar sesión
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))


# Ruta para el Dashboard
@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        return render_template('dashboard.html')
    return redirect(url_for('login'))


# Ruta para manejar las entradas
@app.route('/entradas', methods=['GET', 'POST'])
def entradas():
    if 'user' in session:
        if request.method == 'POST':
            componente = request.form.get('componente', '')
            num_parte = request.form.get('num_parte', '')
            ubicacion_actual = request.form.get('ubicacion_actual', '')
            Id_usuario = request.form.get('Id_usuario', '')
            cantidad_entrada = request.form.get('cantidad_entrada', '')

            # Llamamos a la función para insertar en Firebase
            insert_entry_to_firebase(componente, num_parte, ubicacion_actual, Id_usuario, cantidad_entrada)
            return redirect(url_for('entradas'))

        # Obtener entradas desde Firebase
        productos = get_entries_from_firebase()
        return render_template('entradas.html', productos=productos)
    return redirect(url_for('login'))


@app.route('/entradas/edit/<string:id>', methods=['GET', 'POST'])
def edit_entrada(id):
    if request.method == 'POST':
        # Obtener datos del formulario
        componente = request.form['componente']
        num_parte = request.form['num_parte']
        ubicacion_actual = request.form['ubicacion_actual']
        Id_usuario = request.form['Id_usuario']
        cantidad_entrada = request.form['cantidad_entrada']

        # Actualizar en Firebase
        db.reference('entradas').child(id).update({
            'componente': componente,
            'num_parte': num_parte,
            'ubicacion_actual': ubicacion_actual,
            'Id_usuario': Id_usuario,
            'cantidad_entrada': cantidad_entrada,
        })

        # Redirigir a la página de entradas después de la actualización
        return redirect(url_for('entradas'))

    else:
        # Obtener los datos de la entrada para mostrar en el formulario de edición
        entrada = db.reference('entradas').child(id).get()

        # Renderizar entradas.html pasando la información de la entrada
        return render_template('entradas.html', entrada=entrada, editar=True)


@app.route('/entradas/delete/<string:id>', methods=['POST'])
def delete_entrada(id):
    # Eliminar de Firebase usando delete() en lugar de remove()
    db.reference('entradas').child(id).delete()
    
    # Redirigir a la lista de entradas
    return redirect(url_for('entradas'))



# Ruta para manejar las salidas
@app.route('/salidas', methods=['GET', 'POST'])
def salidas():
    if 'user' in session:
        if request.method == 'POST':
            componente = request.form.get('componente', '')
            num_parte = request.form.get('num_parte', '')
            ubicacion_actual = request.form.get('ubicacion_actual', '')
            Id_usuario = request.form.get('Id_usuario', '')
            cantidad_salida = request.form.get('cantidad_salida')

            # Llamamos a la función para insertar en Firebase
            insert_salida(componente, num_parte, ubicacion_actual, Id_usuario, cantidad_salida)
            return redirect(url_for('salidas'))

        salidas = get_salidas()
        return render_template('salidas.html', salidas=salidas)
    return redirect(url_for('login'))

# Función para insertar una nueva salida en Firebase
def insert_salida(componente, num_parte, ubicacion_actual, Id_usuario, cantidad_salida):
    salidas_ref = db.reference('salidas')
    nueva_salida = {
        'componente': componente,
        'num_parte': num_parte,
        'ubicacion_actual': ubicacion_actual,
        'Id_usuario': Id_usuario,
        'cantidad_salida': cantidad_salida,
    }
    salidas_ref.push(nueva_salida)

# Función para obtener las salidas desde Firebase
def get_salidas():
    salidas_ref = db.reference('salidas')
    salidas = salidas_ref.get()
    return salidas.items() if salidas else {}


@app.route('/edit_device/<string:id>')
def edit_device(id):
    # Aquí va el código para editar el dispositivo con el id
    # Obtén el dispositivo de la base de datos, etc.
    return render_template('edit_device.html', dispositivo=dispositivo)


# Ruta para actualizar los datos de la salida
@app.route('/edit_salida', methods=['POST'])
def edit_salida():
    if 'user' in session:
        # Obtener los datos del formulario
        id = request.form['id']
        componente = request.form['componente']
        num_parte = request.form['num_parte']
        ubicacion_actual = request.form['ubicacion_actual']
        Id_usuario = request.form['Id_usuario']
        cantidad_salida = request.form['cantidad_salida']
        
        # Llamar a la función para actualizar la salida en la base de datos
        update_salida(id, componente, num_parte, ubicacion_actual, Id_usuario, cantidad_salida)
        
        # Redirigir a la lista de salidas
        return redirect(url_for('salidas'))
    return redirect(url_for('login'))

# Función para actualizar los datos de la salida en Firebase
def update_salida(id, componente, num_parte, ubicacion_actual, Id_usuario, cantidad_salida):
    salida_ref = db.reference('salidas').child(id)
    salida_ref.update({
        'componente': componente,
        'num_parte': num_parte,
        'ubicacion_actual': ubicacion_actual,
        'Id_usuario': Id_usuario,
        'cantidad_salida': cantidad_salida,
    })

# Ruta para eliminar una salida
@app.route('/delete_salida/<string:id>', methods=['POST'])
def delete_salida(id):
    if 'user' in session:
        delete_salida_from_db(id)
        return redirect(url_for('salidas'))
    return redirect(url_for('login'))

# Función para eliminar una salida de Firebase
def delete_salida_from_db(id):
    db.reference('salidas').child(id).delete()
    #########################################################################################

@app.route('/reportes')
def reportes():
    # Obtener los datos de la base de datos de Firebase
    ref = db.reference('entradas')  # Cambiar la referencia a la ruta correcta
    entradas_data = ref.get()  # Datos de entradas

    ref_salidas = db.reference('salidas')  # Referencia para salidas
    salidas_data = ref_salidas.get()  # Datos de salidas

    # Verificar si no hay datos
    if entradas_data is None:
        entradas_data = []  # Asignar una lista vacía si no hay datos
    if salidas_data is None:
        salidas_data = []  # Asignar una lista vacía si no hay datos

    # Inicializamos las variables
    total_productos = len(entradas_data) + len(salidas_data)  # Total de productos en ambas tablas
    entradas_recientes = 0
    salidas_recientes = 0
    productos_criticos = 0
    productos_recientes = []

    # Listas para productos en entrada y salida
    productos_entrada = []
    productos_salida = []
    nombres_productos = []

    # Procesamos las entradas
    for entrada in entradas_data:
        if isinstance(entrada, dict):
            try:
                cantidad_entrada = int(entrada.get('cantidad_entrada', 0))
            except ValueError:
                cantidad_entrada = 0  # Si no es numérico, asignamos 0
            entradas_recientes += cantidad_entrada
            nombre_producto = entrada.get('componente', 'Desconocido')
            productos_entrada.append(cantidad_entrada)
            nombres_productos.append(nombre_producto)
            productos_recientes.append([entrada.get('num_parte'), nombre_producto, cantidad_entrada, entrada.get('ubicacion_actual')])

            # Marcar como producto crítico si la cantidad es menor a 10
            if cantidad_entrada < 10:
                productos_criticos += 1

    # Procesamos las salidas
    for salida in salidas_data:
        if isinstance(salida, dict):
            try:
                cantidad_salida = int(salida.get('cantidad_entrada', 0))
            except ValueError:
                cantidad_salida = 0  # Si no es numérico, asignamos 0
            salidas_recientes += cantidad_salida
            nombre_producto = salida.get('componente', 'Desconocido')
            productos_salida.append(cantidad_salida)
            productos_recientes.append([salida.get('num_parte'), nombre_producto, cantidad_salida, salida.get('ubicacion_actual')])

            # Marcar como producto crítico si la cantidad es menor a 10
            if cantidad_salida < 10:
                productos_criticos += 1

    # Datos para los gráficos
    entradas_totales = entradas_recientes
    salidas_totales = salidas_recientes

    # Crear la gráfica
    fig, ax = plt.subplots()
    ax.barh(nombres_productos, productos_entrada, label='Entradas', color='blue', alpha=0.6)
    ax.barh(nombres_productos, productos_salida, label='Salidas', color='red', alpha=0.6)
    ax.set_xlabel('Cantidad')
    ax.set_title('Entradas y Salidas de Productos')
    ax.legend()

    # Convertir la gráfica a imagen para renderizarla en HTML
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    img_base64 = base64.b64encode(img.getvalue()).decode('utf-8')
    plt.close()

    # Renderizamos el template y pasamos los datos y la imagen base64
    return render_template('reportes.html', 
                           total_productos=total_productos,
                           entradas_recientes=entradas_recientes,
                           salidas_recientes=salidas_recientes,
                           productos_criticos=productos_criticos,
                           productos_recientes=productos_recientes,
                           entradas_totales=entradas_totales,
                           salidas_totales=salidas_totales,
                           img_base64=img_base64)



###################################################
# Ruta para inventario
@app.route('/inventario')
def inventario():
    if 'user' in session:
        productos = get_entries_from_firebase()
        return render_template('inventario.html', productos=productos)
    return redirect(url_for('login'))


@app.route('/storage_room')
def storage_room():
    # Aquí va el código de la vista para el Storage Room
    return render_template('storage_room.html')


@app.route('/tools')
def tools():
    # Lógica para la página de herramientas
    return render_template('tools.html')


# Ruta para el inventario general
@app.route('/inventory')
def inventory():
    if 'user' in session:
        return render_template('inventory.html')
    return redirect(url_for('login'))


# Ruta para inventario de repuestos
@app.route('/spare_parts_inventory')
def spare_parts_inventory():
    if 'user' in session:
        return render_template('spare_parts_inventory.html')
    return redirect(url_for('login'))


# Ruta para Fixtures Cage A
@app.route('/spare_parts_inventory/fixtures_cage_a')
def spare_parts_inventory_fixtures_cage_a():
    if 'user' in session:
        return render_template('fixtures_cage_a.html', title="Fixtures Cage A")
    return redirect(url_for('login'))


# Ruta para Fixtures Cage B
@app.route('/spare_parts_inventory/fixtures_cage_b')
def spare_parts_inventory_fixtures_cage_b():
    if 'user' in session:
        return render_template('fixtures_cage_b.html', title="Fixtures Cage B")
    return redirect(url_for('login'))


# Ruta para Fixtures Cage C
@app.route('/spare_parts_inventory/fixtures_cage_c')
def spare_parts_inventory_fixtures_cage_c():
    if 'user' in session:
        return render_template('fixtures_cage_c.html', title="Fixtures Cage C")
    return redirect(url_for('login'))


# Iniciar la aplicación
if __name__ == '__main__':
    app.run(debug=True)
