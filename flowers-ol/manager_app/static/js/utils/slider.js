let elements = document.getElementsByClassName("slider");
let onClick = function() {
    document.getElementsByName(this.getAttribute("name").concat("_validator"))[0].checked = true
};
Array.from(elements).forEach((element) => {element.addEventListener('click', onClick)});
