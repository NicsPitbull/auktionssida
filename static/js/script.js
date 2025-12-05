/* ===========================================
   AUKTIONSSIDA - Huvudskript
   =========================================== */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Auktionssida laddad!');
    
    // Initiera funktioner
    initCountdownTimers();
    initLikeButtons();
    initBidForm();
    initFlashMessages();
});

/* ===========================================
   COUNTDOWN TIMER
   =========================================== */
function initCountdownTimers() {
    const timers = document.querySelectorAll('.countdown-timer');
    
    timers.forEach(timer => {
        const endTime = new Date(timer.dataset.endTime).getTime();
        
        const updateTimer = () => {
            const now = new Date().getTime();
            const distance = endTime - now;
            
            if (distance < 0) {
                timer.innerHTML = '<span class="ended">Auktionen har avslutats</span>';
                return;
            }
            
            const days = Math.floor(distance / (1000 * 60 * 60 * 24));
            const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((distance % (1000 * 60)) / 1000);
            
            timer.innerHTML = `
                <span class="time-unit">${days}d</span>
                <span class="time-unit">${hours}h</span>
                <span class="time-unit">${minutes}m</span>
                <span class="time-unit">${seconds}s</span>
            `;
        };
        
        updateTimer();
        setInterval(updateTimer, 1000);
    });
}

/* ===========================================
   LIKE/DISLIKE FUNKTIONALITET
   =========================================== */
function initLikeButtons() {
    const likeButtons = document.querySelectorAll('.like-btn');
    const dislikeButtons = document.querySelectorAll('.dislike-btn');
    
    likeButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const auctionId = this.dataset.auctionId;
            toggleLike(auctionId, true, this);
        });
    });
    
    dislikeButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const auctionId = this.dataset.auctionId;
            toggleLike(auctionId, false, this);
        });
    });
}

async function toggleLike(auctionId, isLike, button) {
    try {
        const endpoint = isLike ? 'toggle_like' : 'toggle_dislike';
        const response = await fetch(`/auctions/${endpoint}/${auctionId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            // Uppdatera räknaren
            const countSpan = button.querySelector('.count');
            if (countSpan) {
                countSpan.textContent = data.count;
            }
            button.classList.toggle('active');
        } else {
            console.error('Kunde inte uppdatera like/dislike');
        }
    } catch (error) {
        console.error('Fel vid like/dislike:', error);
    }
}

/* ===========================================
   BUD FORMULÄR
   =========================================== */
function initBidForm() {
    const bidForm = document.querySelector('#bid-form');
    
    if (bidForm) {
        bidForm.addEventListener('submit', function(e) {
            const bidInput = this.querySelector('input[name="amount"]');
            const currentBid = parseFloat(this.dataset.currentBid || 0);
            const minBid = parseFloat(this.dataset.minBid || 0);
            const bidAmount = parseFloat(bidInput.value);
            
            if (bidAmount <= currentBid) {
                e.preventDefault();
                showNotification('Ditt bud måste vara högre än nuvarande bud!', 'error');
                return false;
            }
            
            if (bidAmount < minBid) {
                e.preventDefault();
                showNotification(`Minsta bud är ${minBid} kr`, 'error');
                return false;
            }
        });
    }
}

/* ===========================================
   FLASH MESSAGES
   =========================================== */
function initFlashMessages() {
    const flashMessages = document.querySelectorAll('.flash-message');
    
    flashMessages.forEach(msg => {
        // Auto-hide efter 5 sekunder
        setTimeout(() => {
            msg.style.opacity = '0';
            msg.style.transition = 'opacity 0.5s';
            setTimeout(() => msg.remove(), 500);
        }, 5000);
        
        // Klicka för att stänga
        msg.addEventListener('click', function() {
            this.remove();
        });
    });
}

/* ===========================================
   NOTIFIKATIONER
   =========================================== */
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `flash-message flash-${type}`;
    notification.textContent = message;
    
    const container = document.querySelector('.container') || document.body;
    container.insertBefore(notification, container.firstChild);
    
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transition = 'opacity 0.5s';
        setTimeout(() => notification.remove(), 500);
    }, 5000);
}

/* ===========================================
   SÖKFUNKTION
   =========================================== */
function initSearch() {
    const searchInput = document.querySelector('#search-input');
    const searchForm = document.querySelector('#search-form');
    
    if (searchInput && searchForm) {
        // Debounce för live-sökning
        let timeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(timeout);
            timeout = setTimeout(() => {
                // Kan implementera live-sökning här
            }, 300);
        });
    }
}

/* ===========================================
   UTILITY FUNKTIONER
   =========================================== */
function formatCurrency(amount) {
    return new Intl.NumberFormat('sv-SE', {
        style: 'currency',
        currency: 'SEK'
    }).format(amount);
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('sv-SE', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}
