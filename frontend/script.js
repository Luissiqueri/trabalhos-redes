document.getElementById("input--file").addEventListener("change", (event) => {
  event.preventDefault();

  if (event.target.files.length > 0) {
    document.getElementsByClassName("input--file--label")[0].innerHTML = event.target.files[0].name
    document.getElementsByClassName("icon--close")[0].classList.remove("hidden");
  };
})

const removeFile = (event) => {
  event.preventDefault();

  document.getElementById("input--file").value = "";

  document.getElementsByClassName("input--file--label")[0].innerHTML = "Selecione seu arquivo";
  document.getElementsByClassName("icon--close")[0].classList.add("hidden");
}

const clickButton = (event, protocol, filePath) => {
  event.preventDefault();

  const formData = new FormData();
  formData.append("file", filePath);

  fetch(`http://localhost:8000/uploadfile/${protocol}`, {
    method: "POST",
    body: formData,
  })
    .then(async (response) => showResults(await response.json(), protocol))
    .catch((error) => {
      console.log(error);
    });
}

const submitForm = (event) => {
  event.preventDefault();

  const input = document.getElementById("input--file");
  const type = document.getElementById("protocol--select");
  const protocol = type.value;

  if (input.files.length > 0) clickButton(event, protocol, input.files[0]);
  else console.log("Erro: nenhum arquivo encontrado");
}

function showResults(jsonResposnse, protocol) {
  const api = document.querySelector(".main--api");
  while (api.hasChildNodes()) {
    api.removeChild(api.firstChild);
  }
  
  console.log(protocol);
  
  if (protocol === "IP") {
    showIPData();
  } else if (protocol === "ARP") {
    showARPData(jsonResposnse);
  }
  else if (protocol === "RIP") {
    showRIPData(jsonResposnse);
  }
  else if (protocol === "UDP") {
    showUDPData(jsonResposnse);
  }
  else if (protocol === "TCP") {
    showTCPData(jsonResposnse);
  }
  else if (protocol === "HTTP") {
    showHTTPData(jsonResposnse);
  }
  else if (protocol === "DNS") {
    showDNSData(jsonResposnse);
  }
  else if (protocol === "SNMP") {
    showNLBData(jsonResposnse);
  }
}

function showIPData() {
  const api = document.querySelector(".main--api");

  const imageApi = document.createElement("div");
  imageApi.classList.add("image--api");

  api.append(imageApi);

  const img1 = document.createElement("div");
  img1.classList.add("image");
  img1.classList.add("img-1");
  imageApi.appendChild(img1);

  const imgFluxGraph = document.createElement("IMG");
  imgFluxGraph.src = "http://localhost:8000/graficos/fluxGraph.svg";
  img1.appendChild(imgFluxGraph);

  let title = document.createElement("p");
  title.innerHTML = "Gráfico mostrando visualmente o fluxo de dados.";
  title.className = "title";
  img1.appendChild(title);

  let subtitle = document.createElement("p");
  subtitle.innerHTML =
    "*A Largura da aresta indica a quantidade de vezes que ocorreu.";
  subtitle.className = "subtitle";
  img1.appendChild(subtitle);

  const img2 = document.createElement("div");
  img2.classList.add("image");
  img2.classList.add("img-2");
  imageApi.appendChild(img2);

  const imgLocationsGraph = document.createElement("IMG");
  imgLocationsGraph.src = "http://localhost:8000/graficos/locationsGraph.svg";
  img2.appendChild(imgLocationsGraph);

  title = document.createElement("p");
  title.innerHTML =
    "Gráfico sinalizando visualmente a posição geográfica de cada IP.";
  title.className = "title";
  img2.appendChild(title);

  subtitle = document.createElement("p");
  subtitle.innerHTML =
    "*O raio do círculo maior indica a quantidade de IP's presentes naquela região.";
  subtitle.className = "subtitle";
  img2.appendChild(subtitle);
}

function showARPData(json) {
  const api = document.querySelector(".main--api");

  const table = document.createElement("div");
  table.classList.add("Table");

  api.append(table);

  const tableContainer = document.createElement("table");
  tableContainer.classList.add("table--container");

  table.append(tableContainer);

  const tableHeader = document.createElement("thead");
  tableHeader.classList.add("table--header");

  tableContainer.append(tableHeader);

  const tableBody = document.createElement("tbody");
  tableBody.classList.add("table--body");

  tableContainer.append(tableBody);


  for (let value in json) {
    const thElement = document.createElement("th");
    tableHeader.appendChild(thElement);
    thElement.innerHTML = value;
  }

  for (let i in json["IPs"]) {
    const trElement = document.createElement("tr");
    for (let value in json) {
      const tdElement = document.createElement("td");
      tdElement.innerHTML = json[value][i];
      trElement.appendChild(tdElement);
      tableBody.appendChild(trElement);
    }
  }
}

