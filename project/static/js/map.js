


var selectedCountry = undefined
var mapBoundries = new Map()
const unselectedColor = "#0058ab"
const selectedColor = "#fbd914"

  fetch('http://127.0.0.1:8080/list-files')
    .then(response => response.json())
    .then(data => {
      data.forEach(file => {
        //console.log(file);
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
                var countryName = file.replaceAll(".json", "").replaceAll("_", " ").replace(/(?:^|\s|["'([{])+\S/g, match => match.toUpperCase())
                var bound = L.geoJSON(jsonData, {
                  onEachFeature: function (feature, layer) {
                    layer.on('click', function () {
                      selectedCountry = countryName
                      changeCountryName(selectedCountry)
                      changeSelectedBoundColor(selectedCountry)
                      //console.log(selectedCountry)
                    });
                  },
                  style: function (feature) {
                    return {color: unselectedColor, weight: 2};
                  }
                })
                bound.addTo(map)
                mapBoundries.set(countryName, bound)
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

  function changeSelectedBoundColor(name)
  {
    for (const i of mapBoundries.keys())
    {
      const bound = mapBoundries.get(i)
      bound.setStyle({"color": unselectedColor})
    }

    const bound = mapBoundries.get(name)
    bound.setStyle({"color": selectedColor})
  }