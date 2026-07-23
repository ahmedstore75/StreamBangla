const M3U_URL = "https://raw.githubusercontent.com/ahmedstore75/StreamBangla/main/BDIX-Playlist.m3u";

let allChannels = [];
let uniqueCategories = new Set();
let recentChannels = []; 
let favoriteChannels = JSON.parse(localStorage.getItem('tv_fav_channels')) || []; 
let hlsPlayer = null;
let currentActiveChannel = null;
let currentLanguage = 'bn';
let showRecentOnly = false; 
let showFavoritesOnly = false; 

const dict = {
    bn: {
        title: "স্ট্রিমি বাংলা - Premium Live Streaming",
        logo: '<i class="fas fa-play"></i> স্ট্রিমি<span>বাংলা</span>',
        menuTitle: "প্রিমিয়াম মেনু",
        themeDark: "ডার্ক মোড অ্যাক্টিভ",
        themeLight: "লাইট মোড অ্যাক্টিভ",
        subText: "সাবস্ক্রিপশন প্ল্যান",
        recentText: "সাম্প্রতিক চ্যানেল",
        recentActiveText: "সব চ্যানেল দেখুন",
        favText: "প্রিয় চ্যানেল তালিকা",
        favActiveText: "সব চ্যানেল দেখুন",
        optStretch: "ভিডিও সাইজ: Stretch",
        optContain: "ভিডিও সাইজ: Contained",
        refreshText: "প্লে-লিস্ট রিফ্রেশ করুন",
        langBtnText: "English Interface",
        supportText: "হেল্প ও সাপোর্ট",
        welcomeTitle: "সরাসরি সম্প্রচার",
        welcomeDesc: "চ্যানেল তালিকা থেকে পছন্দের চ্যানেল নির্বাচন করুন।",
        searchPlaceholder: "খুঁজুন চ্যানেল বা ক্যাটাগরি...",
        allCat: "সব ক্যাটাগরি",
        noChannel: "কোনো চ্যানেল পাওয়া যায়নি!",
        recentEmpty: "সাম্প্রতিক প্লে করা কোনো চ্যানেল নেই!",
        favEmpty: "প্রিয় তালিকায় কোনো চ্যানেল যোগ করা হয়নি!",
        modalBody: "আপনি বর্তমানে সম্পূর্ণ ফ্রিতে লাইভ স্ট্রিমিং সেবা উপভোগ করছেন। এক্সক্লুসিভ পিওর কোয়ালিটি লাইভ টিভি বা কাস্টম ফিচারের আপদেশের জন্য আমাদের টেলিগ্রাম সাপোর্ট চ্যানেলে নজর রাখুন।",
        noticeLabel: "নোটিশ",
        notice: "স্বাগতম স্ট্রিমি বাংলা লাইভ স্ট্রিমিং অ্যাপে! বাফারিং ছাড়া ঝকঝকে হাই-কোয়ালিটি লাইভ টিভি দেখতে আপনার ইন্টারনেট কানেকশন চেক করুন। কোনো চ্যানেল লোড না হলে মেনু থেকে প্লেলিস্ট রিফ্রেশ করুন। আমাদের সাথে থাকার জন্য ধন্যবাদ!",
        loaderText: "স্ট্রিমিং লোড হচ্ছে...",
        errTitle: "দুঃখিত! চ্যানেলটি লোড করা যাচ্ছে না",
        errDesc: "লিংকটি অফলাইন হতে পারে। প্লে-লিস্ট রিফ্রেশ করে আবার চেষ্টা করুন।"
    },
    en: {
        title: "Stream Bangla - Premium Live Streaming",
        logo: '<i class="fas fa-play"></i> Stream<span>Bangla</span>',
        menuTitle: "Premium Menu",
        themeDark: "Dark Mode Active",
        themeLight: "Light Mode Active",
        subText: "Subscription Plan",
        recentText: "Recent Channels",
        recentActiveText: "Show All Channels",
        favText: "Favorite Channels",
        favActiveText: "Show All Channels",
        optStretch: "Video Size: Stretch",
        optContain: "Video Size: Contained",
        refreshText: "Refresh Playlist",
        langBtnText: "বাংলা ইন্টারফেস",
        supportText: "Help & Support",
        welcomeTitle: "Live Streaming",
        welcomeDesc: "Select your favorite channel from the list to start streaming.",
        searchPlaceholder: "Search channel or category...",
        allCat: "All Categories",
        noChannel: "No channel found!",
        recentEmpty: "No recently played channels!",
        favEmpty: "No channels added to favorites yet!",
        modalBody: "You are currently enjoying live streaming service for free. Keep an eye on our Telegram support group for exclusive high-quality updates or premium custom features.",
        noticeLabel: "Notice",
        notice: "Welcome to Stream Bangla Live Streaming App! Check your internet connection for smooth buffer-free streaming. If channels fail to load, refresh the playlist from the menu. Thanks for staying with us!",
        loaderText: "Streaming loading...",
        errTitle: "Sorry! Channel cannot be loaded",
        errDesc: "The link might be offline. Refresh playlist and try again."
    }
};

