document.addEventListener('DOMContentLoaded', function() {
    // View/Edit mode toggle logic
    const viewMode = document.getElementById('view-mode');
    const editMode = document.getElementById('edit-mode');
    const editButton = document.getElementById('edit-button');
    const cancelButton = document.getElementById('cancel-button');

    if (editButton) {
        editButton.addEventListener('click', () => {
            viewMode.style.display = 'none';
            editMode.style.display = 'block';
        });
    }

    if (cancelButton) {
        cancelButton.addEventListener('click', () => {
            editMode.style.display = 'none';
            viewMode.style.display = 'block';
        });
    }

    // Form logic for dynamic language fields
    const languageLevels = ['A0', 'A1', 'A2', 'B1', 'B2', 'C1', 'C2'];
    let languages = [];

    // This path is now relative to the static folder, but we need to pass the initial form data
    const knownLanguagesInput = document.querySelector('input[name="known_languages"]');
    const learningLanguagesInput = document.querySelector('input[name="learning_languages"]');
    const languagesJsonUrl = document.body.dataset.languagesUrl;

    if (!languagesJsonUrl || !knownLanguagesInput || !learningLanguagesInput) {
        return; // Don't run the rest of the script if essential elements are missing
    }

    fetch(languagesJsonUrl)
        .then(response => response.json())
        .then(data => {
            languages = data.Lang_list;
            populateInitialData();
            setupEventListeners();
        });

    function createLanguageRow(container, language = '', level = 'A0') {
        const row = document.createElement('div');
        row.classList.add('language-row', 'form-row', 'mb-2');

        const langGroup = document.createElement('div');
        langGroup.classList.add('col');
        const langInput = document.createElement('input');
        langInput.type = 'text';
        langInput.name = 'language';
        langInput.value = language;
        langInput.classList.add('form-control');
        langInput.setAttribute('list', 'languages-datalist');
        langGroup.appendChild(langInput);

        const levelGroup = document.createElement('div');
        levelGroup.classList.add('col');
        const levelSelect = document.createElement('select');
        levelSelect.name = 'level';
        levelSelect.classList.add('form-control');
        languageLevels.forEach(lvl => {
            const option = document.createElement('option');
            option.value = lvl;
            option.textContent = lvl;
            if (lvl === level) {
                option.selected = true;
            }
            levelSelect.appendChild(option);
        });
        levelGroup.appendChild(levelSelect);

        const removeGroup = document.createElement('div');
        removeGroup.classList.add('col-auto');
        const removeButton = document.createElement('button');
        removeButton.type = 'button';
        removeButton.textContent = 'Eliminar';
        removeButton.classList.add('btn', 'btn-danger');
        removeButton.addEventListener('click', () => row.remove());
        removeGroup.appendChild(removeButton);

        row.appendChild(langGroup);
        row.appendChild(levelGroup);
        row.appendChild(removeGroup);
        container.appendChild(row);
    }

    function populateInitialData() {
        // We get the data from the global variables defined in the template
        const knownLanguages = window.knownLanguagesData || [];
        const learningLanguages = window.learningLanguagesData || [];

        const knownContainer = document.getElementById('known-languages-container');
        const learningContainer = document.getElementById('learning-languages-container');

        if (knownContainer) knownContainer.innerHTML = ''; // Clear previous
        if (learningContainer) learningContainer.innerHTML = ''; // Clear previous

        if (knownContainer) knownLanguages.forEach(lang => createLanguageRow(knownContainer, lang.language, lang.level));
        if (learningContainer) learningLanguages.forEach(lang => createLanguageRow(learningContainer, lang.language, lang.level));

        if (!document.getElementById('languages-datalist')) {
            const datalist = document.createElement('datalist');
            datalist.id = 'languages-datalist';
            languages.forEach(lang => {
                const option = document.createElement('option');
                option.value = lang.nom;
                datalist.appendChild(option);
            });
            document.body.appendChild(datalist);
        }
    }

    function setupEventListeners() {
        const addKnownBtn = document.getElementById('add-known-language');
        if (addKnownBtn) {
            addKnownBtn.addEventListener('click', () => {
                createLanguageRow(document.getElementById('known-languages-container'));
            });
        }

        const addLearningBtn = document.getElementById('add-learning-language');
        if (addLearningBtn) {
            addLearningBtn.addEventListener('click', () => {
                createLanguageRow(document.getElementById('learning-languages-container'));
            });
        }

        const form = document.querySelector('#edit-mode form');
        if (form) {
            form.addEventListener('submit', function(event) {
                const knownContainer = document.getElementById('known-languages-container');
                const learningContainer = document.getElementById('learning-languages-container');

                const knownData = Array.from(knownContainer.querySelectorAll('.language-row')).map(row => ({
                    language: row.querySelector('input[name="language"]').value,
                    level: row.querySelector('select[name="level"]').value
                }));
                const learningData = Array.from(learningContainer.querySelectorAll('.language-row')).map(row => ({
                    language: row.querySelector('input[name="language"]').value,
                    level: row.querySelector('select[name="level"]').value
                }));

                knownLanguagesInput.value = JSON.stringify(knownData);
                learningLanguagesInput.value = JSON.stringify(learningData);
            });
        }
    }
});