function showRIPData(json) {
  console.log(json);
}

function showUDPData(json) {

}

function showTCPData(json) {

}

function showHTTPData(json) {

}

function showDNSData(json) {

}

function showNLBData(json) {

}


const selectFile = (event, protocol, filePath) => {
  event.preventDefault();

  fetchFile(filePath).then(fileBlob => {
    const formData = new FormData();
    formData.append("file", new File([fileBlob], protocol));

    return fetch(`http://localhost:8000/uploadfile/${protocol}`, {
      method: "POST",
      body: formData,
    });
  }).then(async (response) => {
    const result = await response.json();
    showResults(result, protocol);
  }).catch((error) => {
    console.error('Error:', error);
  });
}

async function fetchFile(filePath) {
  try {
    const response = await fetch(filePath);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const fileBlob = await response.blob();
    return fileBlob;
  } catch (error) {
    console.error('Error fetching the file:', error);
    throw error;
  }
}

































































// const input = document.querySelector("#input--file");
// const inputProtocol = document.querySelector("#protocol--select");
// const label = document.querySelector(".input--file--label");
// const closeIcon = document.querySelector(".icon--close");
// const buttonSendFile = document.querySelector(".send--file--button");
// const loadIcon = document.querySelector(".icon--load");
// const inputView = document.querySelector(".input--file--container");
// const selectView = document.querySelector(".protocol--container");
// const image1 = document.querySelector(".img-1");
// const image2 = document.querySelector(".img-2");

// let lengthGraphs = 0;

// input.style.opacity = 0;

// input.addEventListener("change", function (event) {
//   event.preventDefault();

//   if (input.files.length > 0) {
//     buttonSendFile.disabled = false;
//     closeIcon.style.display = "block";
//     var fileName = input.files[0].name;
//   }
//   label.innerHTML = fileName;
// });

// function removeFile() {
//   label.innerHTML = "Selecione seu arquivo";
//   closeIcon.style.display = "none";
//   buttonSendFile.disabled = true;
//   input.value = null;
//   while (image1.hasChildNodes()) {
//     image1.removeChild(image1.firstChild);
//   }
//   while (image2.hasChildNodes()) {
//     image2.removeChild(image2.firstChild);
//   }

//   const header = document.querySelector(".table--header");
//   while (header.hasChildNodes()) {
//     header.removeChild(header.firstChild);
//   }

//   const body = document.querySelector(".table--body");
//   while (body.hasChildNodes()) {
//     body.removeChild(body.firstChild);
//   }
//   document.querySelector(".Table").classList.add("hidden");
// }

// document.querySelector(".send--file--button").addEventListener("click", clickButton);

// function clickButton(event) {
//   console.log(event);
//   event.preventDefault();

//   loadIcon.classList.remove("hidden");
//   while (image1.hasChildNodes()) {
//     image1.removeChild(image1.firstChild);
//   }
//   while (image2.hasChildNodes()) {
//     image2.removeChild(image2.firstChild);
//   }

//   const header = document.querySelector(".table--header");
//   while (header.hasChildNodes()) {
//     header.removeChild(header.firstChild);
//   }
//   const body = document.querySelector(".table--body");
//   while (body.hasChildNodes()) {
//     body.removeChild(body.firstChild);
//   }

//   const formData = new FormData();
//   formData.append("file", input.files[0]);
//   const protocol = inputProtocol.value;

//   fetch(`http://localhost:8000/uploadfile/${protocol}`, {
//     method: "POST",
//     body: formData,
//   })
//     .then(async (response) => showResults(await response.json(), protocol))
//     .catch((error) => {
//       console.log(error);
//     });
//   if (value) {
//     fetch(file).then(response => response.blob()).then(blob => {
//       const formData = new FormData();
//       formData.append("file", blob);

//       fetch(`http://localhost:8000/uploadfile/${value}`, {
//         method: "POST",
//         body: formData,
//       })
//         .then(async (response) => showResults(await response.json(), value))
//         .catch((error) => {
//           console.log(error);
//         });
//     })
//   } else {
//     const formData = new FormData();
//     formData.append("file", input.files[0]);
//     const protocol = inputProtocol.value;
//     fetch(`http://localhost:8000/uploadfile/${protocol}`, {
//       method: "POST",
//       body: formData,
//     })
//       .then(async (response) => showResults(await response.json(), protocol))
//       .catch((error) => {
//         console.log(error);
//       });
//   }
// }

