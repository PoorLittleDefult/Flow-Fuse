var text = ["Distinctive", "Unique", "Interesting", "Eccentric"];
var counter = 0;
var elem = document.getElementById("textchanger");
var currentText = "";
var typingSpeed = 70;

setInterval(change, 2000);

function change() {
    counter = counter % text.length;
    currentText = text[counter];
    elem.innerHTML = "";
    typeText();
    counter++;
}

function typeText() {
    if (currentText.length > 0) {
        elem.innerHTML += currentText.charAt(0);
        currentText = currentText.slice(1);
        setTimeout(typeText, typingSpeed);
    }
}
