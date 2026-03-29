// Map integration using Leaflet

let hotelMap = null;
let markersLayer = null;

function initializeMap() {
  // Don't initialize if already initialized
  if (hotelMap) return;

  try {
    // Initialize Leaflet map
    hotelMap = L.map("map").setView(
      window.CONFIG.MAP_CENTER,
      window.CONFIG.MAP_ZOOM
    );

    // Add OpenStreetMap tiles
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: "© OpenStreetMap contributors",
      maxZoom: 19,
    }).addTo(hotelMap);

    // Create marker layer group
    markersLayer = L.layerGroup().addTo(hotelMap);

    // Export to window for access from other modules
    window.hotelMap = hotelMap;

    console.log("🗺️ Map initialized successfully");
  } catch (error) {
    console.error("❌ Map initialization error:", error);
  }
}

// Update Map with Hotels
function updateMapMarkers(hotels, landmark) {
  if (!hotelMap || !markersLayer) return;

  // Clear existing markers
  markersLayer.clearLayers();

  // Add landmark marker if available
  if (landmark && landmark.coordinates) {
    const [lat, lng] = landmark.coordinates;

    const landmarkIcon = L.divIcon({
      className: "landmark-marker",
      html: '<div style="background: #ef4444; color: white; width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 20px; border: 3px solid white; box-shadow: 0 2px 8px rgba(0,0,0,0.3);">🏛️</div>',
      iconSize: [40, 40],
    });

    const landmarkMarker = L.marker([lat, lng], { icon: landmarkIcon })
      .bindPopup(`
                <div style="text-align: center; padding: 0.5rem;">
                    <strong style="font-size: 1.1rem;">${landmark.name}</strong>
                    <br>
                    <span style="color: #64748b;">Landmark</span>
                </div>
            `);

    markersLayer.addLayer(landmarkMarker);

    // Center map on landmark
    hotelMap.setView([lat, lng], 13);
  }

  // Add hotel markers
  hotels.forEach((hotel, index) => {
    const lat = hotel.coordinates.lat;
    const lng = hotel.coordinates.lng;

    // Color based on recommendation score
    let color = "#10b981"; // green
    if (hotel.recommendation_score < 50) {
      color = "#ef4444"; // red
    } else if (hotel.recommendation_score < 75) {
      color = "#f59e0b"; // yellow
    }

    const hotelIcon = L.divIcon({
      className: "hotel-marker",
      html: `<div style="background: ${color}; color: white; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 16px; border: 2px solid white; box-shadow: 0 2px 6px rgba(0,0,0,0.3); font-weight: bold;">${
        index + 1
      }</div>`,
      iconSize: [32, 32],
    });

    const marker = L.marker([lat, lng], { icon: hotelIcon }).bindPopup(`
                <div style="min-width: 200px;">
                    <h3 style="margin: 0 0 0.5rem 0; font-size: 1rem;">${
                      hotel.name
                    }</h3>
                    <p style="margin: 0.25rem 0; font-size: 0.875rem;">
                        <strong>Rating:</strong> ${"⭐".repeat(
                          Math.floor(hotel.star_rating)
                        )} ${hotel.star_rating}
                    </p>
                    <p style="margin: 0.25rem 0; font-size: 0.875rem;">
                        <strong>Price:</strong> ${
                          hotel.price_per_night
                        } SAR/night
                    </p>
                    <p style="margin: 0.25rem 0; font-size: 0.875rem;">
                        <strong>Score:</strong> ${
                          hotel.recommendation_score
                        }/100
                    </p>
                    ${
                      hotel.distance
                        ? `
                        <p style="margin: 0.25rem 0; font-size: 0.875rem;">
                            <strong>Distance:</strong> ${hotel.distance}
                        </p>
                    `
                        : ""
                    }
                    <button 
                        onclick="window.showHotelDetails(${hotel.id})"
                        style="margin-top: 0.5rem; padding: 0.5rem 1rem; background: #2563eb; color: white; border: none; border-radius: 0.375rem; cursor: pointer; width: 100%; font-weight: 600;"
                    >
                        View Details
                    </button>
                </div>
            `);

    markersLayer.addLayer(marker);
  });

  // Fit map to show all markers if no landmark
  if (!landmark && hotels.length > 0) {
    const bounds = L.latLngBounds(
      hotels.map((h) => [h.coordinates.lat, h.coordinates.lng])
    );
    hotelMap.fitBounds(bounds, { padding: [50, 50] });
  }

  // Update map info
  const mapInfo = document.getElementById("mapInfo");
  if (mapInfo) {
    mapInfo.textContent = `Showing ${hotels.length} hotels`;
    if (landmark) {
      mapInfo.textContent += ` near ${landmark.name}`;
    }
  }
}

// Add User Location Marker
function addUserLocationMarker(lat, lng) {
  if (!hotelMap || !markersLayer) return;

  const userIcon = L.divIcon({
    className: "user-marker",
    html: '<div style="background: #3b82f6; color: white; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 14px; border: 3px solid white; box-shadow: 0 2px 8px rgba(0,0,0,0.4);">📍</div>',
    iconSize: [24, 24],
  });

  const userMarker = L.marker([lat, lng], { icon: userIcon }).bindPopup(
    "<strong>Your Location</strong>"
  );

  markersLayer.addLayer(userMarker);
}

// Export functions
window.initializeMap = initializeMap;
window.updateMapMarkers = updateMapMarkers;
window.addUserLocationMarker = addUserLocationMarker;
