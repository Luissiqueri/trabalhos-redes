const input = document.querySelector("#input-file");
input.style.opacity = 0;

function clickButton() {
    fetch('')
        .then(response => response.json())
        .then(data => {
            console.log(data)
        }).catch(error => {
            console.log(error);
        });
}