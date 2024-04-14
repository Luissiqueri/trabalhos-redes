const input = document.querySelector("#input-file");
const inputProtocol = document.querySelector("#SelectProtocol");
const label = document.querySelector('.label-input-file');
const abovePanel = document.querySelector('.above-panel');
const closeIcon = document.querySelector('.close-icon');
const buttonSendFile = document.querySelector('.button-send-file');
let lengthGraphs = 0;

function setView(value) {
    const viewed = document.querySelector(`.view`);
    viewed.classList.remove("view");
    const containerGraph = document.querySelector(`.img-${value}`);
    containerGraph.classList.add("view");
}

input.style.opacity = 0;

input.addEventListener("change", function () {
    if (input.files.length > 0) {
        buttonSendFile.disabled = false;
        closeIcon.style.display = "block";
        var fileName = input.files[0].name;
    }
    label.innerHTML = fileName;
});


function removeFile() {
    label.innerHTML = "Selecione seu arquivo";
    closeIcon.style.display = "none";
    buttonSendFile.disabled = true;

}

function clickButton() {
    const formData = new FormData();
    formData.append("file", input.files[0]);
    const protocol = inputProtocol.value;
    fetch(`http://localhost:8000/uploadfile/${protocol}`, {
        method: 'POST',
        body: formData
    })
    .then(async response => showResults(await response.json(), protocol))
    .catch(error => {
        console.log(error);
    });
}

function showResults(jsonResposnse, protocol) {
    if (protocol == "IP") {
        showIPData();
    } else if (protocol == "ARP") {
        showARPData(jsonResposnse);
    }
}

function showIPData() {
    const imgFluxGraph = document.createElement("IMG");
    imgFluxGraph.src = "http://localhost:8000/graficos/fluxGraph.svg";
    document.querySelector(".img-1").appendChild(imgFluxGraph);
    lengthGraphs++;

    let title = document.createElement("p");
    title.innerHTML = "Gráfico mostrando visualmente o fluxo de dados.";
    title.className = "title";
    document.querySelector(".img-1").appendChild(title);

    let subtitle = document.createElement("p");
    subtitle.innerHTML = "*A Largura da aresta indica a quantidade de vezes que ocorreu.";
    subtitle.className = "subtitle";
    document.querySelector(".img-1").appendChild(subtitle);

    const imgLocationsGraph = document.createElement("IMG");
    imgLocationsGraph.src = "http://localhost:8000/graficos/locationsGraph.svg";
    document.querySelector(".img-2").appendChild(imgLocationsGraph);
    lengthGraphs++;

    title = document.createElement("p");
    title.innerHTML = "Gráfico sinalizando visualmente a posição geográfica de cada IP.";
    title.className = "title";
    document.querySelector(".img-2").appendChild(title);

    subtitle = document.createElement("p");
    subtitle.innerHTML = "*O raio do círculo maior indica a quantidade de IP's presentes naquela região.";
    subtitle.className = "subtitle";
    document.querySelector(".img-2").appendChild(subtitle);


    abovePanel.style.display = "flex";
    for (let i = 0; i < lengthGraphs; i++) {
        const paragraph = document.createElement("p");
        paragraph.innerHTML = `Gráfico ${i + 1}`;
        paragraph.onclick = function() { setView(`${i + 1}`) };
        document.querySelector(".above-panel").appendChild(paragraph);
    }
}

function showARPData(jsonResposnse) {
    //jsonResponse = json contendo a tabela montada a partir dos pacotes
    //insira aqui o codigo necessario para exibir as informacoes recebidas
}
