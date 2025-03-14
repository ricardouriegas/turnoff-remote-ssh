import streamlit as st
import paramiko
from datetime import datetime, timedelta
import time

def schedule_shutdown(ip, os_type, username, key_path, shutdown_time, sudo_password=None):
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        private_key = paramiko.RSAKey.from_private_key_file(key_path)

        client.connect(
            hostname=ip,
            username=username,
            pkey=private_key,
            timeout=10
        )

        # Calcular tiempo restante
        now = datetime.now()
        time_diff = shutdown_time - now
        seconds = int(time_diff.total_seconds())

        if seconds <= 0:
            st.error(f"Hora programada debe ser en el futuro para {ip}")
            return False

        # Comandos específicos por SO
        if os_type == "Windows":
            command = f'shutdown /s /f /t {seconds}'
        elif os_type == "Linux":
            minutes = seconds // 60
            command = f'sudo shutdown -h +{minutes}'

        stdin, stdout, stderr = client.exec_command(command)

        if sudo_password and os_type == "Linux":
            stdin.write(f'{sudo_password}\n')
            stdin.flush()

        time.sleep(2)
        error = stderr.read().decode()

        if error:
            st.error(f"Error en {ip} ({os_type}): {error}")
            return False
        return True

    except Exception as e:
        st.error(f"Conexión fallida {ip}: {str(e)}")
        return False
    finally:
        client.close()

# Interfaz web
st.title("⏰ Programador de Apagado Remoto")
st.markdown("### Sistema para equipos Windows y Linux")

# Autenticación
admin_pass = st.text_input("Contraseña maestra:", type="password")
correct_pass = st.secrets["MASTER_PASSWORD"]

if admin_pass == correct_pass:
    st.success("Autenticación exitosa")

    # Configuración
    st.subheader("Configuración de apagado")

    # Selección de hora
    col1, col2 = st.columns(2)
    with col1:
        # Replace st.datetime_input with date and time inputs
        selected_date = st.date_input("Fecha programada:", value=datetime.now().date(), min_value=datetime.now().date())
        selected_time = st.time_input("Hora programada:", value=(datetime.now() + timedelta(minutes=1)).time())
        shutdown_time = datetime.combine(selected_date, selected_time)
    with col2:
        immediate = st.checkbox("Apagado inmediato")

    # Lista de equipos
    computers = st.data_editor(
        [
            {"IP": "192.168.1.100", "OS": "Windows"},
            {"IP": "192.168.1.101", "OS": "Linux"}
        ],
        column_config={
            "OS": st.column_config.SelectboxColumn(
                "Sistema Operativo",
                options=["Windows", "Linux"],
                required=True
            )
        },
        num_rows="dynamic"
    )

    # Configuración SSH
    ssh_user = st.text_input("Usuario SSH:", value="admin")
    sudo_pass = st.text_input("Contraseña sudo (Linux):", type="password")
    key_file = st.file_uploader("Clave privada SSH", type=["pem"])

    if st.button("Programar apagado") and key_file:
        key_path = f"/tmp/{key_file.name}"
        with open(key_path, "w") as f:
            f.write(key_file.getvalue().decode())

        success = 0
        for pc in computers:
            ip = pc["IP"].strip()
            os_type = pc["OS"]
            if ip:
                target_time = datetime.now() + timedelta(seconds=30) if immediate else shutdown_time

                if schedule_shutdown(ip, os_type, ssh_user, key_path, target_time, sudo_pass):
                    st.success(f"✅ {ip} ({os_type}) - Apagado programado: {target_time.strftime('%H:%M')}")
                    success += 1
                else:
                    st.error(f"❌ {ip} ({os_type}) - Error en programación")

        st.metric("Equipos programados", f"{success}/{len(computers)}")

else:
    if admin_pass:
        st.error("Contraseña incorrecta")
