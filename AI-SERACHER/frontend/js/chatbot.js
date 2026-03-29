// Chatbot logic

// DOM Elements
const chatForm = document.getElementById("chatForm");
const chatInput = document.getElementById("chatInput");
const chatMessages = document.getElementById("chatMessages");
const typingIndicator = document.getElementById("typingIndicator");
const quickActionsContainer = document.getElementById("quickActions");
let quickActionBtns = [];

// Initialize Chatbot
document.addEventListener("DOMContentLoaded", () => {
  // Chat form submission
  chatForm.addEventListener("submit", handleChatSubmit);

  // Initialize quick actions with default city
  initQuickActions();
});

// Initialize quick-action buttons (creates Cheap / Luxury / Top rated for given city)
function initQuickActions(city) {
  const defaultCity =
    city ||
    (window.AppState &&
      window.AppState.lastSearchContext &&
      window.AppState.lastSearchContext.city) ||
    "Dubai";
  
  if (!quickActionsContainer) return;
  quickActionsContainer.innerHTML = "";

  const specs = [
    { label: `Cheap in ${defaultCity}`, emoji: "💰", filter: "cheap" },
    { label: `Luxury in ${defaultCity}`, emoji: "⭐", filter: "luxury" },
    { label: `Top rated in ${defaultCity}`, emoji: "🏆", filter: "toprated" },
  ];

  specs.forEach((s) => {
    const btn = document.createElement("button");
    btn.className = "quick-action-btn";
    btn.setAttribute("data-query", s.label);
    btn.setAttribute("data-filter", s.filter);
    btn.innerText = `${s.emoji} ${s.label}`;
    btn.addEventListener("click", (event) => {
      event.preventDefault();
      if (!window.AppState) window.AppState = {};
      window.AppState.quickFilter = s.filter;
      chatInput.value = s.label;
      handleChatSubmit(new Event("submit"));
    });
    quickActionsContainer.appendChild(btn);
  });

  quickActionBtns = document.querySelectorAll(".quick-action-btn");
}

