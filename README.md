# Dual — Django

Aquest projecte converteix el lloc estàtic de Dual en una aplicació Django amb gestió d'usuaris i catàleg de productes.

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

## Configuració d'enviament de correus

El registre d'usuaris requereix l'enviament d'un correu electrònic per a l'activació del compte. Aquest projecte utilitza [Resend](https://resend.com/) per a la gestió de correus.

Perquè funcioni correctament, has de seguir aquests passos:

1.  **Crea un fitxer `.env`** a l'arrel del projecte (al mateix nivell que `manage.py`).
2.  **Afegeix la teva clau d'API de Resend** al fitxer `.env` de la següent manera:

    ```
    RESEND_API_KEY=la_teva_clau_api_aqui
    ```

    Substitueix `la_teva_clau_api_aqui` per la clau real que pots obtenir del teu compte de Resend.

Sense aquesta configuració, el sistema no podrà enviar correus i els nous usuaris no podran activar el seu compte.

## Important: Actualització de la base de dades (Novembre 2025)

Recentment, s'ha fet una reestructuració completa dels models de dades (`Title`, `Package`, `Product`). Si tenies una versió anterior de l'aplicació, la teva base de dades local no serà compatible.

Per solucionar-ho, has de reiniciar la base de dades seguint aquests passos:

1. **Atura el servidor de desenvolupament** (si l'estàs executant).
2. **Esborra el fitxer de la base de dades local**:
   
   ```bash
   rm db.sqlite3
   ```
3. **Aplica les noves migracions** per crear la nova estructura de la base de dades:
   
   ```bash
   python manage.py migrate
   ```
4. **Crea un nou superusuari** per poder accedir al panell d'administració:
   
   ```bash
   python manage.py createsuperuser
   ```
5. **Inicia el servidor de nou**:
   
   ```bash
   python manage.py runserver
   ```

Després de seguir aquests passos, l'aplicació hauria de funcionar correctament amb la nova estructura de dades.

## Internationalization (i18n)

Aquest projecte utilitza el sistema d'internacionalització de Django. Per afegir o modificar traduccions, segueix aquests passos:

1. **Marca les cadenes de text per a traducció**:
   - En plantilles HTML, utilitza `{% trans "Text a traduir" %}`.
   - En codi Python (vistes, formularis), utilitza `from django.utils.translation import gettext_lazy as _` i després `_("Text a traduir")`.

2. **Genera o actualitza els fitxers de traducció (.po)**:
   Executa la següent comanda per a cada idioma que vulguis actualitzar (per exemple, `es` per a l'espanyol):
   
   ```bash
   python manage.py makemessages -l es
   ```
   Això crearà o actualitzarà el fitxer `locale/es/LC_MESSAGES/django.po`.

3. **Edita els fitxers .po**:
   Obre el fitxer `.po` generat i afegeix les traduccions corresponents per a cada `msgid`.

4. **Compila els missatges**:
   Un cop hagis guardat les traduccions, compila els fitxers per a Django:
   
   ```bash
   python manage.py compilemessages
   ```

## Funcionalitats

- Registre i inici/tancament de sessió amb el sistema d'autenticació de Django.
- Creació i edició de productes amb camps de títol, parella de llengües, descripció, preu i fitxer d'àudio.
- Llista pública de productes i pàgina de detall amb reproductor d'àudio.
- Panell d'admin per gestionar productes (`/admin/`).

---

## Edició del contingut de la pàgina d'inici

El contingut de la pàgina d'inici (Homepage) es gestiona a través d'una secció dedicada al panell d'administració.

### Per a Editors de Contingut:

1. **Accedeix al Panell d'Administració**: Navega a `/admin/`.
2. **Ves a "Homepage Content"**: Al menú, busca la secció "Products" i fes clic a "Homepage Content".
3. **Edita el Contingut**: S'obrirà un formulari amb camps de text enriquit per a cada tros de text de la pàgina d'inici. Edita el contingut directament en aquests camps. No hi ha JSON del qual preocupar-se.

### Per a Desenvolupadors:

El contingut inicial de la pàgina d'inici es crea automàticament a través d'una migració de dades. El `populate_content` ja no és necessari per a la pàgina d'inici.



---------------------------------------------------------------



## How to add contents to the pages:



To add a new translatable text variable like `products_paragraf1` and have it appear on the Products page, you'll need to make small 
adjustments in three places: the Admin, the View, and the Template.

Here’s a step-by-step guide on how you would do it:

### Step 1: Add Your New Content in the Django Admin

You've already got the first step right! You would go to the admin panel, navigate to **Continguts Traduïbles** (Translatable Content), and create a new entry.

1. For the **Key** field, you would enter: `products_paragraf1`
2. For the **Contingut (Català)** field, you would type the paragraph you want to display in Catalan.
3. You can then do the same for the other languages (English, Spanish, etc.).

However, just creating it in the admin isn't enough to make it 
appear. We now need to tell the Products page to fetch and display this 
new content.

### Step 2: Update the View to Fetch the Content

The view is the Python code that prepares the data for the page. We need to edit `products/views.py` to tell the `ProductListView` to grab the content you just created.

I would modify the `get_context_data` method to look like this:

```
from .models import TranslatableContent

class ProductListView(TitleContextMixin, ListView):
    # ... (other code remains the same) ...

    def get_context_data(self, **kwargs):
        context = super().get_context_data(self, **kwargs)
        lang = self.request.LANGUAGE_CODE

        # --- I would add this part ---
        # Get all translatable content keys for the product page
        keys = ['products_title', 'products_paragraf1'] # Add any other keys you need here

        translatable_content = {}
        content_items = TranslatableContent.objects.filter(key__in=keys)

        for item in content_items:
            # Get the content for the current language, e.g., 'content_ca'
            content_value = getattr(item, f'content_{lang}', '')
            translatable_content[item.key] = content_value

        context['translatable_content'] = translatable_content
        # --- End of added part ---

        for product in context['products']:
            for package in product.packages.all():
                package.titles_with_status = self.get_titles_with_status(package.titles.all())
        return context
```

This code fetches the content for `products_paragagraf1` (and any other keys we list) from the database and passes it to the template.

### Step 3: Update the Template to Display the Content

Finally, we need to edit the template file `templates/products/product_list.html` to tell it where to place the new text. You mentioned you want it right after the title.

I would find the title in that file and add your new variable right below it, like so:

```
{% extends 'base.html' %}
{% load static %}

{% block content %}
<main>
    {# This is the title #}
    <h2>{{ translatable_content.products_title|safe }}</h2>

    {# I would add your new paragraph right here #}
    <p>{{ translatable_content.products_paragraf1|safe }}</p>

    {# ... the rest of the page that lists the products ... #}
</main>
{% endblock %}
```

By adding `<p>{{ translatable_content.products_paragraf1|safe }}</p>`, we're telling the page to render the content you created in the admin. The `|safe` filter is important to ensure any HTML you add (like bold tags `<b>`) is rendered correctly.

And that's it! If you'd like me to go ahead and implement this for you, just let me know.

## Bulk-Inserting Titles

To add a large number of titles to the database at once, you can use the `seed_titles.py` script. This script reads title data from `samples/audios.json` and populates the database.

### Step 1: Format Your Titles in JSON

You need to add your titles to the `samples/audios.json` file. Each title should follow this structure:

```json
"your-unique-machine-name": {
  "description": "A brief description of the title.",
  "levels": "A2",
  "ages": "10-16",
  "colection": "Name of the Collection",
  "duration": "00:05:30",
  "text_versions": {
    "CA": {
      "title-human": "El títol en català",
      "Directory": "/AUDIOS/your-unique-machine-name/CA/",
      "json_file": "CA-your-unique-machine-name.json"
    },
    "EN": {
      "title-human": "The title in English",
      "Directory": "/AUDIOS/your-unique-machine-name/EN/",
      "json_file": "EN-your-unique-machine-name.json"
    }
  }
}
```

-   `your-unique-machine-name`: A unique identifier for the title, with no spaces (use hyphens).
-   `description`, `levels`, `ages`, `colection`, `duration`: Metadata fields for the title.
-   `text_versions`: An object containing language-specific information.
    -   `CA`, `EN`, etc.: Language codes.
        -   `title-human`: The display name of the title in that language.
        -   `Directory`: The path to the directory containing the audio files for that language.
        -   `json_file`: The name of the JSON file containing the sentences for that language.

Add each title as a new entry inside the `"AUDIOS": { ... }` block in `samples/audios.json`.

### Step 2: Run the Seeding Command

Once the JSON file is updated, run the following command from the project's root directory:

```bash
python seed_titles.py
```

This will read the JSON file and create the `Title` and `TitleLanguage` entries in the database. The script is designed to skip titles that already exist, so it is safe to run multiple times.
