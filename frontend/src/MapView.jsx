import { MapContainer, TileLayer, CircleMarker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";

// Hardcoded for Day 1 — replaced by API fetch on Day 5
const STUB_PINS = [
  { lat: 24.89, lng: 91.87, title: "Flooding · Bangladesh", category: "climate" },
  { lat: 19.61, lng: 37.21, title: "Cholera outbreak · Sudan", category: "disease" },
  { lat: -1.67, lng: 29.22, title: "Armed conflict · DRC", category: "conflict" },
  { lat: 5.15,  lng: 46.19, title: "Food crisis · Somalia", category: "famine" },
  { lat: 37.97, lng: 23.72, title: "Wildfires · Greece", category: "climate" },
];

const CATEGORY_COLORS = {
  conflict:    "#E24B4A",   // red
  climate:     "#378ADD",   // blue
  famine:      "#EF9F27",   // amber
  disease:     "#7F77DD",   // purple
  displacement:"#1D9E75",   // teal
  other:       "#888780",   // gray
};

export default function MapView() {
  return (
    <MapContainer
      center={[20, 10]}
      zoom={2.5}
      style={{ height: "100vh", width: "100%", background: "#0d1117" }}
    >
      <TileLayer
        url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        attribution='&copy; <a href="https://carto.com">CARTO</a>'
      />

      {STUB_PINS.map((pin, i) => (
        <CircleMarker
          key={i}
          center={[pin.lat, pin.lng]}
          radius={10}
          pathOptions={{
            color: CATEGORY_COLORS[pin.category] ?? "#888",
            fillColor: CATEGORY_COLORS[pin.category] ?? "#888",
            fillOpacity: 0.75,
            weight: 1.5,
          }}
        >
          <Popup>
            <strong>{pin.title}</strong>
            <br />
            <span style={{ fontSize: 12, color: "#888" }}>
              Category: {pin.category}
            </span>
          </Popup>
        </CircleMarker>
      ))}
    </MapContainer>
  );
}