const playerEl = document.getElementById('video-player');
const welcomeScreen = document.getElementById('welcome-screen');
const listContainer = document.getElementById('channels-list');
const searchInput = document.getElementById('search-input');
const categoryDropdown = document.getElementById('category-dropdown');
const totalChannelCounter = document.getElementById('total-channel-counter');

const openMenuBtn = document.getElementById('open-menu');
const closeMenuBtn = document.getElementById('close-menu');
const drawer = document.getElementById('premium-drawer');
const overlay = document.getElementById('drawer-overlay');

const subModal = document.getElementById('sub-modal');
const closeModalBtn = document.getElementById('btn-close-modal');
const btnSubscription = document.getElementById('btn-subscription');
const btnRecent = document.getElementById('btn-recent');
const btnFavorites = document.getElementById('btn-favorites');
const btnSupport = document.getElementById('btn-support');

const premiumLoader = document.getElementById('player-premium-loader');
const errorScreen = document.getElementById('player-error-screen');

openMenuBtn.addEventListener('click', () => { drawer.classList.add('open'); overlay.style.display = 'block'; });
const closeMenu = () => { drawer.classList.remove('open'); if(subModal.style.display !== 'block') overlay.style.display = 'none'; };
closeMenuBtn.addEventListener('click', closeMenu);
overlay.addEventListener('click', () => { closeMenu(); subModal.classList.remove('show'); setTimeout(()=>subModal.style.display='none', 300); });

btnSupport.addEventListener('click', () => {
    closeMenu();
    const supportUrl = "https://t.me/banglatvlivefree";
    window.open(supportUrl, '_blank', 'noopener,noreferrer');
});

btnSubscription.addEventListener('click', () => {
    drawer.classList.remove('open');
    subModal.style.display = 'block';
    setTimeout(() => subModal.classList.add('show'), 10);
});
closeModalBtn.addEventListener('click', () => {
    subModal.classList.remove('show');
    setTimeout(() => { subModal.style.display = 'none'; overlay.style.display = 'none'; }, 300);
});

btnRecent.addEventListener('click', () => {
    showFavoritesOnly = false;
    btnFavorites.style.background = "var(--card-bg)";
    btnFavorites.style.borderColor = "var(--border-light)";
    document.getElementById('txt-fav').textContent = dict[currentLanguage].favText;

    showRecentOnly = !showRecentOnly;
    if(showRecentOnly) {
        btnRecent.style.background = "rgba(225, 29, 72, 0.15)";
        btnRecent.style.borderColor = "var(--accent-red)";
        document.getElementById('txt-recent').textContent = dict[currentLanguage].recentActiveText;
    } else {
        btnRecent.style.background = "var(--card-bg)";
        btnRecent.style.borderColor = "var(--border-light)";
        document.getElementById('txt-recent').textContent = dict[currentLanguage].recentText;
    }
    renderChannels();
    closeMenu();
});

btnFavorites.addEventListener('click', () => {
    showRecentOnly = false;
    btnRecent.style.background = "var(--card-bg)";
    btnRecent.style.borderColor = "var(--border-light)";
    document.getElementById('txt-recent').textContent = dict[currentLanguage].recentText;

    showFavoritesOnly = !showFavoritesOnly;
    if(showFavoritesOnly) {
        btnFavorites.style.background = "rgba(225, 29, 72, 0.15)";
        btnFavorites.style.borderColor = "var(--accent-red)";
        document.getElementById('txt-fav').textContent = dict[currentLanguage].favActiveText;
    } else {
        btnFavorites.style.background = "var(--card-bg)";
        btnFavorites.style.borderColor = "var(--border-light)";
        document.getElementById('txt-fav').textContent = dict[currentLanguage].favText;
    }
    renderChannels();
    closeMenu();
});

