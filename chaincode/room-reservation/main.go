package main

import (
	"encoding/json"
	"fmt"
	"log"
	"strconv"
	"strings"
	"time"

	"github.com/hyperledger/fabric-contract-api-go/contractapi"
)

// SmartContract provides functions for managing room reservations
type SmartContract struct {
	contractapi.Contract
}

// Reservation represents a room reservation
type Reservation struct {
	ID          string    `json:"id"`
	RoomNumber  string    `json:"roomNumber"`
	Block       string    `json:"block"`
	Floor       string    `json:"floor"`
	UserID      string    `json:"userID"`
	UserType    string    `json:"userType"` // "student" or "professor"
	StartTime   time.Time `json:"startTime"`
	EndTime     time.Time `json:"endTime"`
	Duration    int       `json:"duration"` // in minutes: 60, 90, or 120
	Status      string    `json:"status"`   // "active" or "cancelled"
	CreatedAt   time.Time `json:"createdAt"`
	CancelledBy string    `json:"cancelledBy,omitempty"`
}

// Room represents a study room
type Room struct {
	Number string `json:"number"`
	Block  string `json:"block"`
	Floor  string `json:"floor"`
	Status string `json:"status"` // "available" or "occupied"
}

// User represents a system user
type User struct {
	ID       string `json:"id"`
	Name     string `json:"name"`
	Email    string `json:"email"`
	UserType string `json:"userType"` // "student" or "professor"
	Block    string `json:"block"`
}

// InitLedger adds initial data to the ledger
func (s *SmartContract) InitLedger(ctx contractapi.TransactionContextInterface) error {
	// Initialize rooms for blocks 33, 34, and 35
	blocks := []string{"33", "34", "35"}
	floors := []string{"1", "2", "3"}
	roomNumbers := []string{"00", "01", "02", "03", "04"}

	for _, block := range blocks {
		for _, floor := range floors {
			for _, roomNum := range roomNumbers {
				room := Room{
					Number: floor + roomNum,
					Block:  block,
					Floor:  floor,
					Status: "available",
				}

				roomJSON, err := json.Marshal(room)
				if err != nil {
					return err
				}

				err = ctx.GetStub().PutState("ROOM_"+block+"_"+floor+roomNum, roomJSON)
				if err != nil {
					return fmt.Errorf("failed to put room to world state: %v", err)
				}
			}
		}
	}

	return nil
}

// RegisterUser registers a new user in the system
func (s *SmartContract) RegisterUser(ctx contractapi.TransactionContextInterface, userID, name, email, userType, block string) error {
	// Validate user type
	if userType != "student" && userType != "professor" {
		return fmt.Errorf("invalid user type: %s. Must be 'student' or 'professor'", userType)
	}

	// Validate block
	if block != "33" && block != "34" && block != "35" {
		return fmt.Errorf("invalid block: %s. Must be '33', '34', or '35'", block)
	}

	user := User{
		ID:       userID,
		Name:     name,
		Email:    email,
		UserType: userType,
		Block:    block,
	}

	userJSON, err := json.Marshal(user)
	if err != nil {
		return err
	}

	return ctx.GetStub().PutState("USER_"+userID, userJSON)
}

// MakeReservation creates a new room reservation
func (s *SmartContract) MakeReservation(ctx contractapi.TransactionContextInterface, reservationID, roomNumber, block, userID, startTimeStr string, duration int) error {
	// Validate duration (60, 90, or 120 minutes)
	if duration != 60 && duration != 90 && duration != 120 {
		return fmt.Errorf("invalid duration: %d. Must be 60, 90, or 120 minutes", duration)
	}

	// Parse start time
	startTime, err := time.Parse("2006-01-02 15:04", startTimeStr)
	if err != nil {
		return fmt.Errorf("invalid start time format: %s. Use YYYY-MM-DD HH:MM", startTimeStr)
	}

	// Calculate end time
	endTime := startTime.Add(time.Duration(duration) * time.Minute)

	// Validate time range (06:00 to 23:00)
	if startTime.Hour() < 6 || startTime.Hour() >= 23 || endTime.Hour() > 23 {
		return fmt.Errorf("reservations are only allowed between 06:00 and 23:00")
	}

	// Get user information
	userBytes, err := ctx.GetStub().GetState("USER_" + userID)
	if err != nil {
		return fmt.Errorf("failed to read user: %v", err)
	}
	if userBytes == nil {
		return fmt.Errorf("user %s does not exist", userID)
	}

	var user User
	err = json.Unmarshal(userBytes, &user)
	if err != nil {
		return err
	}

	// Extract floor from room number
	floor := string(roomNumber[0])

	// Check if room exists
	roomKey := "ROOM_" + block + "_" + roomNumber
	roomBytes, err := ctx.GetStub().GetState(roomKey)
	if err != nil {
		return fmt.Errorf("failed to read room: %v", err)
	}
	if roomBytes == nil {
		return fmt.Errorf("room %s in block %s does not exist", roomNumber, block)
	}

	// Check for conflicting reservations
	conflict, err := s.hasConflictingReservation(ctx, roomNumber, block, startTime, endTime, "")
	if err != nil {
		return fmt.Errorf("error checking for conflicts: %v", err)
	}
	if conflict {
		return fmt.Errorf("room %s in block %s is already reserved for the requested time", roomNumber, block)
	}

	// Create reservation
	reservation := Reservation{
		ID:         reservationID,
		RoomNumber: roomNumber,
		Block:      block,
		Floor:      floor,
		UserID:     userID,
		UserType:   user.UserType,
		StartTime:  startTime,
		EndTime:    endTime,
		Duration:   duration,
		Status:     "active",
		CreatedAt:  time.Now(),
	}

	reservationJSON, err := json.Marshal(reservation)
	if err != nil {
		return err
	}

	return ctx.GetStub().PutState("RESERVATION_"+reservationID, reservationJSON)
}

