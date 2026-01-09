from products.models import TranslatableContent

def run():
    TranslatableContent.objects.get_or_create(
        key='product_terms',
        defaults={
            'content_ca': """
                <h3>1. Objecte</h3>
                <p>Les presents Condicions Generals de Venda tenen per objecte regular la relació contractual de compravenda nascuda entre el Venedor i el Client en el moment en què aquest accepta la casella corresponent durant el procés de contractació online.</p>
                <h3>2. Durada</h3>
                <p>La relació contractual s'entendrà formalitzada des del moment de la compra i tindrà la durada corresponent al període de subscripció seleccionat pel Client.</p>
            """,
            'content_en': """
                <h3>1. Object</h3>
                <p>The purpose of these General Conditions of Sale is to regulate the contractual sales relationship born between the Seller and the Client at the moment the Client accepts the corresponding box during the online contracting process.</p>
                <h3>2. Duration</h3>
                <p>The contractual relationship will be understood to be formalized from the moment of purchase and will have the duration corresponding to the subscription period selected by the Client.</p>
            """,
            'content_es': """
                <h3>1. Objeto</h3>
                <p>Las presentes Condiciones Generales de Venta tienen por objeto regular la relación contractual de compraventa nacida entre el Vendedor y el Cliente en el momento en que éste acepta la casilla correspondiente durante el proceso de contratación online.</p>
                <h3>2. Duración</h3>
                <p>La relación contractual se entenderá formalizada desde el momento de la compra y tendrá la duración correspondiente al período de suscripción seleccionado por el Cliente.</p>
            """,
            'content_fr': "",
            'content_pt': "",
            'content_de': """
                <h3>1. Gegenstand</h3>
                <p>Zweck dieser Allgemeinen Verkaufsbedingungen ist die Regelung des vertraglichen Kaufverhältnisses, das zwischen dem Verkäufer und dem Kunden in dem Moment entsteht, in dem der Kunde während des Online-Vertragsprozesses das entsprechende Kästchen akzeptiert.</p>
                <h3>2. Dauer</h3>
                <p>Das Vertragsverhältnis gilt ab dem Zeitpunkt des Kaufs als formalisiert und hat die Dauer, die dem vom Kunden gewählten Abonnementzeitraum entspricht.</p>
            """,
            'content_it': ""
        }
    )
