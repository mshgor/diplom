function toggleGcodeForm() {
    const formElement = document.getElementById('form2GCode');
    if (formElement.style.display === "none" || !formElement.style.display) {
        formElement.style.display = "block"
    } else {
        formElement.style.display = "none"
    }
}
