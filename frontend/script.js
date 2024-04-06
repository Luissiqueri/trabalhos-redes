const input = () => document.querySelector("#input-file");
input.style.opacity = 0;

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