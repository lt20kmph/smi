function changePage(url) {
  window.location.href = url;
}

$(window).bind("resize", function (e) {
  window.resizeEvt;
  $(window).resize(function () {
    clearTimeout(window.resizeEvt);
    window.resizeEvt = setTimeout(function () {
      var h = $(".stats-containor").height();
      $(".plot-containor").height(h);
      var navHeight = $(".navbar").height();
      $(".ddc").css({ top: navHeight });
      setDims();
    }, 250);
  });
});

$(document).ready(function () {
  var h = $(".stats-containor").height();
  $(".plot-containor").height(h);
  setTimeout(function () {
    var navHeight = $(".navbar").height();
    $(".ddc").css({ top: navHeight });
  }, 250);
});

// $(window).on('resize', setDims());
