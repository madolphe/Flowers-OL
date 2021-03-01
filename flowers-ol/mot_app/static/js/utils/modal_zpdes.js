// Get the modal
var modal = document.getElementById("myModal");
// Get the button that opens the modal
var btn = document.getElementById("setting-button");
// Get the <span> element that closes the modal
var span = document.getElementsByClassName("close_button")[0];
// When the user clicks on the button, open the modal
var is_closed = true;
// Get the button that send request to backend for participant new screen_params:
var btn_screen = document.getElementById("btn_screen");
var screen = 0;

btn_screen.onclick = function(){
  screen = btn_screen.value;
};
btn.onclick = function() {
  modal.style.display = "block";
  is_closed = false;
};
// When the user clicks on <span> (x), close the modal
span.onclick = function() {
  modal.style.display = "none";
  is_closed = true;
};