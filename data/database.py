import sqlite3

# Ruta de la base de datos
DATABASE = 'data/database.db'

# Crear la base de datos si no existe
def create_database():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Las filas devueltas serán diccionarios
    cursor = conn.cursor()

    # Tabla de entradas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS entradas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            componente TEXT,
            num_parte TEXT,
            ubicacion_actual TEXT,
            Id_usuario TEXT,
            cantidad_entrada INTEGER
        )
    """)

    # Tabla de salidas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS salidas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            componente TEXT,
            num_parte TEXT,
            ubicacion_actual TEXT,
            Id_usuario TEXT,
            cantidad_salida INTEGER
        )
    """)

    conn.commit()
    conn.close()

# --- FUNCIONES PARA ENTRADAS ---

def get_entries():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM entradas")
    productos = cursor.fetchall()
    conn.close()
    return productos

def get_entries_by_id(id):
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM entradas WHERE id = ?", (id,))
    producto = cursor.fetchone()
    conn.close()
    return producto

def insert_entry(componente, num_parte, ubicacion_actual, Id_usuario, cantidad_entrada):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO entradas (componente, num_parte, ubicacion_actual, Id_usuario, cantidad_entrada) 
        VALUES (?, ?, ?, ?, ?)
    """, (componente, num_parte, ubicacion_actual, Id_usuario, cantidad_entrada))
    conn.commit()
    conn.close()

def update_entry(id, componente, num_parte, ubicacion_actual, Id_usuario, cantidad_entrada):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE entradas
        SET componente = ?, num_parte = ?, ubicacion_actual = ?, Id_usuario = ?, cantidad_entrada = ?
        WHERE id = ?
    """, (componente, num_parte, ubicacion_actual, Id_usuario, cantidad_entrada, id))
    conn.commit()
    conn.close()

def delete_entry(id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM entradas WHERE id = ?", (id,))
    conn.commit()
    conn.close()

# --- FUNCIONES PARA SALIDAS ---

def get_salidas():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM salidas")
    salidas = cursor.fetchall()
    conn.close()
    return salidas

def insert_salida(componente, num_parte, ubicacion_actual, Id_usuario, cantidad_salida):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Registrar la salida
    cursor.execute("""
        INSERT INTO salidas (componente, num_parte, ubicacion_actual, Id_usuario, cantidad_salida) 
        VALUES (?, ?, ?, ?, ?)
    """, (componente, num_parte, ubicacion_actual, Id_usuario, cantidad_salida))

    # Actualizar la cantidad en la tabla de entradas
    cursor.execute("""
        UPDATE entradas
        SET cantidad_entrada = cantidad_entrada - ?
        WHERE componente = ? AND num_parte = ? AND ubicacion_actual = ?
    """, (cantidad_salida, componente, num_parte, ubicacion_actual))

    conn.commit()
    conn.close()

def delete_salida_from_db(id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM salidas WHERE id = ?", (id,))
    conn.commit()
    conn.close()
