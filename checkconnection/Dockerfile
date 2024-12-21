FROM balenalib/raspberrypi3-debian:latest

# Instal·lar eines necessàries
RUN apt-get update && apt-get install -y curl && apt-get clean

# Copiar el script de monitoratge
COPY monitor-internet.sh /usr/src/app/
RUN chmod +x /usr/src/app/monitor-internet.sh

# Configurar el punt d'entrada
CMD ["bash", "/usr/src/app/monitor-internet.sh"]
    