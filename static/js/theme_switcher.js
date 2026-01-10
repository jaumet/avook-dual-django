document.addEventListener('DOMContentLoaded', () => {
    const themeBtn = document.getElementById('themeBtn');
    const body = document.body;

    const applyTheme = (theme) => {
        if (theme === 'light') {
            body.classList.add('light-theme');
            themeBtn.innerHTML = '🌙 <span data-translate-key="header.theme.dark">Fosc</span>';
        } else {
            body.classList.remove('light-theme');
            themeBtn.innerHTML = '☀️ <span data-translate-key="header.theme.light">Clar</span>';
        }
    };

    themeBtn.addEventListener('click', () => {
        const isLightTheme = body.classList.contains('light-theme');
        const newTheme = isLightTheme ? 'dark' : 'light';
        localStorage.setItem('theme', newTheme);
        applyTheme(newTheme);
    });

    const savedTheme = localStorage.getItem('theme') || 'dark';
    applyTheme(savedTheme);
});