const themeSwitch = document.getElementById('theme-toggle-switch');
const themeText = document.getElementById('theme-text');
const themeIcon = document.getElementById('theme-icon');

themeSwitch.addEventListener('change', () => {
    if(!themeSwitch.checked) {
        document.body.classList.add('light-mode');
        themeIcon.className = "fas fa-sun";
        themeText.textContent = dict[currentLanguage].themeLight;
    } else {
        document.body.classList.remove('light-mode');
        themeIcon.className = "fas fa-moon";
        themeText.textContent = dict[currentLanguage].themeDark;
    }
});

const langToggle = document.getElementById('lang-toggle');
langToggle.addEventListener('click', () => {
    currentLanguage = (currentLanguage === 'bn') ? 'en' : 'bn';
    applyLanguage();
});

function updateCategoryDropdown() {
    const currentLabels = dict[currentLanguage];
    const savedValue = categoryDropdown.value;
    categoryDropdown.innerHTML = `<option value="all" id="opt-all-cat">${currentLabels.allCat}</option>`;
    Array.from(uniqueCategories).sort().forEach(cat => {
        const option = document.createElement('option');
        option.value = cat; option.textContent = cat; categoryDropdown.appendChild(option);
    });
    if (Array.from(uniqueCategories).includes(savedValue)) {
        categoryDropdown.value = savedValue;
    } else {
        categoryDropdown.value = 'all';
    }
}

function applyLanguage() {
    const currentLabels = dict[currentLanguage];
    
    document.getElementById('page-title').textContent = currentLabels.title;
    document.getElementById('logo-text').innerHTML = currentLabels.logo;
    document.getElementById('menu-title').textContent = currentLabels.menuTitle;
    
    themeText.textContent = (!themeSwitch.checked) ? currentLabels.themeLight : currentLabels.themeDark;
    
    document.getElementById('txt-sub').textContent = currentLabels.subText;
    document.getElementById('txt-recent').textContent = showRecentOnly ? currentLabels.recentActiveText : currentLabels.recentText;
    document.getElementById('txt-fav').textContent = showFavoritesOnly ? currentLabels.favActiveText : currentLabels.favText;
    document.getElementById('opt-stretch').textContent = currentLabels.optStretch;
    document.getElementById('opt-contain').textContent = currentLabels.optContain;
    document.getElementById('refresh-text').textContent = currentLabels.refreshText;
    document.getElementById('lang-text').textContent = currentLabels.langBtnText;
    document.getElementById('support-text').textContent = currentLabels.supportText;
    document.getElementById('welcome-title').textContent = currentLabels.welcomeTitle;
    document.getElementById('welcome-desc').textContent = currentLabels.welcomeDesc;
    document.getElementById('notice-label').textContent = currentLabels.noticeLabel;
    document.getElementById('notice-text').textContent = currentLabels.notice;
    document.getElementById('sub-modal-body').textContent = currentLabels.modalBody;
    
    document.getElementById('loader-text').textContent = currentLabels.loaderText;
    document.getElementById('err-title').textContent = currentLabels.errTitle;
    document.getElementById('err-desc').textContent = currentLabels.errDesc;
    
    searchInput.placeholder = currentLabels.searchPlaceholder;
    
    updateCategoryDropdown();
    renderChannels(); 
}

const aspectSelect = document.getElementById('aspect-ratio-select');
const playerWrapper = document.getElementById('player-section-wrapper');
aspectSelect.addEventListener('change', (e) => {
    if(e.target.value === 'contain') { playerWrapper.classList.add('aspect-contained'); }
    else { playerWrapper.classList.remove('aspect-contained'); }
});

document.getElementById('refresh-player').addEventListener('click', () => {
    renderSkeletons();
    totalChannelCounter.textContent = "Total CH: 0";
    showRecentOnly = false;
    showFavoritesOnly = false;
    btnRecent.style.background = "var(--card-bg)";
    btnFavorites.style.background = "var(--card-bg)";
    fetchPlaylist();
    closeMenu();
});

