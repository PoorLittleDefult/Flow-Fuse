var menus = document.querySelectorAll(".menu");
menus.forEach(function(menu) {
  menu.addEventListener("click", function() {
    this.classList.toggle("open");
  });
});
