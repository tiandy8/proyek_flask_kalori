// static/script.js

document.addEventListener('DOMContentLoaded', () => {
    // --- Header Scroll Effect ---
    const header = document.querySelector('.site-header');
    if (header) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 50) { // Add class after scrolling down 50px
                header.classList.add('scrolled');
            } else {
                header.classList.remove('scrolled');
            }
        });
    }

    // --- Mobile Menu Toggle ---
    const hamburgerButton = document.getElementById('hamburger-button');
    const navLinks = document.querySelector('.nav-links'); // Target the container div

    if (hamburgerButton && navLinks) {
        hamburgerButton.addEventListener('click', () => {
            const isExpanded = hamburgerButton.getAttribute('aria-expanded') === 'true';
            hamburgerButton.setAttribute('aria-expanded', !isExpanded);
            navLinks.classList.toggle('active'); // Toggle class on the links container
            hamburgerButton.classList.toggle('active'); // Toggle class on the button itself for styling (e.g., X shape)
        });
    }

     // --- Smooth Scroll Reveal for Cards ---
    const cards = document.querySelectorAll('.card');

    if (cards.length > 0 && 'IntersectionObserver' in window) {
        const cardObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    observer.unobserve(entry.target); // Stop observing once visible
                }
            });
        }, {
            threshold: 0.1 // Trigger when 10% of the card is visible
        });

        cards.forEach(card => {
            cardObserver.observe(card);
        });
    } else {
        // Fallback for older browsers or if no cards exist
        cards.forEach(card => card.classList.add('visible')); // Make them visible directly
    }


    // --- File Input Feedback Script (from dashboard) ---
    const fileInput = document.getElementById('food_image_input');
    const fileChosenText = document.getElementById('file-chosen-text');
    const scanButton = document.getElementById('scan-button');

    if (fileInput && fileChosenText && scanButton) {
        fileInput.addEventListener('change', function() {
            if (this.files && this.files.length > 0) {
                fileChosenText.textContent = this.files[0].name;
                scanButton.disabled = false; // Enable button
            } else {
                fileChosenText.textContent = 'No file chosen';
                scanButton.disabled = true; // Disable button
            }
        });
         // Ensure button is disabled initially if no file is pre-selected
         if (!fileInput.files || fileInput.files.length === 0) {
              scanButton.disabled = true;
         }
    }

    // --- Active Nav Link Highlighting (Simple Example) ---
    // This is a basic example; more robust solutions might involve server-side logic
    // or matching more specific paths.
    try {
        const currentPath = window.location.pathname;
        const navLinksForActiveState = document.querySelectorAll('.nav-menu .nav-link, .nav-auth .nav-link'); // Select all relevant links

        navLinksForActiveState.forEach(link => {
            // Simple check: if the link's href ends with the current path
            // (This needs refinement for root '/' and more complex routes)
            if (link.pathname === currentPath || (currentPath === '/' && link.pathname === '/')) {
                 // Avoid styling button-like links as 'active' text
                 if (!link.classList.contains('btn')) {
                    link.classList.add('active');
                 }
            }
        });
         // Special case for root path
         if (currentPath === '/') {
             const homeLink = document.querySelector('.nav-logo'); // Or a dedicated home link if you add one
             if(homeLink) {
                 // You might add an active style to the logo or a specific home link
             }
         }

    } catch (e) {
        console.error("Error setting active nav link:", e);
    }


}); // End DOMContentLoaded