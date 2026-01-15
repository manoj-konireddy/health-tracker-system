// Health Tracker JavaScript
// Placeholder for future JavaScript functionality

document.addEventListener("DOMContentLoaded", () => {
  console.log("Health Tracker loaded successfully")

  // Form validation helper
  const forms = document.querySelectorAll("form")
  forms.forEach((form) => {
    form.addEventListener("submit", (e) => {
      // Add custom validation here if needed
      console.log("Form submitted:", form.id)
    })
  })
})

// Function to format date inputs
function formatDateInput(inputElement) {
  if (inputElement.type === "date") {
    const today = new Date().toISOString().split("T")[0]
    inputElement.value = today
  }
}

// Initialize date inputs
document.addEventListener("DOMContentLoaded", () => {
  const dateInputs = document.querySelectorAll('input[type="date"]')
  dateInputs.forEach((input) => {
    if (!input.value) {
      const today = new Date().toISOString().split("T")[0]
      input.value = today
    }
  })
})
