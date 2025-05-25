var formChanged = false;

function inputChanged(el) {
    formChanged = true;
    var button = el.parentElement.querySelector('#submitscan');
    var list = button.classList;
    button.classList.add("scan_not_submitted");
}

function scanSubmitted(el) {
    formChanged = false;
    el.classList.remove("scan_not_submitted");
}

window.addEventListener('beforeunload', (event) => {
    if (formChanged && event.srcElement.activeElement.type != 'submit') {
        alert("You have unsaved changes.")
        event.preventDefault();
        return '';
    }
});