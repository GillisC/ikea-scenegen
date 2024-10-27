


var selectedCountry = undefined

  fetch('http://127.0.0.1:8080/list-files')
    .then(response => response.json())
    .then(data => {
      data.forEach(file => {
        console.log(file);
      });
    })
    .catch(error => console.error('Error fetching files:', error));


var map = L.map('map', {
  scrollWheelZoom: false,
  zoomControl: false 
}).setView([60.505, 10.09], 3);

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);


fetch('http://127.0.0.1:8080/list-files')
    .then(response => response.json())
    .then(data => {
      data.forEach(file => {
        fetch("static/boundries/" + file)
              .then(response => response.json())
              .then(jsonData => {
                // Add the GeoJSON layer to the map
                L.geoJSON(jsonData, {
                  onEachFeature: function (feature, layer) {
                    layer.on('click', function () {
                      selectedCountry = file.replaceAll(".json", "").replaceAll("_", " ").replace(/(?:^|\s|["'([{])+\S/g, match => match.toUpperCase());
                      changeCountryName(selectedCountry)
                      console.log(selectedCountry)
                    });
                  },
                  style: function (feature) {
                    return {color: "#ff7800", weight: 2};
                  }
                }).addTo(map);
              })
      .catch(error => console.error('Error loading GeoJSON:', error));
    });
  })
  .catch(error => console.error('Error fetching files:', error));

  function getSelectedCountry()
  {
    return selectedCountry;
  }

  function changeCountryName(name)
  {
    document.getElementById("countryName").innerHTML = "Selected Country: " + name;
  }