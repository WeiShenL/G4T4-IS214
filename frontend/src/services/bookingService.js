// bookingService.js

export async function submitBooking(payload) {
    try {
      const response = await fetch("http://localhost:5005/booking", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(payload)
      });
  
      if (!response.ok) {
        throw new Error("Failed to submit booking");
      }
  
      return await response.json();
    } catch (error) {
      console.error("Booking submission failed:", error);
      return { error: error.message };
    }
  }
  