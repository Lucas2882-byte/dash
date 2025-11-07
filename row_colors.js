// Fonction pour appliquer les couleurs de lignes dans les dialogues
function applyRowColorsInline() {
    const dialog = document.querySelector('[data-testid="stDialog"]');
    if (!dialog) return 0;
    
    const dataframe = dialog.querySelector('div[data-testid="stDataFrame"]');
    if (!dataframe) return 0;
    
    const rows = dataframe.querySelectorAll('div[role="row"]');
    let coloredCount = 0;
    
    rows.forEach((row, index) => {
        if (index === 0) return; // Skip header row
        
        const cells = row.querySelectorAll('div[role="gridcell"]');
        let hasUrgente = false;
        let hasNormale = false;
        
        cells.forEach(cell => {
            const text = cell.textContent || cell.innerText || '';
            if (text.trim() === 'Urgente') {
                hasUrgente = true;
            } else if (text.trim() === 'Normale') {
                hasNormale = true;
            }
        });
        
        if (hasUrgente) {
            row.style.backgroundColor = 'rgba(239, 68, 68, 0.15)';
            row.style.setProperty('background-color', 'rgba(239, 68, 68, 0.15)', 'important');
            cells.forEach(cell => {
                cell.style.backgroundColor = 'rgba(239, 68, 68, 0.15)';
                cell.style.setProperty('background-color', 'rgba(239, 68, 68, 0.15)', 'important');
            });
            coloredCount++;
        } else if (hasNormale) {
            row.style.backgroundColor = 'rgba(34, 197, 94, 0.15)';
            row.style.setProperty('background-color', 'rgba(34, 197, 94, 0.15)', 'important');
            cells.forEach(cell => {
                cell.style.backgroundColor = 'rgba(34, 197, 94, 0.15)';
                cell.style.setProperty('background-color', 'rgba(34, 197, 94, 0.15)', 'important');
            });
            coloredCount++;
        }
    });
    
    return coloredCount;
}

// Fonction pour appliquer les couleurs de lignes dans l'onglet "Par Personne"
function applyRowColorsPerson() {
    const rows = document.querySelectorAll('div[data-testid="stDataFrame"] tbody tr');
    rows.forEach(row => {
        const cells = row.querySelectorAll('td');
        let hasUrgente = false;
        let hasNormale = false;
        cells.forEach(cell => {
            const text = cell.textContent || cell.innerText || '';
            if (text.includes('Urgente')) hasUrgente = true;
            else if (text.includes('Normale')) hasNormale = true;
        });
        if (hasUrgente) {
            row.classList.add('row-urgente');
            row.classList.remove('row-normale');
        } else if (hasNormale) {
            row.classList.add('row-normale');
            row.classList.remove('row-urgente');
        }
    });
}

// Initialiser la coloration pour les dialogues
function initDialogRowColors() {
    // Nettoyer l'interval précédent
    if (window.colorRowsInterval) {
        clearInterval(window.colorRowsInterval);
    }
    
    // Appliquer immédiatement
    setTimeout(applyRowColorsInline, 100);
    setTimeout(applyRowColorsInline, 300);
    setTimeout(applyRowColorsInline, 600);
    setTimeout(applyRowColorsInline, 1000);
    setTimeout(applyRowColorsInline, 2000);
    
    // Continuer à réappliquer toutes les 500ms pendant 10 secondes
    let attempts = 0;
    window.colorRowsInterval = setInterval(() => {
        const colored = applyRowColorsInline();
        attempts++;
        
        // Arrêter après 20 tentatives (10 secondes) ou si on a coloré au moins une ligne
        if (attempts > 20 || (colored > 0 && attempts > 5)) {
            clearInterval(window.colorRowsInterval);
        }
    }, 500);
}

// Initialiser la coloration pour l'onglet "Par Personne"
function initPersonRowColors() {
    setTimeout(applyRowColorsPerson, 100);
    setTimeout(applyRowColorsPerson, 300);
    setTimeout(applyRowColorsPerson, 500);
    setTimeout(applyRowColorsPerson, 1000);
    const observerPerson = new MutationObserver(() => applyRowColorsPerson());
    setTimeout(() => {
        observerPerson.observe(document.body, { 
            childList: true, 
            subtree: true,
            attributes: false,
            characterData: false
        });
    }, 100);
}
