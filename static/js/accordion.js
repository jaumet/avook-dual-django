document.addEventListener('DOMContentLoaded', function() {
    const accordions = document.querySelectorAll('.accordion-header');
    accordions.forEach(accordion => {
        accordion.addEventListener('click', function() {
            this.classList.toggle('active');
            const content = this.nextElementSibling;
            if (content.style.display === 'block') {
                content.style.display = 'none';
                this.querySelector('.accordion-icon').textContent = '+';
            } else {
                content.style.display = 'block';
                this.querySelector('.accordion-icon').textContent = '-';
            }
        });
    });
});
