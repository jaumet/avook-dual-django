document.addEventListener('DOMContentLoaded', function() {
    // Theme toggle logic
    const themeBtn = document.getElementById('themeBtn');
    if (themeBtn) {
        themeBtn.addEventListener('click', () => {
            document.body.classList.toggle('light');

            const isLight = document.body.classList.contains('light');
            if (isLight) {
                themeBtn.textContent = '🌙 Fosc';
            } else {
                themeBtn.textContent = '☀️ Clar';
            }
            // Optional: Save theme preference to localStorage
            // localStorage.setItem('theme', isLight ? 'light' : 'dark');
        });
    }

    // Help modal logic
    const infoModal = document.getElementById('infoModal');
    const infoBtn = document.getElementById('infoBtn');
    const closeModal = document.getElementById('closeModal');

    if (infoBtn) {
        infoBtn.onclick = () => {
            if (infoModal) infoModal.style.display = 'flex';
        };
    }

    if (closeModal) {
        closeModal.onclick = () => {
            if (infoModal) infoModal.style.display = 'none';
        };
    }

    if (infoModal) {
        window.onclick = (event) => {
            if (event.target == infoModal) {
                infoModal.style.display = 'none';
            }
        };
    }

    // Optional: Check for saved theme preference
    // const savedTheme = localStorage.getItem('theme');
    // if (savedTheme === 'light') {
    //     document.body.classList.add('light');
    //     if(themeBtn) themeBtn.textContent = '🌙 Fosc';
    // }
});
