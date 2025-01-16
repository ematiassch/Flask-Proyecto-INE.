from flask import Flask, send_file, jsonify
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os

app = Flask(__name__)

# Ruta para ejecutar el script
@app.route('/run-script', methods=['GET'])
def run_script():
    try:
        # URL de la página donde se encuentra el enlace
        page_url = "https://www.ine.gob.bo/index.php/nacional/"
        target_text = "Índice General, Variación Mensual, Acumulada y a 12 Meses"

        # Carpeta donde se guardará el archivo
        folder_path = "./"
        file_name = f"IPC_Mensual_{datetime.now().strftime('%Y-%m')}.xlsx"
        file_path = os.path.join(folder_path, file_name)

        # Hacer la solicitud a la página web
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(page_url, headers=headers)
        print(f"Código de estado de la respuesta: {response.status_code}")

        # Verificar si la solicitud fue exitosa
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            print("Página cargada correctamente. Buscando enlaces...")

            # Buscar todos los enlaces <a> en la página
            links = soup.find_all("a")
            print(f"Se encontraron {len(links)} enlaces en la página.")

            download_link = None
            for link in links:
                print(f"Revisando enlace: {link.text.strip()}")
                if link.text.strip() == target_text:
                    download_link = link.get("href")
                    print(f"Enlace encontrado: {download_link}")
                    break

            # Verificar si se encontró el enlace correcto
            if download_link:
                # Completar el enlace si es relativo
                if not download_link.startswith("http"):
                    download_link = page_url.rsplit("/", 1)[0] + "/" + download_link

                print(f"URL final del archivo para descargar: {download_link}")

                # Descargar el archivo Excel desde el enlace encontrado
                excel_response = requests.get(download_link, stream=True)
                if excel_response.status_code == 200:
                    with open(file_path, "wb") as file:
                        for chunk in excel_response.iter_content(chunk_size=8192):
                            if chunk:
                                file.write(chunk)
                    print(f"Archivo descargado exitosamente en: {file_path}")

                    # Enviar el archivo como respuesta al cliente
                    return send_file(file_path, as_attachment=True, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                else:
                    print(f"Error al descargar el archivo. Código de estado: {excel_response.status_code}")
                    return jsonify({"error": f"Error al descargar el archivo. Código de estado: {excel_response.status_code}"}), 500
            else:
                print(f"No se encontró ningún enlace con el texto: {target_text}")
                return jsonify({"error": f"No se encontró ningún enlace con el texto: {target_text}"}), 404
        else:
            print(f"Error al acceder a la página. Código de estado: {response.status_code}")
            return jsonify({"error": f"Error al acceder a la página. Código de estado: {response.status_code}"}), 500
    except Exception as e:
        print(f"Error al ejecutar el script: {str(e)}")
        return jsonify({"error": f"Error al ejecutar el script: {str(e)}"}), 500

# Iniciar el servidor
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)