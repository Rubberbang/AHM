/**
 * main.js - Production Version
 */
const API_BASE_URL = "https://api.ahmkoor.com/api";
let currentLang = localStorage.getItem('lang') || 'pap';

function updateLanguage(lang) {
    currentLang = lang;
    localStorage.setItem('lang', lang);
    document.querySelectorAll('.lang-selector').forEach(sel => sel.value = lang);
    document.querySelectorAll('[data-t]').forEach(el => {
        const key = el.getAttribute('data-t');
        if (TRANSLATIONS[lang]?.[key]) el.innerText = TRANSLATIONS[lang][key];
    });
    renderReflection();
}

function toggleMenu() {
    const menu = document.getElementById('mobile-menu');
    if (menu) menu.classList.toggle('hidden');
    lucide.createIcons();
}

function renderReflection() {
    const textEl = document.getElementById('inspiration-text');
    const refEl = document.getElementById('inspiration-ref');
    if (textEl && TRANSLATIONS[currentLang]) {
        textEl.innerText = `"${TRANSLATIONS[currentLang].inspiration_text}"`;
        refEl.innerText = `— ${TRANSLATIONS[currentLang].inspiration_ref}`;
    }
}

// NEW: Check Database for Theme Color Update
async function checkThemeColor() {
    try {
        const res = await fetch(`${API_BASE_URL}/content`);
        if (!res.ok) return;
        const data = await res.json();

        if (data.theme_color) {
            const current = localStorage.getItem('theme_color');
            if (current !== data.theme_color) {
                // If DB is different from Browser, update and refresh to apply
                localStorage.setItem('theme_color', data.theme_color);
                location.reload();
            }
        }
    } catch (e) { console.log("Theme check failed"); }
}

async function renderEvents() {
    const list = document.getElementById('events-list');
    if (!list) return;

    try {
        const res = await fetch(`${API_BASE_URL}/events`);
        const events = await res.json();

        if (events.length === 0) {
            list.innerHTML = '<p class="text-center py-10 text-stone-400">No tin eventonan planea.</p>';
            return;
        }

        list.innerHTML = events.map(event => {
            const isCanceled = event.is_canceled === true;
            const mapsUrl = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(event.location)}`;
            return `
                <div class="bg-white rounded-[1.5rem] md:rounded-[2rem] shadow-sm border border-stone-200 flex flex-col md:flex-row overflow-hidden transition-all ${isCanceled ? 'opacity-60 grayscale' : 'hover:shadow-md'}">
                    <div class="md:w-1/4 ${isCanceled ? 'bg-stone-500' : 'bg-emerald-900'} text-white p-6 md:p-8 flex flex-col items-center justify-center relative">
                        ${isCanceled ? `<div class="absolute top-2 bg-red-600 text-[10px] font-bold px-2 py-0.5 rounded shadow-sm">CANCELÁ</div>` : ''}
                        <div class="text-4xl md:text-5xl font-bold">${event.date.split('-')[2]}</div>
                        <div class="text-[10px] md:text-xs uppercase opacity-70 tracking-widest">${event.date}</div>
                    </div>
                    <div class="p-6 md:p-8 md:w-3/4">
                        <h2 class="text-xl md:text-2xl font-bold ${isCanceled ? 'line-through text-stone-400' : 'text-stone-800'} font-serif mb-2">${event.title}</h2>
                        <div class="flex flex-wrap gap-4 text-stone-500 text-xs md:text-sm mb-4">
                            <a href="${mapsUrl}" target="_blank" class="flex items-center gap-1 hover:text-emerald-700 hover:underline">
                                📍 ${event.location}
                            </a>
                            <span class="flex items-center gap-1">⏰ ${event.time}</span>
                        </div>
                        <p class="text-stone-600 text-sm italic border-l-4 border-emerald-100 pl-4 leading-relaxed">${event.description || ''}</p>
                    </div>
                </div>
            `;
        }).join('');
    } catch (error) {
        list.innerHTML = '<p class="text-center py-10 text-red-500">Error conectando cu servidor.</p>';
    }
}

const contactForm = document.getElementById('contactForm');
if (contactForm) {
    contactForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const btn = document.getElementById('contact-submit-btn');
        const formData = {
            name: document.getElementById('contact-name').value,
            email: document.getElementById('contact-email').value,
            company: document.getElementById('contact-company') ? document.getElementById('contact-company').value : '',
            message: document.getElementById('contact-message').value
        };
        try {
            btn.innerText = "Mandando...";
            btn.disabled = true;
            const response = await fetch(`${API_BASE_URL}/contact`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });
            if (response.ok) {
                document.getElementById('contact-form-container').classList.add('hidden');
                document.getElementById('success-message').classList.remove('hidden');
                lucide.createIcons();
            }
        } catch (error) {
            alert("Error mandando mensahe.");
            btn.disabled = false;
        }
    });
}

window.onload = async () => {
    document.querySelectorAll('.lang-selector').forEach(select => {
        select.addEventListener('change', (e) => {
            updateLanguage(e.target.value);
            if (document.getElementById('events-list')) renderEvents();
        });
    });
    updateLanguage(currentLang);
    lucide.createIcons();
    renderReflection();

    checkThemeColor(); // Added here

    if (document.getElementById('events-list')) await renderEvents();
};