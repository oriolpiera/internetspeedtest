import os
import subprocess
import time
import json
import paho.mqtt.client as mqtt
import re
import csv
from datetime import datetime


class speedtest():
    def test(self):
        args = ['./speedtest', '-a', '-f', 'json', '--accept-license', '--accept-gdpr']

        if os.environ.get('SERVER_ID') != None:
            args.append('-s')
            args.append(os.environ.get('SERVER_ID'))

        p = subprocess.Popen(args , shell=False, stdout=subprocess.PIPE)
        response = p.communicate()
        result = json.loads(response[0])
        print ("Timestamp = " + str(result['timestamp']))
        print ("Down = " + str(result['download']['bandwidth']))
        print ("Up = " + str(result['upload']['bandwidth']))
        print ("Latency = " + str(result['ping']['latency']))
        print ("Jitter = " + str(result['ping']['jitter']))
        print ("Interface = " + str(result['interface']))
        print ("Server = " + str(result['server']))
        return result

    def ping_adreca(self, adreca, duracio_segons):
        temps_final = time.time() + duracio_segons
        paquets_enviats = 0
        paquets_perduts = 0
        temps_total = 0
        respostes_valides = 0

        while time.time() < temps_final:
            try:
                # Executa el ping una vegada
                resultat = subprocess.run(
                    ["ping", "-c", "1", adreca],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                paquets_enviats += 1

                # Busca el temps de resposta en el resultat
                if resultat.returncode == 0:
                    match = re.search(r'time=(\d+\.\d+) ms', resultat.stdout)
                    if match:
                        temps_total += float(match.group(1))
                        respostes_valides += 1
                else:
                    paquets_perduts += 1
            except Exception as e:
                print(f"Error en executar el ping: {e}")
                paquets_perduts += 1

            time.sleep(1)  # Espera 1 segon abans del següent ping

        # Calcula la mitjana de temps
        temps_mitja = temps_total / respostes_valides if respostes_valides > 0 else 0

        return paquets_enviats, paquets_perduts, temps_mitja

    def save_results_to_csv(self, file_path, download, upload, ping, paquets_enviats, paquets_perduts, temps_mitja):
        file_exists = True
        try:
            with open(file_path, 'x') as f:
                file_exists = False
        except FileExistsError:
            pass

        with open(file_path, 'a', newline='') as csvfile:
            fieldnames = ['timestamp', 'download_speed_mbps', 'upload_speed_mbps', 'ping_ms', 'paquets_enviats', 'paquets_perduts', 'temps_mitja']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            if not file_exists:
                writer.writeheader()

            writer.writerow({
                'timestamp': datetime.now().isoformat(),
                'download_speed_mbps': download,
                'upload_speed_mbps': upload,
                'ping_ms': ping,
                'paquets_enviats': paquets_enviats,
                'paquets_perduts': paquets_perduts,
                'temps_mitja': temps_mitja,
            })


speedtest = speedtest()
frequency = os.environ.get('FREQUENCY') or 3600
broker_address = os.environ.get('MQTT_BROKER') or "localhost"

client = mqtt.Client("1")
file_path = "/data/internet_speed_results.csv"

while True:
    client.connect(broker_address)
    result = speedtest.test()
    json_body = [
        {
            "measurement": "download",
            "time": str(result['timestamp']),
            "fields": {
                "value": int(str(result['download']['bandwidth'])),
                "up": int(result['upload']['bandwidth']),
                "latency": float(result['ping']['latency']),
                "jitter": float(result['ping']['jitter']),
                "interface": str(result['interface']['name']),
                "server": str(result['server']['host'])
            }
        }
    ]

    print("JSON body = " + str(json_body))
    msg_info = client.publish("sensors",json.dumps(json_body))
    if msg_info.is_published() == False:
            msg_info.wait_for_publish()



    paquets_enviats, paquets_perduts, temps_mitja = speedtest.ping_adreca('www.google.com', int(frequency))
    json_body = [
        {
            "measurement": "ping",
            "time": str(result['timestamp']),
            "fields": {
                'paquets_enviats': int(paquets_enviats),
                'paquets_perduts': int(paquets_perduts),
                'temps_mitja': float(temps_mitja)
            }
        }
    ]

    print("JSON body = " + str(json_body))
    msg_info = client.publish("sensors",json.dumps(json_body))
    if msg_info.is_published() == False:
            msg_info.wait_for_publish()

    speedtest.save_results_to_csv(
        file_path,
        int(str(result['download']['bandwidth'])),
        int(result['upload']['bandwidth']),
        float(result['ping']['latency']),
        paquets_enviats, paquets_perduts, temps_mitja)

    client.disconnect()
    #time.sleep(int(frequency))




