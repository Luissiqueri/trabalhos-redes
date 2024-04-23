const input = document.querySelector("#input--file");
const inputProtocol = document.querySelector("#protocol--select");
const label = document.querySelector(".input--file--label");
const closeIcon = document.querySelector(".icon--close");
const buttonSendFile = document.querySelector(".send--file--button");
const loadIcon = document.querySelector(".icon--load");
const inputView = document.querySelector(".input--file--container");
const selectView = document.querySelector(".protocol--container");
const image1 = document.querySelector(".img-1");
const image2 = document.querySelector(".img-2");
let lengthGraphs = 0;

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
  input.value = null;
  while (image1.hasChildNodes()) {
    image1.removeChild(image1.firstChild);
  }
  while (image2.hasChildNodes()) {
    image2.removeChild(image2.firstChild);
  }

  const header = document.querySelector(".table--header");
  while (header.hasChildNodes()) {
    header.removeChild(header.firstChild);
  }

  const body = document.querySelector(".table--body");
  while (body.hasChildNodes()) {
    body.removeChild(body.firstChild);
  }
  document.querySelector(".Table").classList.add("hidden");
}

function clickButton() {
  loadIcon.classList.remove("hidden");
  while (image1.hasChildNodes()) {
    image1.removeChild(image1.firstChild);
  }
  while (image2.hasChildNodes()) {
    image2.removeChild(image2.firstChild);
  }

  const header = document.querySelector(".table--header");
  while (header.hasChildNodes()) {
    header.removeChild(header.firstChild);
  }
  const body = document.querySelector(".table--body");
  while (body.hasChildNodes()) {
    body.removeChild(body.firstChild);
  }

  const formData = new FormData();
  formData.append("file", input.files[0]);
  const protocol = inputProtocol.value;
  fetch(`http://localhost:8000/uploadfile/${protocol}`, {
    method: "POST",
    body: formData,
  })
    .then(async (response) => showResults(await response.json(), protocol))
    .catch((error) => {
      console.log(error);
    });
}

function showResults(jsonResposnse, protocol) {
  loadIcon.classList.add("hidden");

  if (protocol == "IP") {
    showIPData();
  } else if (protocol == "ARP") {
    showARPData(jsonResposnse);
  }
}

function showIPData() {
  document.querySelector(".images--api").classList.remove("hidden");

  const imgFluxGraph = document.createElement("IMG");
  imgFluxGraph.src = "http://localhost:8000/graficos/fluxGraph.svg";
  document.querySelector(".img-1").appendChild(imgFluxGraph);
  lengthGraphs++;

  let title = document.createElement("p");
  title.innerHTML = "Gráfico mostrando visualmente o fluxo de dados.";
  title.className = "title";
  document.querySelector(".img-1").appendChild(title);

  let subtitle = document.createElement("p");
  subtitle.innerHTML =
    "*A Largura da aresta indica a quantidade de vezes que ocorreu.";
  subtitle.className = "subtitle";
  document.querySelector(".img-1").appendChild(subtitle);

  const imgLocationsGraph = document.createElement("IMG");
  imgLocationsGraph.src = "http://localhost:8000/graficos/locationsGraph.svg";
  document.querySelector(".img-2").appendChild(imgLocationsGraph);
  lengthGraphs++;

  title = document.createElement("p");
  title.innerHTML =
    "Gráfico sinalizando visualmente a posição geográfica de cada IP.";
  title.className = "title";
  document.querySelector(".img-2").appendChild(title);

  subtitle = document.createElement("p");
  subtitle.innerHTML =
    "*O raio do círculo maior indica a quantidade de IP's presentes naquela região.";
  subtitle.className = "subtitle";
  document.querySelector(".img-2").appendChild(subtitle);
}

function showARPData(json) {
  document.querySelector(".Table").classList.remove("hidden");
  const header = document.querySelector(".table--header");
  const body = document.querySelector(".table--body");

  for (let value in json) {
    const thElement = document.createElement("th");
    header.appendChild(thElement);
    thElement.innerHTML = value;
  }

  for (let i in json["IPs"]) {
    const trElement = document.createElement("tr");
    for (let value in json) {
      const tdElement = document.createElement("td");
      tdElement.innerHTML = json[value][i];
      trElement.appendChild(tdElement);
      body.appendChild(trElement);
    }
  }
}
