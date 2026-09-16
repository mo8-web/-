// رقم الشريحة الحالية
let currentSlide = 0;

// البحث عن جميع الشرائح
const slides = document.querySelectorAll(".hero-slide");


// عرض شريحة محددة
function showSlide(index) {

    // إذا لم توجد شرائح ننهي الدالة
    if (!slides.length) {
        return;
    }

    // إذا تجاوزنا آخر شريحة نعود للأولى
    if (index >= slides.length) {
        currentSlide = 0;
    }

    // إذا رجعنا قبل أول شريحة نذهب للأخيرة
    if (index < 0) {
        currentSlide = slides.length - 1;
    }

    // إخفاء جميع الشرائح
    slides.forEach((slide) => {
        slide.classList.remove("active");
    });

    // إظهار الشريحة الحالية
    slides[currentSlide].classList.add("active");
}


// تغيير الشريحة بالأسهم
function changeSlide(direction) {
    currentSlide += direction;
    showSlide(currentSlide);
}


// تشغيل السلايدر تلقائياً كل 5 ثوانٍ
setInterval(() => {
    currentSlide++;
    showSlide(currentSlide);
}, 5000);
