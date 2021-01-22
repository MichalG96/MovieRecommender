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
function myFunction() {
    changeArrowDirection();
    document.getElementById("myDropdown").classList.toggle("show");
}

// Close the dropdown if the user clicks outside of it
window.onclick = function (event) {
    if (!event.target.matches('.dropbtn')) {
        var dropdowns = document.getElementsByClassName("dropdown-content");
        var i;
        for (i = 0; i < dropdowns.length; i++) {
            var openDropdown = dropdowns[i];
            if (openDropdown.classList.contains('show')) {
                changeArrowDirection();
                openDropdown.classList.remove('show');
            }
        }
    }
}
