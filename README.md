# Docker-django-z1

Prueba técnica de la empresa Z1: Utilizando Django y PostgreSQL crea un API GraphQL que de servicio a una app móvil.

## Requisitos iniciales

Antes de comenzar, asegúrate de tener instaladas las siguientes herramientas:

- Python 3 o superior
- Docker instalado y corriendo en segundo plano
- Un editor de código, como Visual Studio Code

## Configuración del entorno

1. Clona este repositorio en tu máquina local: git clone https://github.com/jesuspi00001/docker-django-z1.git
2. Construye y levanta los contenedores de docker: docker-compose up --build
3. Espera a que el servicio de la bbdd esté levantado y el servicio web quede a la espera (Cntrl+c para salir).
4. Lanza el comando: docker-compose run web python manage.py makemigrations
5. Lanza el comando: docker-compose run web python manage.py migrate
6. Lanza el comando: docker-compose run web python manage.py createsuperuser y sigue las instrucciones para crear un superuser con el que poder acceder al panel de administración.
7. Lanza el comando: docker-compose up
8. Abre tu navegador y visita `http://0.0.0.0:8000` para acceder a la aplicación.
9. En la ruta `http://0.0.0.0:8000/admin` tendremos el panel de administración de la bbdd.
10. En la ruta `http://0.0.0.0:8000/graphql` tendremos el apigraphql y podremos lanzar nuestras consultas.
      
