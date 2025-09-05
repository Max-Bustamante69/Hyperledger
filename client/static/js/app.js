class RoomReservationApp {
  constructor(userId, userType) {
    this.userId = userId;
    this.userType = userType;
    this.socket = null;
    this.calendar = null;
    this.reservations = [];
    this.rooms = [];

    this.init();
  }

  init() {
    this.initSocket();
    this.initCalendar();
    this.loadRooms();
    this.loadReservations();
    this.setupEventListeners();
    this.generateTimeOptions();
    this.setDefaultDate();
    this.loadNetworkInfo();

    // Set up periodic refresh
    setInterval(() => {
      this.loadReservations();
    }, 30000); // Refresh every 30 seconds
  }

  initSocket() {
    this.socket = io();

    this.socket.on("connect", () => {
      console.log("Connected to server");
      this.updateConnectionStatus(true);
      this.socket.emit("join_room", {
        room: "general",
        user_id: this.userId,
      });
    });

    this.socket.on("disconnect", () => {
      console.log("Disconnected from server");
      this.updateConnectionStatus(false);
    });

    this.socket.on("reservation_update", (data) => {
      this.handleReservationUpdate(data);
    });

    this.socket.on("network_info", (data) => {
      this.updateNetworkInfo(data);
    });

    this.socket.on("reservations_data", (data) => {
      if (data.success) {
        this.reservations = data.data;
        this.updateCalendar();
        this.updateReservationLists();
      }
    });

    this.socket.on("error", (data) => {
      this.showAlert("error", data.message);
    });
  }

  initCalendar() {
    const calendarEl = document.getElementById("calendar-container");

    this.calendar = new FullCalendar.Calendar(calendarEl, {
      initialView: "dayGridMonth",
      headerToolbar: {
        left: "",
        center: "title",
        right: "",
      },
      height: "auto",
      events: [],
      eventClick: (info) => {
        this.showReservationDetails(info.event.extendedProps.reservation);
      },
      eventClassNames: (arg) => {
        const reservation = arg.event.extendedProps.reservation;
        let classes = [`fc-event-${reservation.userType}`];
        if (reservation.status === "cancelled") {
          classes.push("fc-event-cancelled");
        }
        return classes;
      },
    });

    this.calendar.render();

    // Calendar navigation
    document.getElementById("prev-btn").addEventListener("click", () => {
      this.calendar.prev();
    });

    document.getElementById("today-btn").addEventListener("click", () => {
      this.calendar.today();
    });

    document.getElementById("next-btn").addEventListener("click", () => {
      this.calendar.next();
    });
  }

  setupEventListeners() {
    // Reservation form
    document
      .getElementById("reservationForm")
      .addEventListener("submit", (e) => {
        e.preventDefault();
        this.makeReservation();
      });

    // Block selection change
    document.getElementById("block").addEventListener("change", (e) => {
      this.updateRoomOptions(e.target.value);
    });

    // Tab switches
    document.querySelectorAll('[data-bs-toggle="tab"]').forEach((tab) => {
      tab.addEventListener("shown.bs.tab", (e) => {
        const target = e.target.getAttribute("data-bs-target");
        if (target === "#my-reservations") {
          this.loadUserReservations();
        } else if (target === "#all-reservations") {
          this.loadAllReservations();
        }
      });
    });

    // Availability check
    document
      .getElementById("check-availability")
      ?.addEventListener("click", () => {
        this.checkRoomAvailability();
      });

    // Filter controls (professor only)
    if (this.userType === "professor") {
      document
        .getElementById("apply-filters")
        ?.addEventListener("click", () => {
          this.applyFilters();
        });

      document.getElementById("refresh-all")?.addEventListener("click", () => {
        this.loadAllReservations();
      });
    }

    // Cancel reservation button
    document
      .getElementById("cancel-reservation-btn")
      .addEventListener("click", () => {
        this.cancelCurrentReservation();
      });
  }

  generateTimeOptions() {
    const timeSelect = document.getElementById("time");
    timeSelect.innerHTML = '<option value="">Select time</option>';

    for (let hour = 6; hour < 23; hour++) {
      for (let minute = 0; minute < 60; minute += 30) {
        const timeStr = `${hour.toString().padStart(2, "0")}:${minute
          .toString()
          .padStart(2, "0")}`;
        const option = document.createElement("option");
        option.value = timeStr;
        option.textContent = timeStr;
        timeSelect.appendChild(option);
      }
    }
  }

  setDefaultDate() {
    const today = new Date();
    const dateStr = today.toISOString().split("T")[0];
    document.getElementById("date").value = dateStr;

    // Set availability check date
    if (document.getElementById("availability-date")) {
      document.getElementById("availability-date").value = dateStr;
    }
  }

  async loadRooms() {
    try {
      const response = await fetch("/api/rooms");
      const data = await response.json();

      if (data.success) {
        this.rooms = data.data;
        this.updateRoomOptions("33"); // Default to block 33
      }
    } catch (error) {
      console.error("Error loading rooms:", error);
    }
  }

  updateRoomOptions(block) {
    const roomSelect = document.getElementById("room");
    roomSelect.innerHTML = '<option value="">Select a room</option>';

    const blockRooms = this.rooms.filter((room) => room.block === block);
    blockRooms.forEach((room) => {
      const option = document.createElement("option");
      option.value = room.number;
      option.textContent = room.full_name;
      roomSelect.appendChild(option);
    });
  }

  async loadReservations() {
    try {
      const response = await fetch("/api/reservations");
      const data = await response.json();

      if (data.success) {
        this.reservations = data.data;
        this.updateCalendar();
        this.updateReservationLists();
      }
    } catch (error) {
      console.error("Error loading reservations:", error);
    }
  }

  async loadUserReservations() {
    try {
      const response = await fetch(`/api/reservations?user_id=${this.userId}`);
      const data = await response.json();

      if (data.success) {
        this.displayReservations(data.data, "my-reservations-list");
      }
    } catch (error) {
      console.error("Error loading user reservations:", error);
    }
  }

  async loadAllReservations() {
    try {
      const response = await fetch("/api/reservations");
      const data = await response.json();

      if (data.success) {
        this.displayReservations(data.data, "all-reservations-list");
      }
    } catch (error) {
      console.error("Error loading all reservations:", error);
    }
  }

  async loadNetworkInfo() {
    try {
      const response = await fetch("/api/network-info");
      const data = await response.json();

      if (data.success) {
        this.updateNetworkInfo(data);
      }
    } catch (error) {
      console.error("Error loading network info:", error);
    }
  }

  updateCalendar() {
    const events = this.reservations
      .filter(
        (reservation) =>
          reservation.status === "active" || reservation.status === "pending"
      )
      .map((reservation) => {
        // Different colors for pending vs active reservations
        let backgroundColor, borderColor, title;

        if (reservation.status === "pending") {
          // Pending reservations (not yet mined)
          backgroundColor =
            reservation.userType === "professor" ? "#ffc107" : "#17a2b8";
          borderColor =
            reservation.userType === "professor" ? "#e0a800" : "#138496";
          title = `${reservation.roomNumber} - ${reservation.userID} (PENDING)`;
        } else {
          // Active reservations (committed to blockchain)
          backgroundColor =
            reservation.userType === "professor" ? "#28a745" : "#007bff";
          borderColor =
            reservation.userType === "professor" ? "#1e7e34" : "#0056b3";
          title = `${reservation.roomNumber} - ${reservation.userID}`;
        }

        return {
          id: reservation.id,
          title: title,
          start: reservation.startTime,
          end: reservation.endTime,
          backgroundColor: backgroundColor,
          borderColor: borderColor,
          extendedProps: {
            reservation: reservation,
          },
        };
      });

    this.calendar.removeAllEvents();
    this.calendar.addEventSource(events);
  }

  updateReservationLists() {
    // Update my reservations if tab is active
    const myReservationsTab = document.querySelector("#my-reservations-tab");
    if (myReservationsTab && myReservationsTab.classList.contains("active")) {
      this.loadUserReservations();
    }

    // Update all reservations if tab is active (professor only)
    if (this.userType === "professor") {
      const allReservationsTab = document.querySelector(
        "#all-reservations-tab"
      );
      if (
        allReservationsTab &&
        allReservationsTab.classList.contains("active")
      ) {
        this.loadAllReservations();
      }
    }
  }

  displayReservations(reservations, containerId) {
    const container = document.getElementById(containerId);

    if (reservations.length === 0) {
      container.innerHTML = `
                <div class="text-center text-muted">
                    <i class="fas fa-calendar-times fa-3x mb-3"></i>
                    <p>No reservations found</p>
                </div>
            `;
      return;
    }

    const html = reservations
      .map((reservation) => {
        const startTime = new Date(reservation.startTime);
        const endTime = new Date(reservation.endTime);
        const statusClass =
          reservation.status === "active" ? "active" : "cancelled";
        const userTypeClass = reservation.userType;

        return `
                <div class="reservation-item ${userTypeClass} ${
          reservation.status
        }" data-reservation-id="${reservation.id}">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <div>
                            <h6 class="mb-1">
                                Block ${reservation.block} - Room ${
          reservation.roomNumber
        }
                                <span class="reservation-status ${statusClass}">${
          reservation.status
        }</span>
                            </h6>
                            <div class="reservation-meta">
                                <i class="fas fa-user me-1"></i>${
                                  reservation.userID
                                } (${reservation.userType})
                            </div>
                        </div>
                        <div class="text-end">
                            <button class="btn btn-sm btn-outline-primary" onclick="window.roomReservationApp.showReservationDetails('${
                              reservation.id
                            }')">
                                <i class="fas fa-eye"></i>
                            </button>
                            ${
                              this.canCancelReservation(reservation)
                                ? `
                                <button class="btn btn-sm btn-outline-danger ms-1" onclick="window.roomReservationApp.cancelReservation('${reservation.id}')">
                                    <i class="fas fa-times"></i>
                                </button>
                            `
                                : ""
                            }
                        </div>
                    </div>
                    <div class="reservation-meta">
                        <i class="fas fa-clock me-1"></i>
                        ${startTime.toLocaleDateString()} ${startTime.toLocaleTimeString(
          [],
          { hour: "2-digit", minute: "2-digit" }
        )} - 
                        ${endTime.toLocaleTimeString([], {
                          hour: "2-digit",
                          minute: "2-digit",
                        })}
                        (${reservation.duration} min)
                    </div>
                </div>
            `;
      })
      .join("");

    container.innerHTML = html;
  }

  canCancelReservation(reservation) {
    if (reservation.status === "cancelled") return false;
    if (this.userType === "professor") return true;
    return reservation.userID === this.userId;
  }

  async makeReservation() {
    const formData = new FormData(document.getElementById("reservationForm"));
    const data = {
      room_number: formData.get("room"),
      block: formData.get("block"),
      user_id: this.userId,
      start_time: `${formData.get("date")} ${formData.get("time")}`,
      duration: parseInt(formData.get("duration")),
    };

    if (!data.room_number || !data.block || !data.start_time) {
      this.showAlert("warning", "Please fill in all required fields");
      return;
    }

    try {
      const response = await fetch("/api/reservations", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });

      const result = await response.json();

      if (result.success) {
        this.showAlert("success", "Reservation created successfully!");
        document.getElementById("reservationForm").reset();
        this.setDefaultDate();
        this.loadReservations();
      } else {
        // Check if it's a conflict and user is professor
        if (
          result.error.includes("already reserved") &&
          this.userType === "professor"
        ) {
          this.handleReservationConflict(data);
        } else {
          this.showAlert("error", result.error);
        }
      }
    } catch (error) {
      console.error("Error making reservation:", error);
      this.showAlert("error", "Failed to make reservation");
    }
  }

  handleReservationConflict(reservationData) {
    // Show override modal for professors
    const modal = new bootstrap.Modal(document.getElementById("overrideModal"));
    modal.show();

    // Store the reservation data for later use
    this.pendingReservation = reservationData;
  }

  async cancelReservation(reservationId) {
    if (!confirm("Are you sure you want to cancel this reservation?")) {
      return;
    }

    try {
      const response = await fetch(`/api/reservations/${reservationId}`, {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          cancelled_by_user_id: this.userId,
        }),
      });

      const result = await response.json();

      if (result.success) {
        this.showAlert("success", "Reservation cancelled successfully!");
        this.loadReservations();
      } else {
        this.showAlert("error", result.error);
      }
    } catch (error) {
      console.error("Error cancelling reservation:", error);
      this.showAlert("error", "Failed to cancel reservation");
    }
  }

  async showReservationDetails(reservationId) {
    let reservation;

    if (typeof reservationId === "string") {
      // Find reservation by ID
      reservation = this.reservations.find((r) => r.id === reservationId);
    } else {
      // Direct reservation object
      reservation = reservationId;
    }

    if (!reservation) {
      this.showAlert("error", "Reservation not found");
      return;
    }

    const startTime = new Date(reservation.startTime);
    const endTime = new Date(reservation.endTime);

    const detailsHtml = `
            <div class="row">
                <div class="col-sm-6"><strong>Reservation ID:</strong></div>
                <div class="col-sm-6">${reservation.id}</div>
            </div>
            <div class="row mt-2">
                <div class="col-sm-6"><strong>Room:</strong></div>
                <div class="col-sm-6">Block ${reservation.block} - Room ${
      reservation.roomNumber
    }</div>
            </div>
            <div class="row mt-2">
                <div class="col-sm-6"><strong>User:</strong></div>
                <div class="col-sm-6">${reservation.userID} (${
      reservation.userType
    })</div>
            </div>
            <div class="row mt-2">
                <div class="col-sm-6"><strong>Date:</strong></div>
                <div class="col-sm-6">${startTime.toLocaleDateString()}</div>
            </div>
            <div class="row mt-2">
                <div class="col-sm-6"><strong>Time:</strong></div>
                <div class="col-sm-6">${startTime.toLocaleTimeString([], {
                  hour: "2-digit",
                  minute: "2-digit",
                })} - ${endTime.toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    })}</div>
            </div>
            <div class="row mt-2">
                <div class="col-sm-6"><strong>Duration:</strong></div>
                <div class="col-sm-6">${reservation.duration} minutes</div>
            </div>
            <div class="row mt-2">
                <div class="col-sm-6"><strong>Status:</strong></div>
                <div class="col-sm-6">
                    <span class="reservation-status ${reservation.status}">${
      reservation.status
    }</span>
                </div>
            </div>
            ${
              reservation.cancelledBy
                ? `
                <div class="row mt-2">
                    <div class="col-sm-6"><strong>Cancelled By:</strong></div>
                    <div class="col-sm-6">${reservation.cancelledBy}</div>
                </div>
            `
                : ""
            }
        `;

    document.getElementById("reservation-details").innerHTML = detailsHtml;

    // Show/hide cancel button
    const cancelBtn = document.getElementById("cancel-reservation-btn");
    if (this.canCancelReservation(reservation)) {
      cancelBtn.style.display = "block";
      cancelBtn.onclick = () => {
        bootstrap.Modal.getInstance(
          document.getElementById("reservationModal")
        ).hide();
        this.cancelReservation(reservation.id);
      };
    } else {
      cancelBtn.style.display = "none";
    }

    const modal = new bootstrap.Modal(
      document.getElementById("reservationModal")
    );
    modal.show();
  }

  async checkRoomAvailability() {
    const date = document.getElementById("availability-date").value;
    const startTime = document.getElementById("availability-start-time").value;
    const endTime = document.getElementById("availability-end-time").value;

    if (!date || !startTime || !endTime) {
      this.showAlert("warning", "Please fill in all fields");
      return;
    }

    const startDateTime = `${date} ${startTime}`;
    const endDateTime = `${date} ${endTime}`;

    try {
      const response = await fetch(
        `/api/available-rooms?start_time=${encodeURIComponent(
          startDateTime
        )}&end_time=${encodeURIComponent(endDateTime)}`
      );
      const data = await response.json();

      if (data.success) {
        this.displayAvailableRooms(data.data);
      } else {
        this.showAlert("error", data.error);
      }
    } catch (error) {
      console.error("Error checking availability:", error);
      this.showAlert("error", "Failed to check room availability");
    }
  }

  displayAvailableRooms(rooms) {
    const container = document.getElementById("available-rooms-list");

    if (rooms.length === 0) {
      container.innerHTML = `
                <div class="text-center text-muted">
                    <i class="fas fa-times-circle fa-3x mb-3"></i>
                    <p>No rooms available for the selected time period</p>
                </div>
            `;
      return;
    }

    const html = `
            <div class="room-grid">
                ${rooms
                  .map(
                    (room) => `
                    <div class="room-card available" onclick="window.roomReservationApp.selectRoom('${room.number}', '${room.block}')">
                        <div class="room-number">Room ${room.number}</div>
                        <div class="room-status available">Block ${room.block}</div>
                        <div class="room-status available">Available</div>
                    </div>
                `
                  )
                  .join("")}
            </div>
        `;

    container.innerHTML = html;
  }

  selectRoom(roomNumber, block) {
    // Fill the reservation form with selected room
    document.getElementById("block").value = block;
    this.updateRoomOptions(block);
    setTimeout(() => {
      document.getElementById("room").value = roomNumber;
    }, 100);

    // Switch to the calendar tab
    const calendarTab = document.getElementById("calendar-tab");
    calendarTab.click();

    this.showAlert("info", `Selected Room ${roomNumber} in Block ${block}`);
  }

  applyFilters() {
    // This would implement filtering for the all reservations view
    // For now, just reload all reservations
    this.loadAllReservations();
  }

  handleReservationUpdate(data) {
    console.log("Reservation update received:", data);

    if (data.type === "new_reservation") {
      this.showAlert(
        "info",
        `New reservation made for Room ${data.data.room_number} in Block ${data.data.block}`
      );
    } else if (data.type === "cancelled_reservation") {
      this.showAlert(
        "info",
        `Reservation ${data.data.reservation_id} has been cancelled`
      );
    }

    // Reload reservations to get the latest data
    this.loadReservations();
  }

  updateConnectionStatus(connected) {
    const indicator = document.querySelector(".status-indicator");
    if (indicator) {
      indicator.className = `status-indicator ${
        connected ? "connected" : "disconnected"
      }`;
    }
  }

  updateNetworkInfo(data) {
    if (!data.success || !data.peers) return;

    const peerList = document.getElementById("peer-list");
    const html = data.peers
      .map(
        (peer) => `
            <div class="peer-item">
                <div class="peer-name">${peer.name}</div>
                <div class="peer-block">Block ${peer.block}</div>
            </div>
        `
      )
      .join("");

    peerList.innerHTML = html;
  }

  showAlert(type, message) {
    // Create alert element
    const alertClass = type === "error" ? "danger" : type;
    const alertHtml = `
            <div class="alert alert-${alertClass} alert-dismissible fade show" role="alert">
                <i class="fas fa-${this.getAlertIcon(type)} me-2"></i>
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;

    // Find or create alert container
    let alertContainer = document.getElementById("alert-container");
    if (!alertContainer) {
      alertContainer = document.createElement("div");
      alertContainer.id = "alert-container";
      alertContainer.className = "position-fixed top-0 end-0 p-3";
      alertContainer.style.zIndex = "9999";
      document.body.appendChild(alertContainer);
    }

    // Add alert
    const alertElement = document.createElement("div");
    alertElement.innerHTML = alertHtml;
    alertContainer.appendChild(alertElement.firstElementChild);

    // Auto-dismiss after 5 seconds
    setTimeout(() => {
      const alert = alertContainer.querySelector(".alert");
      if (alert) {
        const bsAlert = new bootstrap.Alert(alert);
        bsAlert.close();
      }
    }, 5000);
  }

  getAlertIcon(type) {
    switch (type) {
      case "success":
        return "check-circle";
      case "error":
        return "exclamation-circle";
      case "warning":
        return "exclamation-triangle";
      case "info":
        return "info-circle";
      default:
        return "info-circle";
    }
  }
}