searchInput.addEventListener('input', renderChannels);
categoryDropdown.addEventListener('change', renderChannels);

function renderSkeletons() {
    listContainer.innerHTML = '';
    for(let i=0; i<9; i++) {
        listContainer.innerHTML += `
            <div class="skeleton-card shimmer-effect">
                <div class="skeleton-logo"></div>
                <div class="skeleton-text-1"></div>
                <div class="skeleton-text-2"></div>
            </div>
        `;
    }
}

async function fetchPlaylist() {
    let loaded = false;
    try {
        const response = await fetch(M3U_URL);
        if (response.ok) { const data = await response.text(); loaded = parseM3U(data); }
    } catch (e) {}

    if (!loaded) {
        try {
            const res = await fetch(`https://api.allorigins.win/get?url=${encodeURIComponent(M3U_URL)}`);
            if (res.ok) { const json = await res.json(); loaded = parseM3U(json.contents); }
        } catch (e) {}
    }

    if (!loaded) {
        listContainer.innerHTML = `
            <div class="status-msg" style="color:var(--accent-red);">
                <i class="fas fa-exclamation-triangle" style="font-size:26px; margin-bottom:10px;"></i>
                <p><b>Data Error!</b></p>
            </div>`;
    }
}

function parseM3U(text) {
    if (!text || !text.includes("#EXTM3U")) return false;
    allChannels = []; uniqueCategories.clear();
    const lines = text.split(/\r?\n/);
    let currentItem = null;

    for (let i = 0; i < lines.length; i++) {
        let line = lines[i].trim();
        if (line.startsWith('#EXTINF:')) {
            currentItem = {};
            const logoMatch = line.match(/tvg-logo="([^"]+)"/i);
            currentItem.logo = logoMatch ? logoMatch[1] : '';
            const groupMatch = line.match(/(?:group-title|group)="([^"]+)"/i);
            currentItem.category = (groupMatch && groupMatch[1].trim() !== "") ? groupMatch[1].trim() : 'LIVE TV';
            uniqueCategories.add(currentItem.category);
            const commaIndex = line.lastIndexOf(',');
            currentItem.title = commaIndex !== -1 ? line.substring(commaIndex + 1).trim() : 'Live Channel';
        } else if (line.startsWith('http') && currentItem) {
            currentItem.url = line; allChannels.push(currentItem); currentItem = null; 
        }
    }

    if(allChannels.length === 0) return false;
    totalChannelCounter.textContent = `Total CH: ${allChannels.length}`;

    updateCategoryDropdown();
    renderChannels();
    return true;
}

function highlightMatch(text, query) {
    if (!query) return text;
    const regex = new RegExp(`(${query.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&')})`, 'gi');
    return text.replace(regex, '<span class="highlight-text">$1</span>');
}

function renderChannels() {
    const query = searchInput.value.toLowerCase().trim();
    const filterCat = categoryDropdown.value;
    listContainer.innerHTML = '';

    let baseSource = allChannels;
    if (showRecentOnly) baseSource = recentChannels;
    if (showFavoritesOnly) baseSource = allChannels.filter(ch => favoriteChannels.includes(ch.url));

    const results = baseSource.filter(ch => {
        const titleMatch = ch.title.toLowerCase().includes(query);
        const categorySearchMatch = ch.category.toLowerCase().includes(query);
        
        const isDropdownMatch = (query !== "" || filterCat === 'all' || ch.category === filterCat);
        
        return (titleMatch || categorySearchMatch) && isDropdownMatch;
    });

    if (results.length === 0) {
        let msg = dict[currentLanguage].noChannel;
        if(showRecentOnly) msg = dict[currentLanguage].recentEmpty;
        if(showFavoritesOnly) msg = dict[currentLanguage].favEmpty;
        listContainer.innerHTML = `<div class="status-msg">${msg}</div>`;
        return;
    }

    results.forEach(ch => {
        const card = document.createElement('div');
        card.className = `channel-card ${currentActiveChannel && currentActiveChannel.url === ch.url ? 'active-card' : ''}`;

        const isFav = favoriteChannels.includes(ch.url);
        const displayTitle = query ? highlightMatch(ch.title, query) : ch.title;

        card.innerHTML = `
            <i class="fa-star fav-badge-icon ${isFav ? 'fas is-fav' : 'far'}" data-url="${ch.url}"></i>
            <div class="card-logo">
                <i class="fas fa-tv"></i>
                ${ch.logo ? `<img src="${ch.logo}" onerror="this.style.display='none'" alt="logo">` : ''}
            </div>
            <div class="card-info">
                <span class="card-title">${displayTitle}</span>
                <span class="card-category">${ch.category}</span>
            </div>
        `;

        card.querySelector('.fav-badge-icon').addEventListener('click', (e) => {
            e.stopPropagation(); 
            const url = e.target.getAttribute('data-url');
            if (favoriteChannels.includes(url)) {
                favoriteChannels = favoriteChannels.filter(u => u !== url);
                e.target.className = "far fa-star fav-badge-icon";
            } else {
                favoriteChannels.push(url);
                e.target.className = "fas fa-star fav-badge-icon is-fav";
            }
            localStorage.setItem('tv_fav_channels', JSON.stringify(favoriteChannels));
            if (showFavoritesOnly) renderChannels();
        });

        card.addEventListener('click', () => {
            document.querySelectorAll('.channel-card').forEach(c => c.classList.remove('active-card'));
            card.classList.add('active-card');
            currentActiveChannel = ch;
            
            recentChannels = recentChannels.filter(r => r.url !== ch.url);
            recentChannels.unshift(ch);
            if(recentChannels.length > 12) recentChannels.pop();

            launchStream(ch);
        });
        listContainer.appendChild(card);
    });
}

