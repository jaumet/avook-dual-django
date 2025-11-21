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

## Funcionalitats
- Registre i inici/tancament de sessió amb el sistema d'autenticació de Django.
- Creació i edició de productes amb camps de títol, parella de llengües, descripció, preu i fitxer d'àudio.
- Llista pública de productes i pàgina de detall amb reproductor d'àudio.
- Panell d'admin per gestionar productes (`/admin/`).