// CancelReservation cancels an existing reservation
func (s *SmartContract) CancelReservation(ctx contractapi.TransactionContextInterface, reservationID, cancelledByUserID string) error {
	// Get the reservation
	reservationBytes, err := ctx.GetStub().GetState("RESERVATION_" + reservationID)
	if err != nil {
		return fmt.Errorf("failed to read reservation: %v", err)
	}
	if reservationBytes == nil {
		return fmt.Errorf("reservation %s does not exist", reservationID)
	}

	var reservation Reservation
	err = json.Unmarshal(reservationBytes, &reservation)
	if err != nil {
		return err
	}

	// Get the user who is cancelling
	userBytes, err := ctx.GetStub().GetState("USER_" + cancelledByUserID)
	if err != nil {
		return fmt.Errorf("failed to read user: %v", err)
	}
	if userBytes == nil {
		return fmt.Errorf("user %s does not exist", cancelledByUserID)
	}

	var cancellingUser User
	err = json.Unmarshal(userBytes, &cancellingUser)
	if err != nil {
		return err
	}

	// Check permissions: professors can cancel any reservation, students can only cancel their own
	if cancellingUser.UserType == "student" && reservation.UserID != cancelledByUserID {
		return fmt.Errorf("students can only cancel their own reservations")
	}

	// Check if reservation is already cancelled
	if reservation.Status == "cancelled" {
		return fmt.Errorf("reservation %s is already cancelled", reservationID)
	}

	// Update reservation status
	reservation.Status = "cancelled"
	reservation.CancelledBy = cancelledByUserID

	reservationJSON, err := json.Marshal(reservation)
	if err != nil {
		return err
	}

	return ctx.GetStub().PutState("RESERVATION_"+reservationID, reservationJSON)
}

// GetReservation returns a specific reservation
func (s *SmartContract) GetReservation(ctx contractapi.TransactionContextInterface, reservationID string) (*Reservation, error) {
	reservationBytes, err := ctx.GetStub().GetState("RESERVATION_" + reservationID)
	if err != nil {
		return nil, fmt.Errorf("failed to read reservation: %v", err)
	}
	if reservationBytes == nil {
		return nil, fmt.Errorf("reservation %s does not exist", reservationID)
	}

	var reservation Reservation
	err = json.Unmarshal(reservationBytes, &reservation)
	if err != nil {
		return nil, err
	}

	return &reservation, nil
}

// GetAllReservations returns all reservations
func (s *SmartContract) GetAllReservations(ctx contractapi.TransactionContextInterface) ([]*Reservation, error) {
	resultsIterator, err := ctx.GetStub().GetStateByRange("RESERVATION_", "RESERVATION_~")
	if err != nil {
		return nil, err
	}
	defer resultsIterator.Close()

	var reservations []*Reservation
	for resultsIterator.HasNext() {
		queryResponse, err := resultsIterator.Next()
		if err != nil {
			return nil, err
		}

		var reservation Reservation
		err = json.Unmarshal(queryResponse.Value, &reservation)
		if err != nil {
			return nil, err
		}
		reservations = append(reservations, &reservation)
	}

	return reservations, nil
}

// GetReservationsByRoom returns all reservations for a specific room
func (s *SmartContract) GetReservationsByRoom(ctx contractapi.TransactionContextInterface, roomNumber, block string) ([]*Reservation, error) {
	allReservations, err := s.GetAllReservations(ctx)
	if err != nil {
		return nil, err
	}

	var roomReservations []*Reservation
	for _, reservation := range allReservations {
		if reservation.RoomNumber == roomNumber && reservation.Block == block && reservation.Status == "active" {
			roomReservations = append(roomReservations, reservation)
		}
	}

	return roomReservations, nil
}

