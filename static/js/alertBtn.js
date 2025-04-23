export function showMessage(message) {
    const alertBox = document.querySelector('.alert');
    const messageElement = alertBox.querySelector('.msg');

    messageElement.textContent = `Error: ${message}`;

    alertBox.style.display = 'block';

    alertBox.classList.remove('hide'); // показать уведомление
    alertBox.classList.add('show');

    setTimeout(() => {
        alertBox.classList.add('hide');
        alertBox.classList.remove('show');

        setTimeout(() => {
            alertBox.style.display = 'none';
        }, 1000);
    }, 5000);
}

document.querySelector('#closeAlert').addEventListener('click', () => {     // нажать на крестик
    const alertBox = document.querySelector('.alert');
    alertBox.classList.add('hide');
    alertBox.classList.remove('show');

    setTimeout(() => {
        alertBox.style.display = 'none';
    }, 1000);
});

