document.addEventListener("DOMContentLoaded", () => {
    let currentIndex = 0;
    const slides = document.querySelectorAll(".banner-slide");
    const indicators = document.querySelectorAll(".indicator");
    const prevBtn = document.querySelector(".prev-btn");
    const nextBtn = document.querySelector(".next-btn");

    function updateCarousel(index) {
        slides.forEach((slide, i) => {
            slide.classList.toggle("active", i === index);
            indicators[i].classList.toggle("active", i === index);
        });
    }

    function nextSlide() {
        currentIndex = (currentIndex + 1) % slides.length;
        updateCarousel(currentIndex);
    }

    function prevSlide() {
        currentIndex = (currentIndex - 1 + slides.length) % slides.length;
        updateCarousel(currentIndex);
    }

    indicators.forEach((indicator, index) => {
        indicator.addEventListener("click", () => {
            currentIndex = index;
            updateCarousel(currentIndex);
        });
    });

    prevBtn.addEventListener("click", prevSlide);
    nextBtn.addEventListener("click", nextSlide);

    setInterval(nextSlide, 3000); // Auto-slide every 5 seconds
});
