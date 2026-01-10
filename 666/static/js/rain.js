document.addEventListener("DOMContentLoaded", function() {
    const rainContainer = document.querySelector('.rain-container');
    if (!rainContainer) return;

    const dropCount = 100; // Adjust for density

    for (let i = 0; i < dropCount; i++) {
        const drop = document.createElement('div');
        drop.classList.add('raindrop');
        
        // Random horizontal position
        drop.style.left = Math.random() * 100 + 'vw';
        
        // Random animation duration for variety
        const duration = Math.random() * 0.5 + 0.5; // 0.5s to 1s
        drop.style.animationDuration = duration + 's';
        
        // Random delay so they don't all start at once
        drop.style.animationDelay = Math.random() * 2 + 's';
        
        // Random opacity for depth effect
        drop.style.opacity = Math.random() * 0.5;

        rainContainer.appendChild(drop);
    }
});
