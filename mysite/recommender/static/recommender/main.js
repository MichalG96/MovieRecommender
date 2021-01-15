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

