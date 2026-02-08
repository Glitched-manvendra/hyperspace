import { useEffect, useState, useRef, useCallback, type FormEvent } from "react";
import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  useMap,
  useMapEvents,
} from "react-leaflet";
import L from "leaflet";
import { Search, Loader2, MapPin, X } from "lucide-react";

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

/** Pulsing marker for click-selected locations */
const clickIcon = L.divIcon({
  className: "map-click-marker",
  html: '<div class="click-marker-pulse"></div><div class="click-marker-dot"></div>',
  iconSize: [24, 24],
  iconAnchor: [12, 12],
});

/** Default center — Central India */
const DEFAULT_CENTER: [number, number] = [22.9734, 78.6569];

// ── Nominatim helpers (free, no API key) ────────────────────────────

interface GeoResult {
  lat: number;
  lon: number;
  display_name: string;
}

async function forwardGeocode(query: string): Promise<GeoResult | null> {
  try {
    // Add "India" hint for better results with small towns
    const searchQuery = query.includes(",") ? query : `${query}, India`;
    const url = `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(
      searchQuery
    )}&format=json&limit=5&accept-language=en`;
    const resp = await fetch(url, {
      headers: { "User-Agent": "OrbitalNexus/1.0" },
    });
    const data = await resp.json();
    if (data.length > 0) {
      return {
        lat: parseFloat(data[0].lat),
        lon: parseFloat(data[0].lon),
        display_name: data[0].display_name,
      };
    }
    // Retry without "India" suffix if no results (for international queries)
    if (searchQuery !== query) {
      const url2 = `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(
        query
      )}&format=json&limit=5&accept-language=en`;
      const resp2 = await fetch(url2, {
        headers: { "User-Agent": "OrbitalNexus/1.0" },
      });
      const data2 = await resp2.json();
      if (data2.length > 0) {
        return {
          lat: parseFloat(data2[0].lat),
          lon: parseFloat(data2[0].lon),
          display_name: data2[0].display_name,
        };
      }
    }
  } catch {
    /* graceful fallback */
  }
  return null;
}

/** Forward-geocode multiple place names (split by "and", ",", "&") */
async function forwardGeocodeMulti(query: string): Promise<GeoResult[]> {
  // Split on " and ", ",", " & "
  const parts = query.split(/\s+and\s+|\s*,\s*|\s*&\s*/i).map((s) => s.trim()).filter(Boolean);
  if (parts.length <= 1) {
    const single = await forwardGeocode(query);
    return single ? [single] : [];
  }

  // Geocode all in parallel
  const results = await Promise.all(parts.map((p) => forwardGeocode(p)));
  return results.filter((r): r is GeoResult => r !== null);
}

async function reverseGeocode(
  lat: number,
  lon: number
): Promise<string | null> {
  try {
    const url = `https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lon}&format=json&zoom=10&accept-language=en`;
    const resp = await fetch(url, {
      headers: { "User-Agent": "OrbitalNexus/1.0" },
    });
    const data = await resp.json();
    const addr = data.address ?? {};
    const city =
      addr.city ?? addr.town ?? addr.village ?? addr.county ?? addr.state_district;
    const state = addr.state ?? "";
    if (city && state) return `${city}, ${state}`;
    if (city) return city;
    if (state) return state;
    return data.display_name?.split(",").slice(0, 2).join(",") ?? null;
  } catch {
    return null;
  }
}

// ── Sub-components ──────────────────────────────────────────────────

/** Flies the map camera to new coordinates */
function MapController({ center }: { center: [number, number] }) {
  const map = useMap();
  useEffect(() => {
    map.flyTo(center, 12, { duration: 1.8 });
  }, [center, map]);
  return null;
}

/** Captures click events on the map */
function ClickHandler({
  onClick,
}: {
  onClick: (lat: number, lon: number) => void;
}) {
  useMapEvents({
    click(e) {
      onClick(e.latlng.lat, e.latlng.lng);
    },
  });
  return null;
}

// ── Search Bar ──────────────────────────────────────────────────────

interface SearchBarProps {
  onSearch: (lat: number, lon: number, name: string) => void;
  onMultiSearch?: (locations: { lat: number; lon: number; name: string }[]) => void;
  loading: boolean;
}

