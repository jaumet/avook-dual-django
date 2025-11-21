# Audiovook Dual — Django

Aquest projecte converteix el lloc estàtic d'Audiovook Dual en una aplicació Django amb gestió d'usuaris i catàleg de productes.

## Configuració
1. Crea i activa un entorn virtual.
2. Instal·la les dependències:
   ```bash
   pip install -r requirements.txt
   ```
3. Executa les migracions i arrenca el servidor:
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

## Important: Actualització de la base de dades (Novembre 2025)

Recentment, s'ha fet una reestructuració completa dels models de dades (`Title`, `Package`, `Product`). Si tenies una versió anterior de l'aplicació, la teva base de dades local no serà compatible.

Per solucionar-ho, has de reiniciar la base de dades seguint aquests passos:

1.  **Atura el servidor de desenvolupament** (si l'estàs executant).
2.  **Esborra el fitxer de la base de dades local**:
    ```bash
    rm db.sqlite3
    ```
3.  **Aplica les noves migracions** per crear la nova estructura de la base de dades:
    ```bash
    python manage.py migrate
    ```
4.  **Crea un nou superusuari** per poder accedir al panell d'administració:
    ```bash
    python manage.py createsuperuser
    ```
5.  **Inicia el servidor de nou**:
    ```bash
    python manage.py runserver
    ```

Després de seguir aquests passos, l'aplicació hauria de funcionar correctament amb la nova estructura de dades.

## Funcionalitats
- Registre i inici/tancament de sessió amb el sistema d'autenticació de Django.
- Creació i edició de productes amb camps de títol, parella de llengües, descripció, preu i fitxer d'àudio.
- Llista pública de productes i pàgina de detall amb reproductor d'àudio.
- Panell d'admin per gestionar productes (`/admin/`).
