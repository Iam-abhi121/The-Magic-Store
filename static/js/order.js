document.querySelectorAll('.size').forEach((item) => {
    item.addEventListener('click', () => {
        document.querySelectorAll('.size').forEach((el) => el.classList.remove('selected'));
        
        item.classList.add('selected');
        
        const radioInput = item.querySelector('input[type="radio"]');
        if (radioInput) {
            radioInput.checked = true;
        }
    });
});


let slides = document.querySelector(".upper-div");
let slideIndex = 0;

function showSlide(index) {
    if (window.innerWidth <= 1024) {
        slides.style.transform = `translateX(-${index * 100}%)`;
    }
}

function nextSlide() {
    slideIndex++;
    if (slideIndex >= slides.children.length) {
        slideIndex = 0; 
    }
    showSlide(slideIndex);
}

function startSlider() {
    if (window.innerWidth <= 1024) {
        setInterval(nextSlide, 3000);
    }
}

startSlider();
