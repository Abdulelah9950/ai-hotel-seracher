// Main JavaScript file
// Main application logic

// Configuration
const CONFIG = {
  API_BASE_URL: "/api", // Relative URL since frontend and backend are on same server
  DEFAULT_CITY: "Dubai",
  MAP_CENTER: [20, 0], // World view (centered on equator)
  MAP_ZOOM: 2, // Zoom level 2 shows multiple continents
};

// App State with Conversation Memory
const AppState = {
  currentHotels: [],
  currentLandmark: null,
  mapVisible: false,
  userLocation: null,
  
  // Conversation Memoryy
  conversationHistory: [],
  lastSearchContext: {
    city: null,
    landmark: null,
    pricePreference: null,
    amenities: [],
    minRating: null
  },
  
  // Update conversation history
  addMessage(role, message, parsed_query = null) {
    this.conversationHistory.push({
      role: role,
      message: message,
      timestamp: new Date(),
      parsed_query: parsed_query
    });
    
    // Keep last 10 messages
    if (this.conversationHistory.length > 10) {
      this.conversationHistory.shift();
    }
  },
  
  // Get last search context for "remember" functionality
  getLastSearchContext() {
    return this.lastSearchContext;
  },
  
  // Update search context
  updateSearchContext(city, landmark, pricePreference, amenities, minRating) {
    // Update fields if they have values (not null/undefined)
    if (city !== null && city !== undefined) {
      this.lastSearchContext.city = city;
    }
    if (landmark !== null && landmark !== undefined) {
      this.lastSearchContext.landmark = landmark;
    }
    // Always update pricePreference, even if null (to clear previous values)
    if (pricePreference !== undefined) {
      this.lastSearchContext.pricePreference = pricePreference;
    }
    if (amenities && Array.isArray(amenities) && amenities.length > 0) {
      this.lastSearchContext.amenities = amenities;
    }
    if (minRating !== null && minRating !== undefined) {
      this.lastSearchContext.minRating = minRating;
    }
    console.log("Updated search context:", this.lastSearchContext);
  }
};

// DOM Elements
const elements = {
  toggleMapBtn: document.getElementById("toggleMapBtn"),
  mapPanel: document.getElementById("mapPanel"),
  chatPanel: document.querySelector(".chat-panel"),
  hotelModal: document.getElementById("hotelModal"),
  modalClose: document.querySelector(".modal-close"),
  hotelDetails: document.getElementById("hotelDetails"),
  loadingOverlay: document.getElementById("loadingOverlay"),
};

// Initialize App
document.addEventListener("DOMContentLoaded", () => {
  console.log("🚀 AI Hotel Finder initialized");

  // Initialize components
  initializeEventListeners();

  // Try to get user location
  getUserLocation();

  // Check API health
  checkAPIHealth();
});

// Event Listeners
function initializeEventListeners() {
  // Toggle Map
  elements.toggleMapBtn.addEventListener("click", toggleMap);

  // Close Modal
  elements.modalClose.addEventListener("click", closeModal);

  // Close modal on outside click
  elements.hotelModal.addEventListener("click", (e) => {
    if (e.target === elements.hotelModal) {
      closeModal();
    }
  });
}

// Toggle Map Visibility
function toggleMap() {
  AppState.mapVisible = !AppState.mapVisible;

  if (AppState.mapVisible) {
    elements.mapPanel.style.display = "flex";
    elements.chatPanel.classList.add("with-map");
    elements.toggleMapBtn.innerHTML = "<span>🗺️</span> Hide Map";

    // Initialize map on first show
    if (!window.hotelMap && window.initializeMap) {
      setTimeout(() => {
        window.initializeMap();
        console.log("✅ Map initialized on first show");
        
        // If hotels already exist, display them on the map
        if (AppState.currentHotels.length > 0 && window.updateMapMarkers) {
          window.updateMapMarkers(AppState.currentHotels, AppState.currentLandmark);
          console.log("✅ Current hotels rendered on map");
        }
        
        // Add user location marker if available
        if (AppState.userLocation && window.addUserLocationMarker) {
          window.addUserLocationMarker(AppState.userLocation.lat, AppState.userLocation.lng);
          console.log("✅ User location marker added");
        }
      }, 50);
    } else if (window.hotelMap) {
      // Refresh map size if already initialized
      setTimeout(() => {
        window.hotelMap.invalidateSize();
        
        // If hotels exist, update markers
        if (AppState.currentHotels.length > 0 && window.updateMapMarkers) {
          window.updateMapMarkers(AppState.currentHotels, AppState.currentLandmark);
          console.log("✅ Map size refreshed and hotels updated");
        }
        
        // Add user location marker if available
        if (AppState.userLocation && window.addUserLocationMarker) {
          window.addUserLocationMarker(AppState.userLocation.lat, AppState.userLocation.lng);
          console.log("✅ User location marker added");
        }
      }, 50);
    }
  } else {
    elements.mapPanel.style.display = "none";
    elements.chatPanel.classList.remove("with-map");
    elements.toggleMapBtn.innerHTML = "<span>🗺️</span> Show Map";
  }
}

