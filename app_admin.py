

import sqlite3 as sql
import os
from base64 import urlsafe_b64encode, urlsafe_b64decode
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from db_functions.user_functions import get_name_by_id

def claves_admin(c2):
    conn = sql.connect('cripto.sqlite')
    conn.row_factory = sql.Row
    cursor = conn.cursor()

    cursor.execute("SELECT id, user1_id, user2_id, clave, nonce FROM chats")
    chats = cursor.fetchall()

    for chat in chats:
        chat_id = chat['id']
        encrypted_data_key = urlsafe_b64decode(chat['clave'])
        nonce_master = urlsafe_b64decode(chat['nonce'])

        # Descifrado de la clave simétrica original
        AE_Key_stma = c2  # Debes asegurarte de que `c2` esté definido previamente
        chacha_master = ChaCha20Poly1305(AE_Key_stma)
        clave_simetrica_origen = chacha_master.decrypt(nonce_master, encrypted_data_key, None)

        # Generar nueva clave y nonce
        nueva_clave = ChaCha20Poly1305.generate_key()
        nuevo_nonce = os.urandom(12)

        # Cifrar la nueva clave simétrica
        encrypted_nueva_clave = chacha_master.encrypt(nuevo_nonce, nueva_clave, None)

        # Convertir a base64 para almacenamiento en la base de datos
        clave_cifrada_destino = urlsafe_b64encode(encrypted_nueva_clave).decode('utf-8')
        nonce_cifrado_destino = urlsafe_b64encode(nuevo_nonce).decode('utf-8')

        # Actualizar la tabla `chats`
        cursor.execute("""
            UPDATE chats 
            SET clave = ?, nonce = ? 
            WHERE id = ?
        """, (clave_cifrada_destino, nonce_cifrado_destino, chat_id))

        # Procesar los mensajes relacionados con el chat
        cursor.execute("SELECT id, message, nonce, sender_id FROM messages WHERE chat_id = ?", (chat_id,))
        messages = cursor.fetchall()

        for mensaje in messages:
            mensaje_id = mensaje['id']
            mensajecifrado = urlsafe_b64decode(mensaje['message'])
            noncemensaje = urlsafe_b64decode(mensaje['nonce'])

            # Descifrar mensaje con clave simétrica original
            chacha_data = ChaCha20Poly1305(clave_simetrica_origen)
            mensajefinal = chacha_data.decrypt(noncemensaje, mensajecifrado, None)

            # Cifrar mensaje con la nueva clave simétrica
            nuevo_nonce_mensaje = os.urandom(12)
            chacha_nueva = ChaCha20Poly1305(nueva_clave)
            nuevo_mensaje_cifrado = chacha_nueva.encrypt(nuevo_nonce_mensaje, mensajefinal, None)

            # Convertir a base64 y obtener timestamp actual
            ct_mensaje = urlsafe_b64encode(nuevo_mensaje_cifrado).decode('utf-8')
            nonce_mensaje = urlsafe_b64encode(nuevo_nonce_mensaje).decode('utf-8')

            # Actualizar la tabla `messages`
            cursor.execute("""
                UPDATE messages 
                SET message = ?, nonce = ? 
                WHERE id = ?
            """, (ct_mensaje, nonce_mensaje, mensaje_id))

    # Guardar los cambios en la base de datos
    conn.commit()
    conn.close()


def mensajescomprobacion_admin(c2):
    conn = sql.connect('cripto.sqlite')
    conn.row_factory = sql.Row
    cursor = conn.cursor()

    # Obtener todos los mensajes
    cursor.execute("""
        SELECT id,message, nonce, sender_id, recipient_id, chat_id
        FROM messages 
    """)
    mensajes = cursor.fetchall()

    mensajes_desencriptados = []

    for mensaje in mensajes:
        chat_id = mensaje['chat_id']
        cursor.execute("SELECT id, clave, nonce FROM chats WHERE id = ?", (chat_id,))
        chat = cursor.fetchone()

        if not chat:
            raise ValueError(f"No se encontró un chat con id {chat_id}")

        # Descifrar la clave simétrica del chat
        encrypted_data_key = urlsafe_b64decode(chat['clave'])
        nonce_master = urlsafe_b64decode(chat['nonce'])

        AE_Key_stma = c2  # Asegúrate de que `c2` esté definido previamente
        chacha_master = ChaCha20Poly1305(AE_Key_stma)
        clave_simetrica_origen = chacha_master.decrypt(nonce_master, encrypted_data_key, None)

        mensajecifrado = urlsafe_b64decode(mensaje['message'])
        noncemensaje = urlsafe_b64decode(mensaje['nonce'])

        # Descifrar mensaje con clave simétrica original
        chacha_data = ChaCha20Poly1305(clave_simetrica_origen)
        mensajefinal = chacha_data.decrypt(noncemensaje, mensajecifrado, None)
        mensajes_desencriptados.append({
            "id": mensaje["id"],
            "sender_id": get_name_by_id(mensaje["sender_id"])["username"],
            "recipient_id": get_name_by_id(mensaje["recipient_id"])["username"],
            "mensaje": mensajefinal.decode('utf-8')  # Convertir a texto
        })


    # Cerrar conexión
    conn.close()
    return mensajes_desencriptados


def vetarusuarios_admin():
    conn = sql.connect('cripto.sqlite')
    conn.row_factory = sql.Row
    cursor = conn.cursor()

    # Obtener todos los mensajes
    cursor.execute("""
            SELECT id, username, correo
            FROM users 
        """)
    usuariosto = cursor.fetchall()
    usuariostotales = []

    for user in usuariosto:
        usuariostotales.append({
            "id": user["id"],
            "username": user["username"],
            "correo": user["correo"]
        })

    # Cerrar conexión
    conn.close()
    usuariostotales = sorted(usuariostotales, key=lambda x: x['id'])

    return usuariostotales

def eliminarusuariosadmin(user_id, correo, username):
    conn = sql.connect('cripto.sqlite')
    cursor = conn.cursor()

    # Eliminar el mensaje
    cursor.execute("DELETE FROM messages WHERE sender_id = ?", (user_id,))
    cursor.execute("DELETE FROM messages WHERE recipient_id = ?", (user_id,))
    cursor.execute("DELETE FROM chats WHERE user1_id = ?", (user_id,))
    cursor.execute("DELETE FROM chats WHERE user2_id = ?", (user_id,))
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))

    try:
        # Usar placeholders para insertar los valores
        cursor.execute("INSERT INTO ban (username, correo) VALUES (?,?)",
                       (username, correo))
        conn.commit()  # Guardar los cambios
        print(f"Correo '{correo}' vetado correctamente.")
    except sql.IntegrityError as e:
        print("Error al insertar:", e)  # Manejar errores de integridad

    conn.commit()
    conn.close()