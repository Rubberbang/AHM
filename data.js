const CHOIR_EVENTS = [
    { id: '1', title: 'Misa Birgen di Fatima - Dakota', location: 'Misa di Dakota, Oranjestad', date: '2025-12-22', time: '05:00 AM', description: 'Misa di Aurora dia 6.', type: 'Mass' },
    { id: '2', title: 'Parokia Sagrado Curason di Hesus Aruba - Savaneta', location: 'Sagrado Curason, Savaneta', date: '2025-12-23', time: '04:00 AM', description: 'Misa di Aurora dia 7.', type: 'Mass' },
    { id: '3', title: 'Misa Birgen di Fatima - Dakota', location: 'Misa di Dakota, Oranjestad', date: '2025-12-24', time: '04:00 AM', description: 'Misa di Aurora dia 8.', type: 'Mass' }
];

const TRANSLATIONS = {
    pap: {
        home: 'Home', calendar: 'Kalender', contact: 'Contacto',
        hero_title: 'Amigonan di Hesus y Maria', hero_subtitle: 'Canta pa Señor cu alegria y hiba fe na tur skina di Aruba.',
        upcoming_performances: 'Siguiente Presentacion', spiritual_reflection: 'Refleho Spiritual',
        calendar_title: 'Kalender di Presentacion', contact_title: 'Tuma Contacto',
        send_message: 'Manda Mensahe', message_sent: 'Mensahe Manda!', footer_desc: 'Celebrando fe pa medio di koor Arubiano.',
        inspiration_text: "Nan alabá su nòmber ku balia, nan kanta salmo p'E ku arpa i tamburein.",
        inspiration_ref: "Salmo 149:3 (BPK13)",
        mission_title: 'Nos Mishon',
        mission_devotion: 'Devoshon Spiritual',
        mission_devotion_desc: 'Dedica na e liturgia y e experiencia spiritual via canto sagrado.',
        mission_community: 'Comunidad',
        mission_community_desc: 'Un famia di amigonan uni den fe, apoyando otro den Hesus y Maria.',
        mission_heritage: 'Herencia Arubiano',
        mission_heritage_desc: 'Ancra den e rikesa cultural y tradishonnan spiritual di nos isla.',
        our_story_title: 'Nos Historia',
        history_p1: 'Fundá pa miembronan dedica di e comunidad Catolico Arubiano, AHM a crece bira un grupo vibrante di cantante y musiconan.',
        history_p2: 'Unda cu nos presenta, sea na Paradera, Noord of otro misa, nos meta ta hiba e mensahe di fe via nos harmonianan.'
    },
    en: {
        home: 'Home', calendar: 'Calendar', contact: 'Contact',
        hero_title: 'Friends of Jesus and Mary', hero_subtitle: 'Sing to the Lord with joy and spread faith across Aruba.',
        upcoming_performances: 'Upcoming Performances', spiritual_reflection: 'Spiritual Reflection',
        calendar_title: 'Performance Calendar', contact_title: 'Get in Touch',
        send_message: 'Send Message', message_sent: 'Message Sent!', footer_desc: 'Celebrating faith through Aruban tradition.',
        inspiration_text: "Let them praise his name with dancing and make music to him with timbrel and harp.",
        inspiration_ref: "Psalm 149:3",
        mission_title: 'Our Mission',
        mission_devotion: 'Spiritual Devotion',
        mission_devotion_desc: 'Dedicated to the liturgy and spiritual experience through sacred song.',
        mission_community: 'Community',
        mission_community_desc: 'A family of friends united in faith, supporting one another in Jesus and Mary.',
        mission_heritage: 'Aruban Heritage',
        mission_heritage_desc: 'Rooted in the cultural richness and spiritual traditions of our island.',
        our_story_title: 'Our Story',
        history_p1: 'Founded by dedicated members of the Aruban Catholic community, AHM has grown into a vibrant group of singers and musicians.',
        history_p2: 'Wherever we perform, whether in Paradera, Noord, or other parishes, our goal is to carry the message of faith through our harmonies.'
    },
    es: {
        home: 'Inicio', calendar: 'Calendario', contact: 'Contacto',
        hero_title: 'Amigos de Jesús y María', hero_subtitle: 'Cantad al Señor con alegría y llevad la fe a cada rincón de Aruba.',
        upcoming_performances: 'Próximas Presentaciones', spiritual_reflection: 'Reflexión Espiritual',
        calendar_title: 'Calendario de Actuaciones', contact_title: 'Ponte en Contacto',
        send_message: 'Enviar Mensaje', message_sent: '¡Mensaje Enviado!', footer_desc: 'Celebrando la fe a través de la tradición coral arubana.',
        inspiration_text: "Alaben su nombre con danza; Con pandero y arpa a él canten.",
        inspiration_ref: "Salmo 149:3",
        mission_title: 'Nuestra Misión',
        mission_devotion: 'Devoción Espiritual',
        mission_devotion_desc: 'Dedicados a la liturgia y a la experiencia espiritual a través del canto sagrado.',
        mission_community: 'Comunidad',
        mission_community_desc: 'Una familia de amigos unidos en la fe, apoyándonos unos a otros en Jesús y María.',
        mission_heritage: 'Herencia Arubana',
        mission_heritage_desc: 'Arraigados en la riqueza cultural y las tradiciones espirituales de nuestra isla.',
        our_story_title: 'Nuestra Historia',
        history_p1: 'Fundado por miembros dedicados de la comunidad católica de Aruba, AHM ha crecido hasta convertirse en un vibrante grupo de cantantes y músicos.',
        history_p2: 'Dondequiera que actuamos, ya sea en Paradera, Noord u otras parroquias, nuestro objetivo es llevar el mensaje de la fe a través de nuestras armonías.'

    }
};