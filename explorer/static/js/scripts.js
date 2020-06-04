$( document ).ready(function() {
  var h = $('.stats-containor').height();
  $('.plot-containor').height(h); 
  var navHeight = $('.navbar').height();
  $('.ddc').css({top:navHeight});
});

function changePage (url) {
  window.location.href = url;
} 
