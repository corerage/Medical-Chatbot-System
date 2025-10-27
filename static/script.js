// Get elements
const aboutSection = document.getElementById('about');
const aboutLink = document.querySelector('a[href="#about"]');
const howLink = document.querySelector('a[href="#how"]');

// Reveal About on "About" link click
aboutLink.addEventListener('click', (e) => {
    e.preventDefault();
    aboutSection.classList.remove('hidden');
    aboutSection.classList.add('visible');
    
    // Smooth scroll to About section
    aboutSection.scrollIntoView({ behavior: 'smooth' });
});

// Reveal About on "How It Works" link click
howLink.addEventListener('click', (e) => {
    e.preventDefault();
    aboutSection.classList.remove('hidden');
    aboutSection.classList.add('visible');
    
    // Smooth scroll to How It Works section
    document.getElementById('how').scrollIntoView({ behavior: 'smooth' });
});

// Reveal About on scroll using Intersection Observer
const observerOptions = {
    threshold: 0.2
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            aboutSection.classList.remove('hidden');
            aboutSection.classList.add('visible');
        }
    });
}, observerOptions);

// Start observing the How It Works section
observer.observe(document.getElementById('how'));