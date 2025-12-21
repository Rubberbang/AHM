let currentLang = localStorage.getItem('lang') || 'pap';

// Function to handle language changes from any selector
function updateLanguage(lang) {
    currentLang = lang;
    localStorage.setItem('lang', lang);
    
    // Update all selectors to match
    document.querySelectorAll('.lang-selector').forEach(sel => {
        sel.value = lang;
    });

    document.querySelectorAll('[data-t]').forEach(el => {
        const key = el.getAttribute('data-t');
        if (TRANSLATIONS[lang]?.[key]) el.innerText = TRANSLATIONS[lang][key];
    });
    renderReflection();
}

// Mobile Menu Toggle
function toggleMenu() {
    const menu = document.getElementById('mobile-menu');
    const icon = document.getElementById('menu-icon');
    const isHidden = menu.classList.contains('hidden');
    
    if (isHidden) {
        menu.classList.remove('hidden');
        lucide.createIcons(); // Re-render icons if needed
    } else {
        menu.classList.add('hidden');
    }
}

// Attach listeners to all language selectors (Desktop and Mobile)
document.querySelectorAll('.lang-selector').forEach(select => {
    select.addEventListener('change', (e) => {
        updateLanguage(e.target.value);
        if (window.location.pathname.includes('calendar.html')) renderEvents();
    });
});

function renderReflection() {
    const textEl = document.getElementById('inspiration-text');
    const refEl = document.getElementById('inspiration-ref');
    if (textEl) {
        textEl.innerText = `"${TRANSLATIONS[currentLang].inspiration_text}"`;
        refEl.innerText = `— ${TRANSLATIONS[currentLang].inspiration_ref}`;
    }
}

function renderEvents() {
    const list = document.getElementById('events-list');
    if (!list) return;
    list.innerHTML = CHOIR_EVENTS.map(event => `
        <div class="bg-white rounded-[1.5rem] md:rounded-[2rem] shadow-sm border border-stone-200 flex flex-col md:flex-row overflow-hidden">
            <div class="md:w-1/4 bg-emerald-900 text-white p-6 md:p-8 flex flex-col items-center justify-center">
                <div class="text-3xl md:text-5xl font-bold">${event.date.split('-')[2]}</div>
                <div class="text-[10px] md:text-xs uppercase opacity-70">${event.date}</div>
            </div>
            <div class="p-6 md:p-8 md:w-3/4">
                <h2 class="text-xl md:text-2xl font-bold text-stone-800 font-serif mb-2">${event.title}</h2>
                <p class="text-stone-500 text-xs md:text-sm mb-4">📍 ${event.location} | ⏰ ${event.time}</p>
                <p class="text-stone-600 text-sm italic border-l-4 border-emerald-100 pl-4">${event.description}</p>
            </div>
        </div>
    `).join('');
}

document.getElementById('contactForm')?.addEventListener('submit', (e) => {
    e.preventDefault();
    document.getElementById('contact-form-container').classList.add('hidden');
    document.getElementById('success-message').classList.remove('hidden');
});

window.onload = () => {
    updateLanguage(currentLang);
    lucide.createIcons();
    renderEvents();
};