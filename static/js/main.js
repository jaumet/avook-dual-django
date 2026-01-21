document.addEventListener('DOMContentLoaded', function() {
    // Hamburger menu toggle
    const menuToggle = document.getElementById('menuToggle');
    const headerRight = document.querySelector('.main-header .header-right');
    if (menuToggle && headerRight) {
        const toggleMenu = (e) => {
            e.preventDefault();
            e.stopPropagation();
            headerRight.classList.toggle('active');
            menuToggle.classList.toggle('active');

            // Prevent scrolling when menu is open
            if (headerRight.classList.contains('active')) {
                document.body.style.overflow = 'hidden';
            } else {
                document.body.style.overflow = '';
            }
        };

        menuToggle.addEventListener('click', toggleMenu);

        // Close menu when clicking outside
        document.addEventListener('click', (e) => {
            if (headerRight.classList.contains('active') &&
                !headerRight.contains(e.target) &&
                !menuToggle.contains(e.target)) {
                headerRight.classList.remove('active');
                menuToggle.classList.remove('active');
                document.body.style.overflow = '';
            }
        });

        // Close menu when clicking on a link (for mobile UX)
        headerRight.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                headerRight.classList.remove('active');
                menuToggle.classList.remove('active');
                document.body.style.overflow = '';
            });
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

});
