# WinstonLutz Docker

Dieses Projekt enthält eine Docker-Container-basierte Anwendung zur Analyse und Darstellung von Winston-Lutz DICOM-Dateien.

## Voraussetzungen

- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Installation und Ausführung

### Auf Ubuntu

1. **Docker und Docker Compose installieren**:
   ```bash
   sudo apt-get update
   sudo apt-get install -y docker.io
   sudo systemctl start docker
   sudo systemctl enable docker
   sudo usermod -aG docker $USER
   ```
2. **Repository klonen:**
  ```bash
git clone https://github.com/yourusername/winston-lutz-docker.git
cd winston-lutz-docker
``

3. **Docker-Container starten:**
```bash
sudo docker-compose up --build
```
#### Anwendung im Browser öffnen
http://localhost:3141

### Auf Windows
1. **Docker Desktop installieren**
2. Repository klonen:
Öffne die Eingabeaufforderung oder PowerShell und führe folgende Befehle aus:

```bash

git clone https://github.com/yourusername/winston-lutz-docker.git
cd winston-lutz-docker
```

3. **Docker-Container starten:**

``bash

docker-compose up --build
```

Anwendung im Browser öffnen:
http://localhost:3141 


### Fehlerbehebung

   #### Docker-Dienst neu starten:

    ``bash

sudo systemctl restart docker
```
#### Logs anzeigen:

```bash

docker-compose logs
```

#### Container stoppen und entfernen:

```bash

    docker-compose down
```

### Autor

Erik Schröder

### Lizenz
Dieses Projekt enthält Teile von pylinac, die unter der folgenden Lizenz stehen:
``
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
IN THE SOFTWARE.
``
