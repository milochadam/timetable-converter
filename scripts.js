function enable_all() {
    elements = document.getElementsByClassName('toggle_button');
    for (var i = 0; i < elements.length; i++) {
        var element = elements[i];
        element.classList.add('active');
        element.addEventListener('click', toggle_hide, false);
    }
}

function toggle_hide() {
    button = event.target
    elements = document.getElementsByClassName(button.id);

    if (button.classList.contains('active')) {
        button.classList.remove('active');
        button.classList.add('unactive');
    } else {
        button.classList.remove('unactive');
        button.classList.add('active');
    }

    state = ['', 'hidden'];
    for (var i = 0; i < elements.length; i++) {
        var element = elements[i]
        if (element.style.visibility == state[0]) {
            element.style.visibility = state[1];
        } else {
            element.style.visibility = state[0]
        }
    }
}
