/* Theme Name: Lugada - Landing page Template
   Author: Coderthemes
   Author e-mail: coderthemes@gmail.com
   Version: 1.0.0
   Created:Jun 2015
   File Description:Main JS file of the template
*/

/* ==============================================
Smooth Scroll To Anchor
=============================================== */
//jQuery for page scrolling feature - requires jQuery Easing plugin
$(function() {
    $('.navbar-nav a').bind('click', function(event) {
        var $anchor = $(this);
        $('html, body').stop().animate({
            scrollTop: $($anchor.attr('href')).offset().top - 0
        }, 1500, 'easeInOutExpo');
        event.preventDefault();
    });
});
/* ==============================================
Preloader
=============================================== */

$(window).load(function() {
    $('.status').fadeOut();
    $('.preloader').delay(350).fadeOut('slow');
});

/* ==============================================
WOW plugin triggers animate.css on scroll
=============================================== */
jQuery(document).ready(function () {
    wow = new WOW(
        {
            animateClass: 'animated',
            offset: 100,
            mobile: true
        }
    );
    wow.init();
});


/* ==============================================
Magnific Popup
=============================================== */
$(document).ready(function() {
    $('.popup-video').magnificPopup({
      disableOn: 700,
      type: 'iframe',
      mainClass: 'mfp-fade',
      removalDelay: 160,
      preloader: false,

      fixedContentPos: false
    });
});

$(document).ready(function() {
    $('.image-popup').magnificPopup({
        type: 'image',
        closeOnContentClick: true,
        mainClass: 'mfp-fade',
        gallery: {
            enabled: true,
            navigateByImgClick: true,
            preload: [0,1] // Will preload 0 - before current, and 1 after the current image
        }
    });
});

