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

## Internationalization (i18n)

Aquest projecte utilitza un sistema de traducció basat en JavaScript al frontend. Per afegir un nou idioma, segueix aquests passos:

1.  **Afegeix l'idioma a `settings.py`**:
    A `avook_site/settings.py`, afegeix el nou codi d'idioma a la llista `LANGUAGES`. Això és necessari perquè el sistema d'URL de Django reconegui el nou idioma. Per exemple, per afegir alemany:
    ```python
    LANGUAGES = [
        ('ca', 'Català'),
        ('en', 'English'),
        ('es', 'Spanish'),
        ('pt', 'Portuguese'),
        ('it', 'Italian'),
        ('fr', 'French'),
        ('de', 'German'),  # Nova línia
    ]
    ```

2.  **Afegeix les traduccions al fitxer JSON**:
    Obre el fitxer `static/js/translations.json` i afegeix una nova secció per al teu idioma. Copia totes les claus de la secció `en` (anglès) i tradueix els valors. Per exemple, per a l'alemany (`de`):
    ```json
    {
      "ca": { ... },
      "en": { ... },
      "es": { ... },
      "fr": { ... },
      "it": { ... },
      "pt": { ... },
      "de": {
        "header.catalog": "Katalog",
        "header.products": "Produkte",
        ...
      }
    }
    ```

3.  **Afegeix l'opció al selector d'idioma**:
    A `templates/base.html`, afegeix la nova opció al selector d'idioma (`<select id="language-select">`):
    ```html
    <select id="language-select">
        ...
        <option value="de">Deutsch</option>
    </select>
    ```

4.  **Reinicia el servidor**:
    Atura i torna a iniciar el servidor de desenvolupament perquè els canvis a les URL tinguin efecte.

L'aplicació ara hauria de mostrar el nou idioma al selector i permetre als usuaris canviar-hi.

## Funcionalitats
- Registre i inici/tancament de sessió amb el sistema d'autenticació de Django.
- Creació i edició de productes amb camps de títol, parella de llengües, descripció, preu i fitxer d'àudio.
- Llista pública de productes i pàgina de detall amb reproductor d'àudio.
- Panell d'admin per gestionar productes (`/admin/`).

---

## Edició del contingut de la pàgina d'inici

El contingut de la pàgina d'inici (Homepage) es gestiona a través d'una secció dedicada al panell d'administració.

### Per a Editors de Contingut:

1.  **Accedeix al Panell d'Administració**: Navega a `/admin/`.
2.  **Ves a "Homepage Content"**: Al menú, busca la secció "Products" i fes clic a "Homepage Content".
3.  **Edita el Contingut**: S'obrirà un formulari amb camps de text enriquit per a cada tros de text de la pàgina d'inici. Edita el contingut directament en aquests camps. No hi ha JSON del qual preocupar-se.

### Per a Desenvolupadors:

El contingut inicial de la pàgina d'inici es crea automàticament a través d'una migració de dades. El `populate_content` ja no és necessari per a la pàgina d'inici.
