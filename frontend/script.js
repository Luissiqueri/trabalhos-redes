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
  const api = document.querySelector(".main--api");
  const pacotes = json;
  let routers = {};
  
  const NEVER = -1;

  //pega o estado final enviado de cada roteador:
  for (let i = pacotes.length - 1; i >= 0; i--) {
    const pacote = pacotes[i];
    if (routers[pacote.src] == undefined) {
      routers[pacote.src] = {}
      routers[pacote.src].table = pacote.table;
      routers[pacote.src].lastSend = i;
      routers[pacote.src].lastReceived = NEVER;
    }
  }

  for (let i = pacotes.length - 1; i >= 0; i--) {
    const pacote = pacotes[i];
    let router;
    if (routers[pacote.dst] == undefined) {
      router = {}
      router.lastReceived = NEVER;
      router.lastSend = NEVER;
    } else {
      router = routers[pacote.dst];
    }
    if (i > router.lastReceived) {
      router.lastReceived = i;
      routers[pacote.dst] = router;
    }
  }

  //encontra roteadores que receberam tabelas depois de terem mandado a sua:
  let pendingRouters = [];
  for (let routerIP in routers) {
    let router = routers[routerIP];
    if (router.lastReceived > router.lastSend) {
      router.ip = routerIP;
      pendingRouters.push(router);
    }
  }

  console.log(pendingRouters);

  //calcula a tabela resultante dos roteadores pendentes
  for (let router of pendingRouters) {
    if (router.table == undefined) {
      router.table = [];
    }
    for (let i = router.lastSend + 1; i < pacotes.length; i++) {
      const pacote = pacotes[i];
      if (pacote.dst == router.ip) {
        let table = pacote.table;
        for (let entry of table) {
          let entryCopiada = JSON.parse(JSON.stringify(entry));
          entryCopiada.next = pacote.src;
          entryCopiada.metric += 1;
          let entryIndex = -1;
          for (let currentEntryIndex = 0; currentEntryIndex < router.table.length; currentEntryIndex++) {
            if (router.table[currentEntryIndex].IP == entryCopiada.IP) {
              entryIndex = currentEntryIndex;
              break;
            }
          }
          if (entryIndex == -1) {
            router.table.push(entryCopiada);
          } else {
            let currentEntry = router.table[entryIndex];
            if (currentEntry.next == entryCopiada.next) {
              router.table[entryIndex] = entryCopiada;
            } else if (currentEntry.metric > entryCopiada.metric) {
              router.table[entryIndex] = entryCopiada;
            }
          }
        }
      }
    }
  }
  for (let calculatedRouter of pendingRouters) {
    routers[calculatedRouter.ip] = calculatedRouter;
  }
  
  api.innerHTML = "";
  api.style.paddingTop = "200px";
  for (let routerIP in routers) {
    let router = routers[routerIP];
    let routerDiv = document.createElement("DIV");
    let routerIPDiv = document.createElement("DIV");
    routerIPDiv.innerText = "Tabela RIP resultante do roteador " + routerIP;
    routerDiv.appendChild(routerIPDiv);
    routerDiv.style.marginTop = "20px";
    let ripTable = document.createElement("TABLE");
    routerDiv.appendChild(ripTable);
    let ripHeader = document.createElement("TR");
    let ipHeader = document.createElement("TH");
    ipHeader.innerText = "IP";
    ripHeader.appendChild(ipHeader);
    let maskHeader = document.createElement("TH");
    maskHeader.innerText = "Mask";
    ripHeader.appendChild(maskHeader);
    let metricHeader = document.createElement("TH");
    metricHeader.innerText = "Saltos";
    ripHeader.appendChild(metricHeader);
    let nextHeader = document.createElement("TH");
    nextHeader.innerText = "Next";
    ripHeader.appendChild(nextHeader);
    ripTable.appendChild(ripHeader);
    for (let entry of router.table) {
      let ripEntry = document.createElement("TR");
      let ip = document.createElement("TD");
      ip.innerText = entry.IP;
      ripEntry.appendChild(ip);
      let mask = document.createElement("TD");
      mask.innerText = entry.mask;
      ripEntry.appendChild(mask);
      let metric = document.createElement("TD");
      metric.innerText = entry.metric;
      ripEntry.appendChild(metric);
      let next = document.createElement("TD");
      next.innerText = entry.next;
      ripEntry.appendChild(next);
      ripTable.appendChild(ripEntry);
    }
    routerDiv.appendChild(ripTable);
    api.appendChild(routerDiv);
  }
}

function showUDPData(json) {

}

function showTCPData(json) {

}

function showHTTPData(json) {
  const contents = json;
  const api = document.querySelector(".main--api");
  api.innerHTML = `<div style="font-size: 18px; font-weight: bold;">Conteúdos acessados por cada host</div>`;
  api.style.paddingTop = "100px";
  for (let ip in contents) {
    let ipCOntentsDiv = document.createElement("DIV");
    ipCOntentsDiv.style.fontSize = "15px";
    ipCOntentsDiv.style.marginTop = "15px";
    ipCOntentsDiv.innerHTML = `<span>Conteúdos acessados pelo host ${ip}:</span>`;
    for (let content of contents[ip]) {
      let contentLinkDiv = document.createElement("DIV");
      contentLinkDiv.style.backgroundColor = "#fa7070";
      contentLinkDiv.style.padding = "5px";
      contentLinkDiv.style.borderRadius = "0.25rem";
      contentLinkDiv.style.margin = "10px 0px";
      contentLinkDiv.innerHTML = `<a style="color: white" target="_blank" href="../${content.path}">${content.type}</a>`;
      ipCOntentsDiv.appendChild(contentLinkDiv);
    }
    api.appendChild(ipCOntentsDiv);
  }
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

