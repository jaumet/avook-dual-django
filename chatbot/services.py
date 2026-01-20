import os
from openai import OpenAI
from django.conf import settings
from django.utils import timezone
from products.models import UserPurchase

# It's better to initialize the client once and reuse it.
# Make sure to set CHATBOT_OPENAI_API_KEY in your .env file
api_key = os.getenv('CHATBOT_OPENAI_API_KEY')
if not api_key:
    raise ValueError("CHATBOT_OPENAI_API_KEY environment variable not set.")

client = OpenAI(api_key=api_key)

def get_dual_method_explanation():
    """
    Returns a static, detailed explanation of the Dual method.
    This content should be curated to be as effective as possible for the GPT model.
    """
    return """
    **El Mètode Dual: Una Immersió Lingüística Completa**

    El mètode Dual es basa en la immersió total i l'aprenentatge actiu, simulant com aprenem la nostra llengua materna. No es tracta de memoritzar regles gramaticals, sinó d'adquirir l'idioma de manera natural. Els pilars fonamentals són:

    1.  **Escolta Activa (Listening):** Comences escoltant àudios de converses quotidianes, notícies o històries. L'objectiu és acostumar la teva oïda als sons, ritmes i entonacions de l'idioma. Al principi, potser no entens res, però el teu cervell comença a reconèixer patrons.

    2.  **Lectura i Escolta Simultànies (Reading + Listening):** Després d'haver escoltat un àudio diverses vegades, el llegeixes mentre el tornes a escoltar. Aquesta tècnica connecta els sons que ja has començat a reconèixer amb les paraules escrites. És un pas crucial per associar grafia i fonètica.

    3.  **Repetició en Veu Alta (Shadowing):** Intentes repetir el que diu l'àudio, imitant la pronunciació i l'entonació de la manera més fidel possible. Aquest exercici entrena els teus músculs facials per produir nous sons i millora dràsticament la teva fluïdesa.

    4.  **Comprensió Profunda:** Només després d'haver passat per les fases anteriors, busques el significat de les paraules o frases que no coneixes. D'aquesta manera, aprens vocabulari en context, la qual cosa facilita molt la seva retenció.

    El teu rol com a tutor és guiar l'usuari a través d'aquest procés, resoldre dubtes sobre vocabulari o expressions idiomàtiques, i oferir exemples pràctics. Actua com un company d'aprenentatge, no com un professor tradicional.
    """

def get_user_active_products(user):
    """
    Fetches the list of active products for a given user.
    """
    active_purchases = UserPurchase.objects.filter(
        user=user,
        expiry_date__gte=timezone.now().date()
    )
    product_names = [purchase.product.name for purchase in active_purchases]
    if not product_names:
        return "L'usuari no té productes actius en aquest moment."
    return "Productes actius de l'usuari: " + ", ".join(product_names)

def get_openai_response(user, user_message_content, session):
    """
    Constructs the prompt and gets a response from the OpenAI API.
    """
    system_prompt = get_dual_method_explanation()
    user_context = get_user_active_products(user)

    full_system_prompt = f"{system_prompt}\n\nContext addicional sobre l'usuari actual: {user_context}"

    # Retrieve the last 10 messages to maintain conversation context
    messages = list(session.messages.order_by('-created_at')[:10])
    messages.reverse()

    conversation_history = [{"role": msg.role, "content": msg.content} for msg in messages]

    # The first message should be the system prompt, followed by the history.
    api_messages = [
        {"role": "system", "content": full_system_prompt},
    ] + conversation_history

    try:
        model_name = getattr(settings, 'CHATBOT_OPENAI_MODEL', 'gpt-4')
        completion = client.chat.completions.create(
            model=model_name,
            messages=api_messages
        )
        return completion.choices[0].message.content
    except Exception as e:
        # Handle potential API errors, rate limits, etc.
        print(f"OpenAI API call failed: {e}")
        raise
