const input = () => document.querySelector("#input-file");
const label = document.querySelector('.label-input-file');
const abovePanel = document.querySelector('.above-panel');

input().style.opacity = 0;
input().addEventListener("change", function () {
    if (input().files.length > 0)
        var fileName = input().files[0].name;
    label.innerHTML = fileName;
});

function clickButton() {
    const formData = new FormData();
    formData.append("file", input().files[0])
    fetch('http://localhost:8000/uploadfile', {
        method: 'POST',
        body: formData
    }).then(response => response.json())
        .then(data => {
            console.log(data)
            const imgFluxGraph = document.createElement("IMG");
            imgFluxGraph.src = "http://localhost:8000/graficos/fluxGraph.svg";
            imgFluxGraph.style.height = "100px";
            document.querySelector(".body").appendChild(imgFluxGraph);

            const imgLocationsGraph = document.createElement("IMG");
            imgLocationsGraph.src = "http://localhost:8000/graficos/locationsGraph.svg";
            imgLocationsGraph.style.height = "100px";
            document.querySelector(".body").appendChild(imgLocationsGraph);

        }).catch(error => {
            console.log(error);
        });
}