// GetReservationsByUser returns all reservations for a specific user
func (s *SmartContract) GetReservationsByUser(ctx contractapi.TransactionContextInterface, userID string) ([]*Reservation, error) {
	allReservations, err := s.GetAllReservations(ctx)
	if err != nil {
		return nil, err
	}

	var userReservations []*Reservation
	for _, reservation := range allReservations {
		if reservation.UserID == userID {
			userReservations = append(userReservations, reservation)
		}
	}

	return userReservations, nil
}

// GetAvailableRooms returns all available rooms for a specific time period
func (s *SmartContract) GetAvailableRooms(ctx contractapi.TransactionContextInterface, startTimeStr, endTimeStr string) ([]*Room, error) {
	startTime, err := time.Parse("2006-01-02 15:04", startTimeStr)
	if err != nil {
		return nil, fmt.Errorf("invalid start time format: %s", startTimeStr)
	}

	endTime, err := time.Parse("2006-01-02 15:04", endTimeStr)
	if err != nil {
		return nil, fmt.Errorf("invalid end time format: %s", endTimeStr)
	}

	// Get all rooms
	allRooms, err := s.GetAllRooms(ctx)
	if err != nil {
		return nil, err
	}

	var availableRooms []*Room
	for _, room := range allRooms {
		conflict, err := s.hasConflictingReservation(ctx, room.Number, room.Block, startTime, endTime, "")
		if err != nil {
			return nil, err
		}
		if !conflict {
			availableRooms = append(availableRooms, room)
		}
	}

	return availableRooms, nil
}

// GetAllRooms returns all rooms in the system
func (s *SmartContract) GetAllRooms(ctx contractapi.TransactionContextInterface) ([]*Room, error) {
	resultsIterator, err := ctx.GetStub().GetStateByRange("ROOM_", "ROOM_~")
	if err != nil {
		return nil, err
	}
	defer resultsIterator.Close()

	var rooms []*Room
	for resultsIterator.HasNext() {
		queryResponse, err := resultsIterator.Next()
		if err != nil {
			return nil, err
		}

		var room Room
		err = json.Unmarshal(queryResponse.Value, &room)
		if err != nil {
			return nil, err
		}
		rooms = append(rooms, &room)
	}

	return rooms, nil
}

// GetUser returns user information
func (s *SmartContract) GetUser(ctx contractapi.TransactionContextInterface, userID string) (*User, error) {
	userBytes, err := ctx.GetStub().GetState("USER_" + userID)
	if err != nil {
		return nil, fmt.Errorf("failed to read user: %v", err)
	}
	if userBytes == nil {
		return nil, fmt.Errorf("user %s does not exist", userID)
	}

	var user User
	err = json.Unmarshal(userBytes, &user)
	if err != nil {
		return nil, err
	}

	return &user, nil
}

// hasConflictingReservation checks if there's a conflicting reservation for the given time period
func (s *SmartContract) hasConflictingReservation(ctx contractapi.TransactionContextInterface, roomNumber, block string, startTime, endTime time.Time, excludeReservationID string) (bool, error) {
	roomReservations, err := s.GetReservationsByRoom(ctx, roomNumber, block)
	if err != nil {
		return false, err
	}

	for _, reservation := range roomReservations {
		// Skip the reservation we're excluding (useful for updates)
		if reservation.ID == excludeReservationID {
			continue
		}

		// Check for time overlap
		if startTime.Before(reservation.EndTime) && endTime.After(reservation.StartTime) {
			return true, nil
		}
	}

	return false, nil
}

// GetReservationsByDateRange returns reservations within a date range
func (s *SmartContract) GetReservationsByDateRange(ctx contractapi.TransactionContextInterface, startDateStr, endDateStr string) ([]*Reservation, error) {
	startDate, err := time.Parse("2006-01-02", startDateStr)
	if err != nil {
		return nil, fmt.Errorf("invalid start date format: %s", startDateStr)
	}

	endDate, err := time.Parse("2006-01-02", endDateStr)
	if err != nil {
		return nil, fmt.Errorf("invalid end date format: %s", endDateStr)
	}

	// Add 24 hours to end date to include the entire day
	endDate = endDate.Add(24 * time.Hour)

	allReservations, err := s.GetAllReservations(ctx)
	if err != nil {
		return nil, err
	}

	var filteredReservations []*Reservation
	for _, reservation := range allReservations {
		if reservation.StartTime.After(startDate) && reservation.StartTime.Before(endDate) && reservation.Status == "active" {
			filteredReservations = append(filteredReservations, reservation)
		}
	}

	return filteredReservations, nil
}

func main() {
	assetChaincode, err := contractapi.NewChaincode(&SmartContract{})
	if err != nil {
		log.Panicf("Error creating room reservation chaincode: %v", err)
	}

	if err := assetChaincode.Start(); err != nil {
		log.Panicf("Error starting room reservation chaincode: %v", err)
	}
}

