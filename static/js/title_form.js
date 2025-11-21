document.addEventListener('DOMContentLoaded', function() {
    const addFormButton = document.getElementById('add-language-form');
    const formContainer = document.getElementById('language-forms');
    const totalFormsInput = document.querySelector('input[name="languages-TOTAL_FORMS"]');
    const formsetPrefix = 'languages';

    addFormButton.addEventListener('click', function() {
        const formCount = parseInt(totalFormsInput.value);
        const newFormHtml = formContainer.children[0].cloneNode(true);

        // Neteja els valors dels camps clonats
        newFormHtml.querySelectorAll('input, select, textarea').forEach(input => {
            input.value = '';
            if (input.type === 'checkbox' || input.type === 'radio') {
                input.checked = false;
            }
        });

        // Actualitza els atributs 'name' i 'id'
        newFormHtml.innerHTML = newFormHtml.innerHTML.replace(new RegExp(`${formsetPrefix}-(\\d+)-`, 'g'), `${formsetPrefix}-${formCount}-`);

        formContainer.appendChild(newFormHtml);
        totalFormsInput.value = formCount + 1;
    });
});