// Get User Location
function getUserLocation() {
  if (navigator.geolocation) {
    console.log("🔍 Requesting user location permission...");
    
    // Options: enableHighAccuracy=true for GPS, timeout=10s, maxAge=0 for fresh location
    const options = {
      enableHighAccuracy: true,
      timeout: 10000,  // 10 seconds
      maximumAge: 0    // Don't use cached location
    };
    
    navigator.geolocation.getCurrentPosition(
      (position) => {
        AppState.userLocation = {
          lat: position.coords.latitude,
          lng: position.coords.longitude,
        };
        console.log("✅ User location obtained:", AppState.userLocation);
        console.log("📍 Accuracy: " + position.coords.accuracy + " meters");
      },
      (error) => {
        console.warn("⚠️ Location error:", error.message);
        console.warn("Code:", error.code);
        
        // Show helpful message
        if (error.code === 1) {
          console.warn("Location permission denied. Try: 1) Reload page, 2) Check browser privacy settings, 3) Type city name explicitly");
        } else if (error.code === 2) {
          console.warn("Location unavailable. Try asking 'hotels in medina' instead of 'hotels near me'");
        } else if (error.code === 3) {
          console.warn("Location request timed out. Try again or type city name");
        }
      },
      options
    );
  } else {
    console.error("❌ Geolocation not supported by this browser");
  }
}

// Check API Health
async function checkAPIHealth() {
  try {
    const response = await fetch(`${CONFIG.API_BASE_URL}/health`);
    const data = await response.json();

    if (data.status === "healthy") {
      console.log("✅ API is healthy:", data.message);
    }
  } catch (error) {
    console.error("❌ API health check failed:", error);
    showNotification("Warning: Backend API may be unavailable", "warning");
  }
}

// API Functions
async function fetchHotels(city = null) {
  showLoading();

  try {
    let url = `${CONFIG.API_BASE_URL}/hotels`;
    if (city) {
      url += `?city=${encodeURIComponent(city)}`;
    }

    const response = await fetch(url);
    const data = await response.json();

    hideLoading();
    return data.hotels || [];
  } catch (error) {
    hideLoading();
    console.error("Error fetching hotels:", error);
    return [];
  }
}

async function fetchHotelDetails(hotelId) {
  showLoading();

  try {
    const url = `${CONFIG.API_BASE_URL}/hotels/${hotelId}`;
    console.log("Fetching hotel details from:", url);
    
    const response = await fetch(url);
    
    if (!response.ok) {
      console.error(`HTTP Error: ${response.status}`);
      hideLoading();
      return { error: `HTTP ${response.status}: ${response.statusText}` };
    }
    
    const data = await response.json();
    hideLoading();
    console.log("Hotel details response:", data);
    return data;
  } catch (error) {
    hideLoading();
    console.error("Error fetching hotel details:", error);
    return { error: error.message };
  }
}

async function fetchNearbyHotels(lat, lng, radius = 5, count = 15) {
  showLoading();

  try {
    const response = await fetch(`${CONFIG.API_BASE_URL}/hotels/nearby`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        latitude: lat,
        longitude: lng,
        radius_km: radius,
        count: count,
      }),
    });

    const data = await response.json();

    hideLoading();
    return data.hotels || [];
  } catch (error) {
    hideLoading();
    console.error("Error fetching nearby hotels:", error);
    return [];
  }
}

async function fetchLandmarks() {
  try {
    const response = await fetch(`${CONFIG.API_BASE_URL}/landmarks`);
    const data = await response.json();
    return data.landmarks || [];
  } catch (error) {
    console.error("Error fetching landmarks:", error);
    return [];
  }
}