// Try to extract a city name from user input
function extractCityFromInput(text) {
  if (!text) return null;

  // List of price/quality keywords that should NOT trigger button updates
  const priceKeywords = ["cheap", "budget", "affordable", "luxury", "expensive", "5 star", "4 star", "3 star", "top rated", "best", "premium"];
  
  // Check if the input is ONLY a price keyword - don't update buttons
  const cleanedInput = text.trim().toLowerCase();
  if (priceKeywords.some(keyword => cleanedInput === keyword || cleanedInput.includes(keyword))) {
    // Only return city if there's ALSO a city mentioned with "in"
    const inMatch = text.match(/\bin\s+([A-Za-z\u00C0-\u017F\s'-]+)$/i);
    if (inMatch) return inMatch[1].trim();
    // If it's just a price keyword without "in <city>", don't extract any city
    return null;
  }

  // Match 'in <city>' pattern - this is the primary way to detect cities
  const inMatch = text.match(/\bin\s+([A-Za-z\u00C0-\u017F\s'-]+)$/i);
  if (inMatch) return inMatch[1].trim();

  // If input is short (1-3 words) and letters only, treat as city name
  // But NOT if it contains price keywords
  const cleaned = text.replace(/[^\p{L}\s'-]/gu, "").trim();
  const words = cleaned.split(/\s+/).filter(Boolean);
  
  if (
    words.length >= 1 &&
    words.length <= 3 &&
    /^[\p{L}\s'-]+$/u.test(cleaned) &&
    !priceKeywords.some(keyword => cleaned.toLowerCase().includes(keyword))
  ) {
    return cleaned;
  }
  
  return null;
}

// Handle Chat Submit
async function handleChatSubmit(e) {
  e.preventDefault();

  const message = chatInput.value.trim();
  if (!message) return;

  // If the submitted message contains a city, update quick-action buttons now
  try {
    const cityFromMessage = extractCityFromInput(message);
    if (cityFromMessage) {
      initQuickActions(cityFromMessage);
    }
  } catch (err) {
    console.warn("City extraction failed:", err);
  }

  // Add user message to chat
  addUserMessage(message);

  // Clear input
  chatInput.value = "";

  // Show typing indicator
  showTypingIndicator();

  // Send to API with conversation context
  try {
    // Add message to conversation history
    window.AppState.addMessage("user", message);

    const response = await fetch(`${window.CONFIG.API_BASE_URL}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: message,
        user_location: window.AppState.userLocation,
        // Send last search context to backend so it can remember
        last_search_context: window.AppState.getLastSearchContext(),
        conversation_history: window.AppState.conversationHistory.slice(-3), // Last 3 messages
      }),
    });

    const data = await response.json();
    console.log("API Response:", data);

    // Hide typing indicator
    hideTypingIndicator();

    // Handle response
    handleChatResponse(data);
  } catch (error) {
    hideTypingIndicator();
    addBotMessage(
      "Sorry, I encountered an error. Please make sure the backend server is running."
    );
    console.error("Chat error:", error);
  }
}

// Handle Chat Response
function handleChatResponse(data) {
  const intent = data.intent;

  if (intent === "greeting" || intent === "help" || intent === "unknown") {
    // Simple text response - add to conversation history
    window.AppState.addMessage("bot", data.message);
    addBotMessage(data.message);
    return;
  }

  if (intent === "search") {
    // Hotel search results
    const hotels = data.hotels || [];
    const message = data.message;
    const landmark = data.landmark;

    // Extract filters from filters_used (the parsed query)
    const filters = data.filters_used || {};
    const city = filters.city;
    const price = filters.price_preference;
    const min_rating = filters.min_rating;
    const amenities = filters.amenities || [];

    // Add message to conversation history
    window.AppState.addMessage("bot", message);

    // Add message
    addBotMessage(message);

    // Update search context for future queries
    if (
      city ||
      landmark ||
      price !== undefined ||
      amenities.length > 0 ||
      min_rating
    ) {
      console.log("Updating context with:", {
        city,
        landmark,
        price,
        amenities,
        min_rating,
      });
      window.AppState.updateSearchContext(
        city,
        landmark,
        price,
        amenities,
        min_rating
      );
      console.log("New context:", window.AppState.lastSearchContext);
    }

    // Display hotels
    if (hotels.length > 0) {
      displayHotels(hotels, landmark);

      // Update app state landmark; displayed hotels are set inside displayHotels
      window.AppState.currentLandmark = landmark;

      // Update map if visible
      if (window.AppState.mapVisible && window.updateMapMarkers) {
        window.updateMapMarkers(window.AppState.currentHotels || [], landmark);
        // Add user location marker if available
        if (window.AppState.userLocation && window.addUserLocationMarker) {
          const ul = window.AppState.userLocation;
          try {
            window.addUserLocationMarker(ul.lat, ul.lng);
          } catch (e) {
            console.warn("Could not add user location marker:", e);
          }
        }
      }
    } else {
      addBotMessage(
        "No hotels found matching your criteria. Try adjusting your search."
      );
    }
  }
}

// Add User Message
function addUserMessage(message) {
  const messageDiv = document.createElement("div");
  messageDiv.className = "message user-message";
  messageDiv.innerHTML = `
        <div class="message-avatar">👤</div>
        <div class="message-content">
            <div class="message-bubble">
                <p>${escapeHtml(message)}</p>
            </div>
        </div>
    `;

  chatMessages.appendChild(messageDiv);
  scrollToBottom();
}

// Add Bot Message
function addBotMessage(message) {
  const messageDiv = document.createElement("div");
  messageDiv.className = "message bot-message";
  messageDiv.innerHTML = `
        <div class="message-avatar">🤖</div>
        <div class="message-content">
            <div class="message-bubble">
                <p>${escapeHtml(message)}</p>
            </div>
        </div>
    `;

  chatMessages.appendChild(messageDiv);
  scrollToBottom();
}

// Display Hotels with front-end filters (cheap/luxury/toprated) and max 5 results
function displayHotels(hotels, landmark) {
  if (!Array.isArray(hotels)) hotels = [];

  // Determine quick filter from AppState (set by quick-action buttons only)
  // Don't use lastSearchContext for auto-filtering - only explicit quickFilter button clicks
  const quickFilter = (window.AppState && window.AppState.quickFilter) || null;

  // Copy and apply filtering
  let filtered = hotels.slice();

  if (
    quickFilter === "cheap" ||
    (typeof quickFilter === "string" && quickFilter.toLowerCase() === "cheap")
  ) {
    filtered = filtered.filter((h) => {
      const p = Number(h.price_per_night);
      return !isNaN(p) && p <= 400;
    });
  } else if (
    quickFilter === "luxury" ||
    (typeof quickFilter === "string" && quickFilter.toLowerCase() === "luxury")
  ) {
    filtered = filtered.filter((h) => {
      const p = Number(h.price_per_night);
      return !isNaN(p) && p > 400;
    });
  } else if (
    quickFilter === "toprated" ||
    (typeof quickFilter === "string" && quickFilter.toLowerCase() === "toprated")
  ) {
    filtered = filtered.filter((h) => {
      const sr = Number(h.star_rating);
      return !isNaN(sr) && Math.round(sr) >= 5;
    });
  }

  // Limit to max 15 hotels (changed from 5 to show all found hotels)
  filtered = filtered.slice(0, 15);

  if (filtered.length === 0) {
    addBotMessage("No hotels found matching your selected filter.");
    // Clear quick filter after use so subsequent searches act normally
    if (window.AppState) window.AppState.quickFilter = null;
    return;
  }

  // Build HTML for filtered hotels
  const messageDiv = document.createElement("div");
  messageDiv.className = "message bot-message";

  let hotelsHTML = filtered
    .map((hotel, index) => {
      // Parse amenities if it's a JSON string
      let amenities = hotel.amenities;
      if (typeof amenities === "string") {
        try {
          amenities = JSON.parse(amenities);
        } catch (e) {
          amenities = [];
        }
      }
      if (!Array.isArray(amenities)) {
        amenities = [];
      }

      return `
        <div class="hotel-card" onclick="window.showHotelDetails(${hotel.id})">
            <div class="hotel-card-header">
                <div>
                    <div class="hotel-name">${escapeHtml(hotel.name)}</div>
                    <div class="hotel-rating">
                        ${"⭐".repeat(Math.floor(hotel.star_rating || 0))} ${
        hotel.star_rating || ""
      }
                    </div>
                </div>
                <div class="hotel-score">${
                  hotel.recommendation_score || "N/A"
                }/100</div>
            </div>
            
      <div class="hotel-info">
        <div class="hotel-info-item">
          <span>📍</span>
          <span>${escapeHtml(
            hotel.address || hotel.city || "Location unknown"
          )}</span>
        </div>
        <div class="hotel-info-item">
          <span>💰</span>
          <span>${
            hotel.price_per_night
              ? hotel.price_per_night + " SAR/night"
              : "Price N/A"
          }</span>
        </div>
        ${
          hotel.distance
            ? `
          <div class="hotel-info-item">
            <span>🚗</span>
            <span>${hotel.distance}</span>
          </div>
        `
            : ""
        }
        ${
          hotel.phone
            ? `
          <div class="hotel-info-item">
            <span>📞</span>
            <span>${escapeHtml(hotel.phone)}</span>
          </div>
        `
            : ""
        }
        ${
          hotel.website
            ? `
          <div class="hotel-info-item">
            <span>🌐</span>
            <span><a href="${escapeHtml(
              hotel.website
            )}" target="_blank">Website</a></span>
          </div>
        `
            : ""
        }
      </div>
            
            <div class="hotel-amenities">
                ${amenities
                  .slice(0, 4)
                  .map(
                    (amenity) =>
                      `<span class="amenity-tag">${escapeHtml(amenity)}</span>`
                  )
                  .join("")}
                ${
                  amenities.length > 4
                    ? `<span class="amenity-tag">+${
                        amenities.length - 4
                      } more</span>`
                    : ""
                }
            </div>
            
      <div class="hotel-explanation">
        ${escapeHtml(hotel.explanation || "")}
      </div>
      ${
        hotel.score_breakdown
          ? `
      
      `
          : ""
      }
        </div>
    `;
    })
    .join("");

  messageDiv.innerHTML = `
        <div class="message-avatar">🤖</div>
        <div class="message-content">
            ${hotelsHTML}
        </div>
    `;

  chatMessages.appendChild(messageDiv);
  scrollToBottom();

  // Update app state with displayed hotels and clear quickFilter
  if (!window.AppState) window.AppState = {};
  window.AppState.currentHotels = filtered;
  window.AppState.quickFilter = null;
}

// Typing Indicator
function showTypingIndicator() {
  typingIndicator.style.display = "flex";
  scrollToBottom();
}

function hideTypingIndicator() {
  typingIndicator.style.display = "none";
}

// Scroll to Bottom
function scrollToBottom() {
  setTimeout(() => {
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }, 100);
}

// Escape HTML
function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

// Export functions
window.addBotMessage = addBotMessage;
window.addUserMessage = addUserMessage;
// Handle chatbot interactions and message handling
