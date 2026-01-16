from products.models import Product, ProductTranslation, Package, Title

def run():
    # Clear existing products and packages to ensure a clean slate
    Product.objects.all().delete()
    Package.objects.all().delete()

    # Create Packages for each level and assign all titles of that level
    levels = ['A0', 'A1', 'A2', 'B1', 'B2', 'C1']
    packages = {}
    for level in levels:
        package, created = Package.objects.get_or_create(name=level, level=level)
        titles = Title.objects.filter(level=level)
        package.titles.set(titles)
        packages[level] = package

    # Product 1: Dual Start
    product_start = Product.objects.create(machine_name='dual-start', price=19, duration=3, category='start')
    product_start.packages.add(packages['A0'], packages['A1'])
    translations_start = {
        'ca': {
            'name': 'Dual Start',
            'description': """<p class="dual-meta">A0–A1 · Accés 3 mesos · <strong>19 €</strong></p>
<p class="dual-desc">Ideal per començar des de zero o gairebé zero. Accés a tots els textos <strong>A0 i A1</strong> en <strong>7 llengües</strong>, amb històries molt curtes (1–3 minuts) i frases simples.</p>
<ul class="dual-features">
    <li>✔ Textos breus i molt guiats</li>
    <li>✔ Mètode Dual frase a frase (L1↔L2)</li>
    <li>✔ Pensat per perdre la por des del primer dia</li>
</ul>"""
        },
        'en': {
            'name': 'Dual Start',
            'description': """<p class="dual-meta">A0–A1 · 3-month access · <strong>19 €</strong></p>
<p class="dual-desc">Ideal for starting from scratch or almost from scratch. Access to all <strong>A0 and A1</strong> texts in <strong>7 languages</strong>, with very short stories (1–3 minutes) and simple sentences.</p>
<ul class="dual-features">
    <li>✔ Short and highly guided texts</li>
    <li>✔ Dual method sentence by sentence (L1↔L2)</li>
    <li>✔ Designed to lose fear from day one</li>
</ul>"""
        },
        'es': {
            'name': 'Dual Start',
            'description': """<p class="dual-meta">A0–A1 · Acceso 3 meses · <strong>19 €</strong></p>
<p class="dual-desc">Ideal para empezar desde cero o casi cero. Acceso a todos los textos <strong>A0 y A1</strong> en <strong>7 idiomas</strong>, con historias muy cortas (1–3 minutos) y frases simples.</p>
<ul class="dual-features">
    <li>✔ Textos breves y muy guiados</li>
    <li>✔ Método Dual frase a frase (L1↔L2)</li>
    <li>✔ Pensado para perder el miedo desde el primer día</li>
</ul>"""
        },
        'fr': {
            'name': 'Dual Start',
            'description': """<p class="dual-meta">A0–A1 · Accès 3 mois · <strong>19 €</strong></p>
<p class="dual-desc">Idéal pour commencer de zéro ou presque. Accès à tous les textes <strong>A0 et A1</strong> en <strong>7 langues</strong>, avec des histoires très courtes (1–3 minutes) et des phrases simples.</p>
<ul class="dual-features">
    <li>✔ Textes courts et très guidés</li>
    <li>✔ Méthode Dual phrase par phrase (L1↔L2)</li>
    <li>✔ Conçu pour perdre la peur dès le premier jour</li>
</ul>"""
        },
        'de': {
            'name': 'Dual Start',
            'description': """<p class="dual-meta">A0–A1 · 3 Monate Zugang · <strong>19 €</strong></p>
<p class="dual-desc">Ideal, um von Grund auf oder fast von Grund auf anzufangen. Zugang zu allen <strong>A0 und A1</strong> Texten in <strong>7 Sprachen</strong>, mit sehr kurzen Geschichten (1–3 Minuten) und einfachen Sätzen.</p>
<ul class="dual-features">
    <li>✔ Kurze und sehr geführte Texte</li>
    <li>✔ Duale Methode Satz für Satz (L1↔L2)</li>
    <li>✔ Entwickelt, um die Angst vom ersten Tag an zu verlieren</li>
</ul>"""
        },
        'it': {
            'name': 'Dual Start',
            'description': """<p class="dual-meta">A0–A1 · Accesso 3 mesi · <strong>19 €</strong></p>
<p class="dual-desc">Ideale per iniziare da zero o quasi. Accesso a tutti i testi <strong>A0 e A1</strong> in <strong>7 lingue</strong>, con storie molto brevi (1–3 minuti) e frasi semplici.</p>
<ul class="dual-features">
    <li>✔ Testi brevi e molto guidati</li>
    <li>✔ Metodo Dual frase per frase (L1↔L2)</li>
    <li>✔ Pensato per perdere la paura dal primo giorno</li>
</ul>"""
        },
        'pt': {
            'name': 'Dual Start',
            'description': """<p class="dual-meta">A0–A1 · Acesso 3 meses · <strong>19 €</strong></p>
<p class="dual-desc">Ideal para começar do zero ou quase do zero. Acesso a todos os textos <strong>A0 e A1</strong> em <strong>7 línguas</strong>, com histórias muito curtas (1–3 minutos) e frases simples.</p>
<ul class="dual-features">
    <li>✔ Textos curtos e muito guiados</li>
    <li>✔ Método Dual frase a frase (L1↔L2)</li>
    <li>✔ Projetado para perder o medo desde o primeiro dia</li>
</ul>"""
        }
    }
    for lang, data in translations_start.items():
        ProductTranslation.objects.create(product=product_start, language_code=lang, name=data['name'], description=data['description'])

    # Product 2: Dual Progress
    product_progress = Product.objects.create(machine_name='dual-progress', price=29, duration=3, category='progress')
    product_progress.packages.add(packages['A2'], packages['B1'])
    translations_progress = {
        'ca': {
            'name': 'Dual Progress',
            'description': """<p class="dual-meta">A2–B1 · Accés 3 mesos · <strong>29 €</strong></p>
<p class="dual-desc">Per a qui ja entén una mica la llengua i vol <strong>guanyar fluïdesa</strong>. Accés als textos <strong>A2 i B1</strong>, amb històries més llargues i vocabulari més ric.</p>
<ul class="dual-features">
    <li>✔ Textos de 3–5 minuts</li>
    <li>✔ Consolidació de comprensió i ritme</li>
    <li>✔ Pas natural cap a la llengua funcional</li>
</ul>"""
        },
        'en': {
            'name': 'Dual Progress',
            'description': """<p class="dual-meta">A2–B1 · 3-month access · <strong>29 €</strong></p>
<p class="dual-desc">For those who already understand the language a bit and want to <strong>gain fluency</strong>. Access to <strong>A2 and B1</strong> texts, with longer stories and richer vocabulary.</p>
<ul class="dual-features">
    <li>✔ Texts of 3–5 minutes</li>
    <li>✔ Consolidation of comprehension and rhythm</li>
    <li>✔ Natural step towards functional language</li>
</ul>"""
        },
        'es': {
            'name': 'Dual Progress',
            'description': """<p class="dual-meta">A2–B1 · Acceso 3 meses · <strong>29 €</strong></p>
<p class="dual-desc">Para quien ya entiende un poco el idioma y quiere <strong>ganar fluidez</strong>. Acceso a los textos <strong>A2 y B1</strong>, con historias más largas y vocabulario más rico.</p>
<ul class="dual-features">
    <li>✔ Textos de 3–5 minutos</li>
    <li>✔ Consolidación de comprensión y ritmo</li>
    <li>✔ Paso natural hacia el lenguaje funcional</li>
</ul>"""
        },
        'fr': {
            'name': 'Dual Progress',
            'description': """<p class="dual-meta">A2–B1 · Accès 3 mois · <strong>29 €</strong></p>
<p class="dual-desc">Pour ceux qui comprennent déjà un peu la langue et veulent <strong>gagner en fluidité</strong>. Accès aux textes <strong>A2 et B1</strong>, avec des histoires plus longues et un vocabulaire plus riche.</p>
<ul class="dual-features">
    <li>✔ Textes de 3–5 minutes</li>
    <li>✔ Consolidation de la compréhension et du rythme</li>
    <li>✔ Pas naturel vers une langue fonctionnelle</li>
</ul>"""
        },
        'de': {
            'name': 'Dual Progress',
            'description': """<p class="dual-meta">A2–B1 · 3 Monate Zugang · <strong>29 €</strong></p>
<p class="dual-desc">Für diejenigen, die die Sprache bereits ein wenig verstehen und <strong>flüssiger werden möchten</strong>. Zugang zu den Texten <strong>A2 und B1</strong>, mit längeren Geschichten und reichhaltigerem Vokabular.</p>
<ul class="dual-features">
    <li>✔ Texte von 3–5 Minuten</li>
    <li>✔ Festigung des Verständnisses und des Rhythmus</li>
    <li>✔ Natürlicher Schritt zur funktionalen Sprache</li>
</ul>"""
        },
        'it': {
            'name': 'Dual Progress',
            'description': """<p class="dual-meta">A2–B1 · Accesso 3 mesi · <strong>29 €</strong></p>
<p class="dual-desc">Per chi già capisce un po' la lingua e vuole <strong>acquisire fluidità</strong>. Accesso ai testi <strong>A2 e B1</strong>, con storie più lunghe e vocabolario più ricco.</p>
<ul class="dual-features">
    <li>✔ Testi di 3–5 minuti</li>
    <li>✔ Consolidamento della comprensione e del ritmo</li>
    <li>✔ Passo naturale verso una lingua funzionale</li>
</ul>"""
        },
        'pt': {
            'name': 'Dual Progress',
            'description': """<p class="dual-meta">A2–B1 · Acesso 3 meses · <strong>29 €</strong></p>
<p class="dual-desc">Para quem já entende um pouco da língua e quer <strong>ganhar fluência</strong>. Acesso aos textos <strong>A2 e B1</strong>, com histórias mais longas e vocabulário mais rico.</p>
<ul class="dual-features">
    <li>✔ Textos de 3–5 minutos</li>
    <li>✔ Consolidação da compreensão e do ritmo</li>
    <li>✔ Passo natural para a língua funcional</li>
</ul>"""
        }
    }
    for lang, data in translations_progress.items():
        ProductTranslation.objects.create(product=product_progress, language_code=lang, name=data['name'], description=data['description'])

    # Product 3: Dual Advanced
    product_advanced = Product.objects.create(machine_name='dual-advanced', price=36, duration=3, category='advanced')
    product_advanced.packages.add(packages['B2'], packages['C1'])
    translations_advanced = {
        'ca': {
            'name': 'Dual Advanced',
            'description': """<p class="dual-meta">B2–C1 · Accés 3 mesos · <strong>36 €</strong></p>
<p class="dual-desc">Pensat per treballar llengua <strong>real</strong>: registres, matisos i precisió. Accés als textos <strong>B2 i C1</strong>, amb llenguatge natural i històries llargues.</p>
<ul class="dual-features">
    <li>✔ Textos de 5–12 minuts</li>
    <li>✔ Comprensió profunda i vocabulari avançat</li>
    <li>✔ Ideal per perfeccionar la llengua</li>
</ul>"""
        },
        'en': {
            'name': 'Dual Advanced',
            'description': """<p class="dual-meta">B2–C1 · 3-month access · <strong>36 €</strong></p>
<p class="dual-desc">Designed to work with <strong>real</strong> language: registers, nuances, and precision. Access to <strong>B2 and C1</strong> texts, with natural language and long stories.</p>
<ul class="dual-features">
    <li>✔ Texts of 5–12 minutes</li>
    <li>✔ Deep comprehension and advanced vocabulary</li>
    <li>✔ Ideal for perfecting the language</li>
</ul>"""
        },
        'es': {
            'name': 'Dual Advanced',
            'description': """<p class="dual-meta">B2–C1 · Acceso 3 meses · <strong>36 €</strong></p>
<p class="dual-desc">Pensado para trabajar con lenguaje <strong>real</strong>: registros, matices y precisión. Acceso a los textos <strong>B2 y C1</strong>, con lenguaje natural e historias largas.</p>
<ul class="dual-features">
    <li>✔ Textos de 5–12 minutos</li>
    <li>✔ Comprensión profunda y vocabulario avanzado</li>
    <li>✔ Ideal para perfeccionar el idioma</li>
</ul>"""
        },
        'fr': {
            'name': 'Dual Advanced',
            'description': """<p class="dual-meta">B2–C1 · Accès 3 mois · <strong>36 €</strong></p>
<p class="dual-desc">Conçu pour travailler avec une langue <strong>réelle</strong> : registres, nuances et précision. Accès aux textes <strong>B2 et C1</strong>, avec un langage naturel et des histoires longues.</p>
<ul class="dual-features">
    <li>✔ Textes de 5–12 minutes</li>
    <li>✔ Compréhension approfondie et vocabulaire avancé</li>
    <li>✔ Idéal pour perfectionner la langue</li>
</ul>"""
        },
        'de': {
            'name': 'Dual Advanced',
            'description': """<p class="dual-meta">B2–C1 · 3 Monate Zugang · <strong>36 €</strong></p>
<p class="dual-desc">Entwickelt, um mit <strong>echter</strong> Sprache zu arbeiten: Register, Nuancen und Präzision. Zugang zu den Texten <strong>B2 und C1</strong>, mit natürlicher Sprache und langen Geschichten.</p>
<ul class="dual-features">
    <li>✔ Texte von 5–12 Minuten</li>
    <li>✔ Tiefes Verständnis und fortgeschrittener Wortschatz</li>
    <li>✔ Ideal zur Perfektionierung der Sprache</li>
</ul>"""
        },
        'it': {
            'name': 'Dual Advanced',
            'description': """<p class="dual-meta">B2–C1 · Accesso 3 mesi · <strong>36 €</strong></p>
<p class="dual-desc">Progettato per lavorare con la lingua <strong>reale</strong>: registri, sfumature e precisione. Accesso ai testi <strong>B2 e C1</strong>, con linguaggio naturale e storie lunghe.</p>
<ul class="dual-features">
    <li>✔ Testi di 5–12 minuti</li>
    <li>✔ Comprensione profonda e vocabolario avanzato</li>
    <li>✔ Ideale per perfezionare la lingua</li>
</ul>"""
        },
        'pt': {
            'name': 'Dual Advanced',
            'description': """<p class="dual-meta">B2–C1 · Acesso 3 meses · <strong>36 €</strong></p>
<p class="dual-desc">Projetado para trabalhar com a língua <strong>real</strong>: registros, nuances e precisão. Acesso aos textos <strong>B2 e C1</strong>, com linguagem natural e histórias longas.</p>
<ul class="dual-features">
    <li>✔ Textos de 5–12 minutos</li>
    <li>✔ Compreensão profunda e vocabulário avançado</li>
    <li>✔ Ideal para aperfeiçoar a língua</li>
</ul>"""
        }
    }
    for lang, data in translations_advanced.items():
        ProductTranslation.objects.create(product=product_advanced, language_code=lang, name=data['name'], description=data['description'])

    # Product 4: Dual Full Access
    product_full = Product.objects.create(machine_name='dual-full-access', price=49, duration=6, category='full_access')
    product_full.packages.set(packages.values())
    translations_full = {
        'ca': {
            'name': 'Dual Full Access',
            'description': """<p class="dual-meta">A0–C1 · Accés 6 mesos · <strong>49 €</strong></p>
<p class="dual-desc">Accés complet a <strong>tots els nivells i tots els textos</strong> del mètode Dual. La millor opció si vols seguir un recorregut complet, al teu ritme.</p>
<ul class="dual-features">
    <li>✔ De principiant absolut a avançat</li>
    <li>✔ Màxima flexibilitat de combinacions</li>
    <li>✔ Tot el mètode Dual, sense límits</li>
</ul>"""
        },
        'en': {
            'name': 'Dual Full Access',
            'description': """<p class="dual-meta">A0–C1 · 6-month access · <strong>49 €</strong></p>
<p class="dual-desc">Full access to <strong>all levels and all texts</strong> of the Dual method. The best option if you want to follow a complete journey, at your own pace.</p>
<ul class="dual-features">
    <li>✔ From absolute beginner to advanced</li>
    <li>✔ Maximum flexibility of combinations</li>
    <li>✔ The entire Dual method, without limits</li>
</ul>"""
        },
        'es': {
            'name': 'Dual Full Access',
            'description': """<p class="dual-meta">A0–C1 · Acceso 6 meses · <strong>49 €</strong></p>
<p class="dual-desc">Acceso completo a <strong>todos los niveles y todos los textos</strong> del método Dual. La mejor opción si quieres seguir un recorrido completo, a tu ritmo.</p>
<ul class="dual-features">
    <li>✔ De principiante absoluto a avanzado</li>
    <li>✔ Máxima flexibilidad de combinaciones</li>
    <li>✔ Todo el método Dual, sin límites</li>
</ul>"""
        },
        'fr': {
            'name': 'Dual Full Access',
            'description': """<p class="dual-meta">A0–C1 · Accès 6 mois · <strong>49 €</strong></p>
<p class="dual-desc">Accès complet à <strong>tous les niveaux et tous les textes</strong> de la méthode Dual. La meilleure option si vous voulez suivre un parcours complet, à votre rythme.</p>
<ul class="dual-features">
    <li>✔ Du débutant absolu à avancé</li>
    <li>✔ Flexibilité maximale des combinaisons</li>
    <li>✔ Toute la méthode Dual, sans limites</li>
</ul>"""
        },
        'de': {
            'name': 'Dual Full Access',
            'description': """<p class="dual-meta">A0–C1 · 6 Monate Zugang · <strong>49 €</strong></p>
<p class="dual-desc">Vollständiger Zugang zu <strong>allen Niveaus und allen Texten</strong> der Dual-Methode. Die beste Option, wenn Sie eine vollständige Reise in Ihrem eigenen Tempo machen möchten.</p>
<ul class="dual-features">
    <li>✔ Vom absoluten Anfänger bis zum Fortgeschrittenen</li>
    <li>✔ Maximale Flexibilität der Kombinationen</li>
    <li>✔ Die gesamte Dual-Methode, ohne Grenzen</li>
</ul>"""
        },
        'it': {
            'name': 'Dual Full Access',
            'description': """<p class="dual-meta">A0–C1 · Accesso 6 mesi · <strong>49 €</strong></p>
<p class="dual-desc">Accesso completo a <strong>tutti i livelli e tutti i testi</strong> del metodo Dual. La migliore opzione se vuoi seguire un percorso completo, al tuo ritmo.</p>
<ul class="dual-features">
    <li>✔ Da principiante assoluto ad avanzato</li>
    <li>✔ Massima flessibilità di combinazioni</li>
    <li>✔ L'intero metodo Dual, senza limiti</li>
</ul>"""
        },
        'pt': {
            'name': 'Dual Full Access',
            'description': """<p class="dual-meta">A0–C1 · Acesso 6 meses · <strong>49 €</strong></p>
<p class="dual-desc">Acesso completo a <strong>todos os níveis e todos os textos</strong> do método Dual. A melhor opção se você quer seguir uma jornada completa, no seu próprio ritmo.</p>
<ul class="dual-features">
    <li>✔ Do iniciante absoluto ao avançado</li>
    <li>✔ Máxima flexibilidade de combinações</li>
    <li>✔ Todo o método Dual, sem limites</li>
</ul>"""
        }
    }
    for lang, data in translations_full.items():
        ProductTranslation.objects.create(product=product_full, language_code=lang, name=data['name'], description=data['description'])

    # Product 5: Dual Free Test
    product_free = Product.objects.create(machine_name='dual-free-test', price=0, duration=0, category='free')
    product_free.packages.add(packages['A0'])
    translations_free = {
        'ca': {'name': 'Dual Free Test', 'description': 'Producte de prova gratuït'},
        'en': {'name': 'Dual Free Test', 'description': 'Free test product'},
        'es': {'name': 'Dual Free Test', 'description': 'Producto de prueba gratuito'},
        'fr': {'name': 'Dual Free Test', 'description': 'Produit de test gratuit'},
        'de': {'name': 'Dual Free Test', 'description': 'Kostenloses Testprodukt'},
        'it': {'name': 'Dual Free Test', 'description': 'Prodotto di prova gratuito'},
        'pt': {'name': 'Dual Free Test', 'description': 'Produto de teste gratuito'}
    }
    for lang, data in translations_free.items():
        ProductTranslation.objects.create(product=product_free, language_code=lang, name=data['name'], description=data['description'])

    print("Database seeded successfully with new products and packages.")
