document.querySelectorAll(".form-container label").forEach((el) => {
    el.className = "plus";
});

document.querySelectorAll(".form-container label input").forEach((checkbox) => {
    if (checkbox.checked) {
        checkbox.parentElement.className = "tick";
        checkbox.parentElement.style.cssText = "color: gold;border: 0.1rem solid gold;";
    }
});

document.querySelectorAll(".form-container label input").forEach((checkbox) => {
    checkbox.addEventListener("change", (event) => {
        if (event.target.checked) {
            checkbox.parentElement.className = "tick";
            checkbox.parentElement.style.cssText = "color: gold;border: 0.1rem solid gold;";
        } else {
            checkbox.parentElement.className = "plus";
            checkbox.parentElement.style.cssText = "color: #0072dc;border: 0.1rem solid #0072dc;";

        }
    });
});


function changeArrowDirection() {
    arrowDirection = document.getElementById('arrow').className;
    if (arrowDirection === 'fa fa-angle-down') {
        document.getElementById('arrow').className = ('fa fa-angle-up');
    } else if (arrowDirection === 'fa fa-angle-up') {
        document.getElementById('arrow').className = ('fa fa-angle-down');
    }
}

/* When the user clicks on the button,
toggle between hiding and showing the dropdown content */
function showHideDropdown() {
    changeArrowDirection();
    document.getElementById("myDropdown").classList.toggle("show");
}

// Close the dropdown if the user clicks outside of it
window.onclick = function (event) {
    if (!event.target.matches('.dropbtn')) {
        var dropdown = document.getElementsByClassName("dropdown-content")[0];
        if (dropdown.classList.contains('show')) {
            changeArrowDirection();
            dropdown.classList.remove('show');
            // dropdown.style.transform = "translate-y(0)";
        }
    }
}

const navSlide = () => {
    const burger = document.querySelector('.burger');
    const nav_links = document.querySelector('.nav-links');
    const nav = document.querySelector('nav');
    const navLinks = document.querySelectorAll('.nav-links li');

    burger.addEventListener('click', () => {
        nav_links.classList.toggle('nav-active');
        navLinks.forEach((link, index) => {
            if (link.style.animation) {
                link.style.animation = '';
            } else {
                // link.style.animation = `navLinkFade 0.3s forwards ${index / 10 + 0.25}s`;
                link.style.animation = `navLinkFade 0.8s forwards 0.3s`;
            }
        });

        burger.classList.toggle('toggle');

    });
}

navSlide();


function goToPreviousSlide() {
    let totalSlides = 5;
    let currentSlideNo = location.hash.slice(-1);
    let goTo = 1;
    if (currentSlideNo == 1 || currentSlideNo == '') {
        goTo = totalSlides;
    } else {
        goTo = +currentSlideNo - 1;
    }
    location.hash = "#slide-" + goTo;
}

function goToNextSlide() {
    let totalSlides = 5;
    let currentSlideNo = location.hash.slice(-1);
    let goTo = 1;
    if (currentSlideNo == 5) {
        goTo = 1;
    } else if (currentSlideNo == '') {
        goTo = 2;
    }
     else {
        goTo = +currentSlideNo + 1;
    }
    location.hash = "#slide-" + goTo;
}
