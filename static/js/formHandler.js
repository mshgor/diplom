import { initScene, threeScene } from './app.js';
import { showMessage } from './alertBtn.js'

async function sendGcode() {

    const expression = document.getElementById("expression").value;
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    const dataToSend = { 'gcode': expression }; 

    const options = {
        method: "POST",
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify(dataToSend)            
    };

    try {
        const response = await fetch("/", options);

        if (!response.ok) {

            if (response.status == 500) {
                const err_Data = await response.json();
                const errorMessage = err_Data.error;
                console.log(errorMessage);
                showMessage(errorMessage);
                
            };
            throw new Error(`Error: ${response.status}`); 
        }

        const result = await response.json();
        console.log("Response from server: ", result);
        threeScene(result);

    } catch (error) {
        console.error(error);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    initScene(); // Базовая сцена
});

document.getElementById("calcForm").addEventListener('submit', function (event) {
    event.preventDefault();
    sendGcode();
});