function MapSearchBar({ onSearch, onMultiSearch, loading }: SearchBarProps) {
  const [query, setQuery] = useState("");
  const [searchLoading, setSearchLoading] = useState(false);
  const [searchError, setSearchError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    const trimmed = query.trim();
    if (!trimmed || searchLoading || loading) return;

    setSearchLoading(true);
    setSearchError(null);

    // Check if query contains multiple places (has "and", ",", "&")
    const hasMultiple = /\s+and\s+|\s*,\s*|\s*&\s*/i.test(trimmed);

    if (hasMultiple && onMultiSearch) {
      const results = await forwardGeocodeMulti(trimmed);
      if (results.length > 0) {
        const locations = results.map((r) => ({
          lat: r.lat,
          lon: r.lon,
          name: r.display_name.split(",").slice(0, 2).join(",").trim(),
        }));
        onMultiSearch(locations);
        setQuery("");
      } else {
        setSearchError(`Could not find any of those places. Check spelling or try one at a time.`);
      }
    } else {
      const result = await forwardGeocode(trimmed);
      if (result) {
        onSearch(result.lat, result.lon, result.display_name);
        setQuery("");
      } else {
        setSearchError(`Could not find "${trimmed}". Try adding a state name (e.g., "${trimmed}, UP").`);
      }
    }
    setSearchLoading(false);
  };

  return (
    <div className="absolute top-3 left-3 z-[1000] w-72 sm:w-80">
      <form onSubmit={handleSubmit} className="relative">
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setSearchError(null);
          }}
          placeholder="Search any place… (e.g., Sultanpur or Agra, Mathura)"
          className="w-full pl-10 pr-10 py-2.5 text-sm rounded-lg border-2 border-border bg-surface text-text shadow-neo-sm focus:outline-none focus:ring-2 focus:ring-primary placeholder:text-text/40"
          disabled={searchLoading || loading}
        />
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text/40" />
        {query && (
          <button
            type="button"
            onClick={() => {
              setQuery("");
              setSearchError(null);
              inputRef.current?.focus();
            }}
            className="absolute right-10 top-1/2 -translate-y-1/2 text-text/40 hover:text-text"
          >
            <X className="w-4 h-4" />
          </button>
        )}
        <button
          type="submit"
          disabled={!query.trim() || searchLoading || loading}
          className="absolute right-2 top-1/2 -translate-y-1/2 p-1 rounded text-primary disabled:text-text/20"
        >
          {searchLoading ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <MapPin className="w-4 h-4" />
          )}
        </button>
      </form>
      {searchError && (
        <div className="mt-1 px-3 py-1.5 text-xs rounded-lg bg-red-100 dark:bg-red-900/40 text-red-700 dark:text-red-300 border border-red-300 dark:border-red-700">
          {searchError}
        </div>
      )}
    </div>
  );
}

// ── Click Tooltip ───────────────────────────────────────────────────

interface ClickTooltipProps {
  lat: number;
  lon: number;
  name: string | null;
  loading: boolean;
}

function ClickTooltip({ lat, lon, name, loading }: ClickTooltipProps) {
  return (
    <div className="absolute bottom-20 left-1/2 -translate-x-1/2 z-[1000] pointer-events-none">
      <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-surface border-2 border-border shadow-neo-sm text-sm whitespace-nowrap pointer-events-auto">
        {loading ? (
          <>
            <Loader2 className="w-3.5 h-3.5 animate-spin text-primary" />
            <span className="text-text/70">
              Analyzing {lat.toFixed(2)}°N, {lon.toFixed(2)}°E …
            </span>
          </>
        ) : (
          <>
            <MapPin className="w-3.5 h-3.5 text-primary" />
            <span className="font-semibold text-text">
              {name ?? `${lat.toFixed(4)}°N, ${lon.toFixed(4)}°E`}
            </span>
          </>
        )}
      </div>
    </div>
  );
}

// ── Main MapView ────────────────────────────────────────────────────

interface MapViewProps {
  lat?: number;
  lon?: number;
  regionName?: string;
  /** Called when user clicks the map or searches a single place */
  onLocationSelect?: (lat: number, lon: number, name?: string) => void;
  /** Called when user searches multiple places (e.g., "Agra and Mathura") */
  onMultiLocationSelect?: (locations: { lat: number; lon: number; name: string }[]) => void;
  /** Additional markers from multi-location queries */
  extraMarkers?: { lat: number; lon: number; name: string }[];
  /** Whether parent is currently loading data */
  loading?: boolean;
}

/**
 * MapView — Interactive Leaflet map
 *
 * Features:
 * - Click/tap anywhere to select a location and fetch data
 * - Search bar for finding any city, town, or village (including small ones)
 * - Multi-city search: "Agra, Mathura" places markers on all
 * - Smooth fly-to animations
 * - Reverse geocoding for clicked coordinates
 * - Mobile responsive
 */