// Show Hotel Details Modal
async function showHotelDetails(hotelId) {
  // If hotel exists in currentHotels (e.g., Geoapify results), use that data directly
  let hotel = null;
  let reviews = [];
  let sentiment = null;
  let summary = null;

  if (window.AppState.currentHotels && window.AppState.currentHotels.length > 0) {
    hotel = window.AppState.currentHotels.find((h) => h.id === hotelId);
  }

  if (hotel && hotel.source === "geoapify") {
    // Use the Geoapify-provided fields and synthesize some properties for the modal
    reviews = [];
    sentiment = null;
    summary = "Live data from Geoapify";
  } else if (hotel) {
    // Use the hotel from currentHotels (database source)
    reviews = [];
    sentiment = null;
    summary = "Hotel from local database";
  } else {
    // Fallback: fetch from backend (database)
    const data = await fetchHotelDetails(hotelId);

    if (!data) {
      showNotification("Could not load hotel details - server error", "error");
      console.error("Fetch returned null");
      return;
    }

    if (data.error) {
      showNotification("Could not load hotel details: " + data.error, "error");
      return;
    }

    hotel = data.hotel;
    if (!hotel) {
      showNotification("Hotel not found", "error");
      return;
    }

    reviews = data.reviews || [];
    sentiment = data.sentiment_analysis;
    summary = data.review_summary;
  }

  // Build HTML
  let html = `
        <div class="hotel-detail-header">
            <h2>${hotel.name}</h2>
            <div class="hotel-detail-rating">
                ${"⭐".repeat(Math.floor(hotel.star_rating))}
                <span>${hotel.star_rating} stars</span>
            </div>
        </div>
        
    <div class="hotel-detail-info">
      <p><strong>📍 Address:</strong> ${hotel.address || "N/A"}, ${
    hotel.city || ""
  }</p>
      <p><strong>💰 Price:</strong> ${
        hotel.price_per_night ? hotel.price_per_night + " SAR/night" : "N/A"
      }</p>
      ${hotel.phone ? `<p><strong>📞 Phone:</strong> ${hotel.phone}</p>` : ""}
      ${
        hotel.website
          ? `<p><strong>🌐 Website:</strong> <a href="${hotel.website}" target="_blank">${hotel.website}</a></p>`
          : ""
      }
      ${
        hotel.coordinates && hotel.coordinates.lat
          ? `<p><strong>📌 Coordinates:</strong> ${hotel.coordinates.lat}, ${hotel.coordinates.lng} - <a href="https://www.google.com/maps/search/?api=1&query=${hotel.coordinates.lat},${hotel.coordinates.lng}" target="_blank">Open in Maps</a></p>`
          : ""
      }
    </div>
        
        <div class="hotel-detail-amenities">
            <h3>✨ Amenities</h3>
            <div class="amenities-grid">
                ${
                  Array.isArray(hotel.amenities) && hotel.amenities.length > 0
                    ? hotel.amenities
                        .map((a) => `<span class="amenity-badge">${a}</span>`)
                        .join("")
                    : '<p>No amenities listed</p>'
                }
            </div>
        </div>
        
        <div class="hotel-description">
            <h3>📝 Description</h3>
            <p>${hotel.description || "No description available."}</p>
        </div>
    `;

  if (reviews.length > 0) {
    html += `
            <div class="hotel-reviews">
                <h3>💬 Reviews (${reviews.length})</h3>
                
                ${
                  sentiment
                    ? `
                    <div class="sentiment-summary">
                        <div class="sentiment-bar">
                            <div class="sentiment-positive" style="width: ${sentiment.distribution.positive}%">
                                ${sentiment.distribution.positive}% Positive
                            </div>
                            <div class="sentiment-neutral" style="width: ${sentiment.distribution.neutral}%">
                                ${sentiment.distribution.neutral}%
                            </div>
                            <div class="sentiment-negative" style="width: ${sentiment.distribution.negative}%">
                                ${sentiment.distribution.negative}%
                            </div>
                        </div>
                        <p class="summary-text">${summary}</p>
                    </div>
                `
                    : ""
                }
                
                <div class="reviews-list">
                    ${reviews
                      .slice(0, 5)
                      .map(
                        (review) => `
                        <div class="review-item">
                            <div class="review-header">
                                <strong>${review.guest_name}</strong>
                                <span class="review-rating">${"⭐".repeat(
                                  review.rating
                                )}</span>
                            </div>
                            <p class="review-text">${review.review_text}</p>
                        </div>
                    `
                      )
                      .join("")}
                </div>
            </div>
        `;
  }

  elements.hotelDetails.innerHTML = html;
  elements.hotelModal.style.display = "flex";
}

// Close Modal
function closeModal() {
  elements.hotelModal.style.display = "none";
}

// Loading Overlay
function showLoading() {
  elements.loadingOverlay.style.display = "flex";
}

function hideLoading() {
  elements.loadingOverlay.style.display = "none";
}

// Notification System
function showNotification(message, type = "info") {
  const notification = document.createElement("div");
  notification.className = `notification notification-${type}`;
  notification.textContent = message;
  notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        background: ${
          type === "error"
            ? "#ef4444"
            : type === "warning"
            ? "#f59e0b"
            : "#10b981"
        };
        color: white;
        border-radius: 0.5rem;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        z-index: 3000;
        animation: slideIn 0.3s ease-out;
    `;

  document.body.appendChild(notification);

  setTimeout(() => {
    notification.style.animation = "slideOut 0.3s ease-out";
    setTimeout(() => notification.remove(), 300);
  }, 3000);
}

// Utility Functions
function formatPrice(price) {
  return `${price.toLocaleString()} SAR`;
}

function formatDistance(distanceKm) {
  if (distanceKm < 1) {
    return `${Math.round(distanceKm * 1000)} meters`;
  }
  return `${distanceKm.toFixed(2)} km`;
}

// Export for use in other modules
window.AppState = AppState;
window.CONFIG = CONFIG;
window.showHotelDetails = showHotelDetails;
window.showNotification = showNotification;
window.showLoading = showLoading;
window.hideLoading = hideLoading;