function launchStream(channel) {
    welcomeScreen.style.opacity = '0';
    setTimeout(() => { welcomeScreen.style.display = 'none'; }, 400);

    errorScreen.style.display = 'none';
    
    playerEl.removeAttribute('controls');
    premiumLoader.style.display = 'flex';

    if (Hls.isSupported()) {
        if (hlsPlayer) { hlsPlayer.destroy(); }
        hlsPlayer = new Hls({ enableWorker: true, lowLatencyMode: true });
        hlsPlayer.loadSource(channel.url); hlsPlayer.attachMedia(playerEl);
        
        hlsPlayer.on(Hls.Events.MANIFEST_PARSED, () => { 
            playerEl.play().catch(e => console.log(e)); 
        });

        hlsPlayer.on(Hls.Events.ERROR, function (event, data) {
            if (data.fatal) {
                premiumLoader.style.display = 'none';
                errorScreen.style.display = 'flex';
                playerEl.setAttribute('controls', 'true');
                hlsPlayer.destroy();
            }
        });
    } else if (playerEl.canPlayType('application/vnd.apple.mpegurl')) {
        playerEl.src = channel.url;
        playerEl.addEventListener('loadedmetadata', () => { playerEl.play().catch(e => console.log(e)); });
        playerEl.addEventListener('error', () => {
            premiumLoader.style.display = 'none';
            errorScreen.style.display = 'flex';
            playerEl.setAttribute('controls', 'true');
        });
    }
}

playerEl.addEventListener('waiting', () => {
    if(currentActiveChannel) {
        playerEl.removeAttribute('controls');
        premiumLoader.style.display = 'flex';
    }
});
playerEl.addEventListener('playing', () => {
    premiumLoader.style.display = 'none';
    errorScreen.style.display = 'none';
    playerEl.setAttribute('controls', 'true');
});
playerEl.addEventListener('error', () => {
    if(currentActiveChannel) {
        premiumLoader.style.display = 'none';
        errorScreen.style.display = 'flex';
        playerEl.setAttribute('controls', 'true');
    }
});

window.addEventListener('keydown', (e) => {
    if (document.activeElement.tagName === 'INPUT' || document.activeElement.tagName === 'SELECT') return;
    
    switch (e.key.toLowerCase()) {
        case ' ': 
            e.preventDefault();
            if (playerEl.paused) playerEl.play().catch(o=>o); else playerEl.pause();
            break;
        case 'f': 
            e.preventDefault();
            if (!document.fullscreenElement) {
                playerEl.requestFullscreen().catch(err => console.log(err));
            } else {
                document.exitFullscreen();
            }
            break;
        case 'm': 
            e.preventDefault();
            playerEl.muted = !playerEl.muted;
            break;
    }
});

window.addEventListener('DOMContentLoaded', () => {
    renderSkeletons();
    fetchPlaylist();
});
