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
  } else {
    goTo = +currentSlideNo + 1;
  }
  location.hash = "#slide-" + goTo;
}


// Handling CSRF
$(function () {
  // This function gets cookie with a given name
  function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
      var cookies = document.cookie.split(';');
      for (var i = 0; i < cookies.length; i++) {
        var cookie = jQuery.trim(cookies[i]);
        // Does this cookie string begin with the name we want?
        if (cookie.substring(0, name.length + 1) == (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  var csrftoken = getCookie('csrftoken');

  /*
  The functions below will create a header with csrftoken
  */

  function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
  }

  function sameOrigin(url) {
    // test that a given url is a same-origin URL
    // url could be relative or scheme relative or absolute
    var host = document.location.host; // host + port
    var protocol = document.location.protocol;
    var sr_origin = '//' + host;
    var origin = protocol + sr_origin;
    // Allow absolute or scheme relative URLs to same origin
    return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
      (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
      // or any other URL that isn't scheme relative or absolute i.e relative.
      !(/^(\/\/|http:|https:).*/.test(url));
  }

  $.ajaxSetup({
    beforeSend: function (xhr, settings) {
      if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
        // Send the token to same-origin, relative URLs only.
        // Send the token only if the method warrants CSRF protection
        // Using the CSRFToken value acquired earlier
        xhr.setRequestHeader("X-CSRFToken", csrftoken);
      }
    }
  });

});


function testFunc() {
  console.log("create post is working!") // sanity check
  $.ajax({
    // url: '{% url "preferences" %}', // the endpoint
    url: 'add_rating/', // the endpoint
    type: "POST", // http method
    // data: {the_post: $('#post-text').val()}, // data sent with the post request
    success: function (json) {
      console.log(json); // log the returned json to the console
    },
    error: function (xhr, errmsg, err) {
      $('#results').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: " + errmsg +
        " <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
      console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
    }
  });
}