function MapView({
  lat,
  lon,
  regionName,
  onLocationSelect,
  onMultiLocationSelect,
  extraMarkers = [],
  loading = false,
}: MapViewProps) {
  const [clickedPos, setClickedPos] = useState<[number, number] | null>(null);
  const [clickedName, setClickedName] = useState<string | null>(null);
  const [resolving, setResolving] = useState(false);

  // The "active" position = API response position > clicked position > default
  const activePos: [number, number] = [
    lat ?? clickedPos?.[0] ?? DEFAULT_CENTER[0],
    lon ?? clickedPos?.[1] ?? DEFAULT_CENTER[1],
  ];

  /** Handle a map click */
  const handleMapClick = useCallback(
    async (clickLat: number, clickLon: number) => {
      setClickedPos([clickLat, clickLon]);
      setClickedName(null);
      setResolving(true);

      // Reverse geocode to get place name
      const name = await reverseGeocode(clickLat, clickLon);
      setClickedName(name);
      setResolving(false);

      // Notify parent → triggers backend query
      onLocationSelect?.(clickLat, clickLon, name ?? undefined);
    },
    [onLocationSelect]
  );

  /** Handle a search result */
  const handleSearch = useCallback(
    (searchLat: number, searchLon: number, displayName: string) => {
      const shortName = displayName.split(",").slice(0, 2).join(",").trim();
      setClickedPos([searchLat, searchLon]);
      setClickedName(shortName);
      onLocationSelect?.(searchLat, searchLon, shortName);
    },
    [onLocationSelect]
  );

  /** Handle multi-city search results */
  const handleMultiSearch = useCallback(
    (locations: { lat: number; lon: number; name: string }[]) => {
      if (locations.length > 0) {
        // Center on the first location
        setClickedPos([locations[0].lat, locations[0].lon]);
        setClickedName(locations.map((l) => l.name.split(",")[0]).join(", "));
      }
      onMultiLocationSelect?.(locations);
    },
    [onMultiLocationSelect]
  );

  return (
    <div className="relative w-full h-full">
      <MapContainer
        center={DEFAULT_CENTER}
        zoom={5}
        className="w-full h-full map-container"
        zoomControl={false}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <MapController center={activePos} />
        <ClickHandler onClick={handleMapClick} />

        {/* Main marker (from API response) */}
        {lat != null && lon != null && (
          <Marker position={[lat, lon]}>
            <Popup>
              <strong>{regionName ?? "Selected Location"}</strong>
              <br />
              {lat.toFixed(4)}°N, {lon.toFixed(4)}°E
              <br />
              <span className="text-xs text-gray-500">
                Satellite analysis target
              </span>
            </Popup>
          </Marker>
        )}

        {/* Click marker (before API response arrives) */}
        {clickedPos && !(lat != null && lon != null) && (
          <Marker position={clickedPos} icon={clickIcon}>
            <Popup>
              <strong>{clickedName ?? "Loading…"}</strong>
              <br />
              {clickedPos[0].toFixed(4)}°N, {clickedPos[1].toFixed(4)}°E
            </Popup>
          </Marker>
        )}

        {/* Extra markers from multi-location queries */}
        {extraMarkers.map((m, i) => (
          <Marker key={`extra-${i}-${m.lat}-${m.lon}`} position={[m.lat, m.lon]}>
            <Popup>
              <strong>{m.name}</strong>
              <br />
              {m.lat.toFixed(4)}°N, {m.lon.toFixed(4)}°E
              <br />
              <span className="text-xs text-gray-500">
                Satellite analysis target
              </span>
            </Popup>
          </Marker>
        ))}
      </MapContainer>

      {/* Search bar overlay */}
      <MapSearchBar onSearch={handleSearch} onMultiSearch={handleMultiSearch} loading={loading} />

      {/* Click tooltip (shows while loading) */}
      {(loading || resolving) && clickedPos && (
        <ClickTooltip
          lat={clickedPos[0]}
          lon={clickedPos[1]}
          name={clickedName}
          loading={loading || resolving}
        />
      )}

      {/* Tap hint (shown when no data loaded yet) */}
      {!loading && !clickedPos && lat == null && (
        <div className="absolute bottom-20 left-1/2 -translate-x-1/2 z-[1000] pointer-events-none">
          <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-surface/90 border-2 border-border shadow-neo-sm text-xs text-text/60 animate-pulse">
            <MapPin className="w-3.5 h-3.5" />
            Tap anywhere on the map or search a city
          </div>
        </div>
      )}
    </div>
  );
}

export default MapView;
