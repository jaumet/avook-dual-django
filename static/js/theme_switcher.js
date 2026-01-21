document.addEventListener('DOMContentLoaded', () => {
    const themeBtn = document.getElementById('themeBtn');
    if (!themeBtn) return;

    const body = document.body;

    const applyTheme = (theme) => {
        if (theme === 'light') {
            body.classList.add('light');
            themeBtn.innerHTML = '🌙 <span data-translate-key="header.theme.dark">Fosc</span>';
        } else {
            body.classList.remove('light');
            themeBtn.innerHTML = '☀️ <span data-translate-key="header.theme.light">Clar</span>';
        }
        // If translator exists, re-translate to handle the new span
        if (window.translatePage) {
            window.translatePage();
        }
    };

    themeBtn.addEventListener('click', () => {
        const isLightTheme = body.classList.contains('light');
        const newTheme = isLightTheme ? 'dark' : 'light';
        localStorage.setItem('theme', newTheme);
        applyTheme(newTheme);
    });

    const savedTheme = localStorage.getItem('theme') || 'dark';
    // We don't necessarily need to updateBody here because the inline script
    // in base.html already did it, but it doesn't hurt.
    applyTheme(savedTheme);
});
