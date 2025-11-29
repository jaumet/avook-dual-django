document.addEventListener('DOMContentLoaded', () => {
    const supportedLangs = ['ca', 'en', 'es', 'fr', 'it', 'pt'];
    let translations = {};

    function getCurrentLanguage() {
        const langFromUrl = window.location.pathname.split('/')[1];
        return supportedLangs.includes(langFromUrl) ? langFromUrl : 'ca'; // Default to Catalan
    }

    async function loadTranslations() {
        try {
            const response = await fetch('/static/js/translations.json');
            if (!response.ok) {
                console.error('Failed to load translations file.');
                return;
            }
            translations = await response.json();
            translatePage();
        } catch (error) {
            console.error('Error fetching translations:', error);
        }
    }

    function translatePage() {
        const lang = getCurrentLanguage();
        if (!translations[lang]) {
            console.warn(`No translations found for language: ${lang}`);
            return;
        }

        document.querySelectorAll('[data-translate-key]').forEach(element => {
            const key = element.getAttribute('data-translate-key');
            const translation = translations[lang][key];
            if (translation) {
                // Handle special cases like placeholders
                if (element.placeholder !== undefined) {
                    element.placeholder = translation;
                } else {
                    element.textContent = translation;
                }
            } else {
                console.warn(`No translation found for key: ${key} in language: ${lang}`);
            }
        });
    }

    loadTranslations();
});
