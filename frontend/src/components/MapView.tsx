import { useEffect } from "react";
import { MapContainer, TileLayer, Marker, Popup, useMap } from "react-leaflet";
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

/** Default center — Greater Noida */
const DEFAULT_CENTER: [number, number] = [28.4744, 77.504];

/**
 * MapController — flies the map camera to new coordinates
 */
function MapController({ center }: { center: [number, number] }) {
  const map = useMap();
  useEffect(() => {
    map.flyTo(center, 12, { duration: 2 });
  }, [center, map]);
  return null;
}

interface MapViewProps {
  lat?: number;
  lon?: number;
  regionName?: string;
}

/**
 * MapView — Leaflet map with dynamic flyTo
 *
 * Shows the target region for satellite data fusion.
 * When new coordinates arrive, smoothly flies the camera to the location.
 */
function MapView({ lat, lon, regionName }: MapViewProps) {
  const position: [number, number] = [lat ?? DEFAULT_CENTER[0], lon ?? DEFAULT_CENTER[1]];
  const label = regionName ?? "Greater Noida";

  return (
    <MapContainer
      center={DEFAULT_CENTER}
      zoom={11}
      className="w-full h-full"
      zoomControl={false}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <MapController center={position} />
      <Marker position={position}>
        <Popup>
          <strong>{label}</strong>
          <br />
          {position[0].toFixed(4)}°N, {position[1].toFixed(4)}°E
          <br />
          <span className="text-xs text-gray-500">
            Satellite analysis target
          </span>
        </Popup>
      </Marker>
    </MapContainer>
  );
}

export default MapView;
