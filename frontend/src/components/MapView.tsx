import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import L from "leaflet";

// Fix default marker icon issue with bundlers
import markerIcon2x from "leaflet/dist/images/marker-icon-2x.png";
import markerIcon from "leaflet/dist/images/marker-icon.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";

// @ts-expect-error — Leaflet icon defaults workaround
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});

/** Greater Noida coordinates — default map center */
const GREATER_NOIDA: [number, number] = [28.4744, 77.504];

/**
 * MapView — Leaflet map centered on Greater Noida
 *
 * Shows the target region for satellite data fusion.
 * Future: will render data overlays (NDVI heatmaps, flood risk zones, etc.)
 */
function MapView() {
  return (
    <MapContainer
      center={GREATER_NOIDA}
      zoom={11}
      className="w-full h-full"
      zoomControl={false}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <Marker position={GREATER_NOIDA}>
        <Popup>
          <strong>Greater Noida</strong>
          <br />
          28.4744°N, 77.504°E
          <br />
          <span className="text-xs text-gray-500">
            Default analysis region
          </span>
        </Popup>
      </Marker>
    </MapContainer>
  );
}

export default MapView;
