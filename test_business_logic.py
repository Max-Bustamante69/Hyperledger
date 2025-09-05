#!/usr/bin/env python3
"""
Business Logic Verification Script
Tests all university requirements are properly implemented
"""

import asyncio
import sys
from datetime import datetime, timedelta
from client.blockchain_client import BlockchainClient, ReservationUtils

class BusinessLogicTester:
    def __init__(self):
        self.client = BlockchainClient()
        self.test_results = []
    
    async def run_all_tests(self):
        """Run comprehensive business logic tests"""
        print("🧪 UNIVERSITY ROOM RESERVATION SYSTEM - BUSINESS LOGIC VERIFICATION")
        print("=" * 70)
        
        # Initialize client
        await self.client.initialize("test-admin", "professor")
        
        # Test 1: Room Structure
        await self.test_room_structure()
        
        # Test 2: User Roles
        await self.test_user_roles()
        
        # Test 3: Time Validation
        await self.test_time_validation()
        
        # Test 4: Duration Validation
        await self.test_duration_validation()
        
        # Test 5: Conflict Detection
        await self.test_conflict_detection()
        
        # Test 6: Professor Privileges
        await self.test_professor_privileges()
        
        # Test 7: Real-time Features
        await self.test_realtime_features()
        
        # Print results
        self.print_results()
    
    async def test_room_structure(self):
        """Test: 3 blocks, 3 floors, 5 rooms per floor = 45 rooms total"""
        print("\n📋 Test 1: Room Structure Verification")
        
        rooms = ReservationUtils.generate_room_list()
        
        # Check total rooms
        expected_total = 3 * 3 * 5  # 3 blocks × 3 floors × 5 rooms
        actual_total = len(rooms)
        
        self.assert_test("Total rooms count", actual_total == expected_total, 
                        f"Expected {expected_total}, got {actual_total}")
        
        # Check blocks
        blocks = set(room['block'] for room in rooms)
        expected_blocks = {'33', '34', '35'}
        self.assert_test("Blocks 33, 34, 35 exist", blocks == expected_blocks,
                        f"Expected {expected_blocks}, got {blocks}")
        
        # Check floors per block
        for block in expected_blocks:
            block_rooms = [r for r in rooms if r['block'] == block]
            floors = set(r['floor'] for r in block_rooms)
            expected_floors = {'1', '2', '3'}
            self.assert_test(f"Block {block} has floors 1,2,3", floors == expected_floors,
                            f"Block {block}: Expected {expected_floors}, got {floors}")
        
        # Check room numbers per floor
        for block in expected_blocks:
            for floor in ['1', '2', '3']:
                floor_rooms = [r for r in rooms if r['block'] == block and r['floor'] == floor]
                room_numbers = set(r['number'] for r in floor_rooms)
                expected_numbers = {f"{floor}00", f"{floor}01", f"{floor}02", f"{floor}03", f"{floor}04"}
                self.assert_test(f"Block {block} Floor {floor} room numbers", 
                               room_numbers == expected_numbers,
                               f"Expected {expected_numbers}, got {room_numbers}")
    
    async def test_user_roles(self):
        """Test: Student and Professor roles work correctly"""
        print("\n👥 Test 2: User Roles Verification")
        
        # Register student
        result = await self.client.register_user("student1", "John Doe", "john@uni.edu", "student", "33")
        self.assert_test("Student registration", result['success'], result.get('error', ''))
        
        # Register professor  
        result = await self.client.register_user("prof1", "Dr. Smith", "smith@uni.edu", "professor", "33")
        self.assert_test("Professor registration", result['success'], result.get('error', ''))
        
        # Test invalid role
        result = await self.client.register_user("invalid1", "Test", "test@uni.edu", "admin", "33")
        self.assert_test("Invalid role rejection", not result['success'], "Should reject invalid roles")
    
    async def test_time_validation(self):
        """Test: Operating hours 06:00-23:00"""
        print("\n⏰ Test 3: Time Validation")
        
        # Valid time (within hours)
        result = await self.client.make_reservation("100", "33", "student1", "2024-12-20 10:00", 60)
        self.assert_test("Valid time reservation", result['success'], result.get('error', ''))
        
        # Invalid time - too early
        result = await self.client.make_reservation("101", "33", "student1", "2024-12-20 05:00", 60)
        self.assert_test("Too early rejection", not result['success'], "Should reject reservations before 06:00")
        
        # Invalid time - too late
        result = await self.client.make_reservation("102", "33", "student1", "2024-12-20 23:30", 60)
        self.assert_test("Too late rejection", not result['success'], "Should reject reservations after 23:00")
        
        # Invalid time - would end after 23:00
        result = await self.client.make_reservation("103", "33", "student1", "2024-12-20 22:30", 120)
        self.assert_test("End time after 23:00 rejection", not result['success'], "Should reject if ends after 23:00")
    
    async def test_duration_validation(self):
        """Test: Duration options 1h, 1.5h, 2h only"""
        print("\n⏱️ Test 4: Duration Validation")
        
        valid_durations = [60, 90, 120]  # 1h, 1.5h, 2h
        
        for duration in valid_durations:
            result = await self.client.make_reservation(f"20{duration//30}", "33", "student1", 
                                                      "2024-12-21 10:00", duration)
            self.assert_test(f"Valid duration {duration}min", result['success'], result.get('error', ''))
        
        # Invalid durations
        invalid_durations = [30, 45, 150, 180]
        for duration in invalid_durations:
            result = await self.client.make_reservation(f"30{duration//30}", "33", "student1", 
                                                      "2024-12-21 12:00", duration)
            self.assert_test(f"Invalid duration {duration}min rejection", not result['success'], 
                           f"Should reject {duration}min duration")
    
    async def test_conflict_detection(self):
        """Test: No overlapping reservations allowed"""
        print("\n🚫 Test 5: Conflict Detection")
        
        # Make first reservation
        result1 = await self.client.make_reservation("300", "33", "student1", "2024-12-22 14:00", 90)
        self.assert_test("First reservation", result1['success'], result1.get('error', ''))
        
        # Try overlapping reservation (should fail)
        result2 = await self.client.make_reservation("300", "33", "student1", "2024-12-22 14:30", 60)
        self.assert_test("Overlapping reservation rejection", not result2['success'], 
                        "Should reject overlapping reservations")
        
        # Try adjacent reservation (should work)
        result3 = await self.client.make_reservation("300", "33", "student1", "2024-12-22 15:30", 60)
        self.assert_test("Adjacent reservation", result3['success'], result3.get('error', ''))
    
    async def test_professor_privileges(self):
        """Test: Professor can cancel any reservation and override"""
        print("\n🎓 Test 6: Professor Privileges")
        
        # Student makes reservation
        result1 = await self.client.make_reservation("400", "34", "student1", "2024-12-23 16:00", 60)
        self.assert_test("Student reservation", result1['success'], result1.get('error', ''))
        
        if result1['success']:
            reservation_id = result1['reservation_id']
            
            # Another student tries to cancel (should fail)
            await self.client.register_user("student2", "Jane Doe", "jane@uni.edu", "student", "34")
            result2 = await self.client.cancel_reservation(reservation_id, "student2")
            self.assert_test("Student cannot cancel others", not result2['success'], 
                           "Students should not cancel other students' reservations")
            
            # Professor cancels (should work)
            result3 = await self.client.cancel_reservation(reservation_id, "prof1")
            self.assert_test("Professor can cancel any", result3['success'], result3.get('error', ''))
    
    async def test_realtime_features(self):
        """Test: Real-time features and network info"""
        print("\n🔴 Test 7: Real-time Features")
        
        # Test network info
        network_info = self.client.get_network_info()
        self.assert_test("Network info available", network_info['success'], network_info.get('error', ''))
        
        if network_info['success']:
            peers = network_info['peers']
            expected_peer_count = 3  # Block 33, 34, 35
            self.assert_test("Correct peer count", len(peers) == expected_peer_count,
                           f"Expected {expected_peer_count} peers, got {len(peers)}")
            
            peer_blocks = set(peer['block'] for peer in peers)
            expected_blocks = {'33', '34', '35'}
            self.assert_test("All blocks represented", peer_blocks == expected_blocks,
                           f"Expected blocks {expected_blocks}, got {peer_blocks}")
        
        # Test room availability
        result = await self.client.get_available_rooms("2024-12-24 10:00", "2024-12-24 12:00")
        self.assert_test("Room availability check", result['success'], result.get('error', ''))
    
    def assert_test(self, test_name, condition, message):
        """Record test result"""
        status = "✅ PASS" if condition else "❌ FAIL"
        self.test_results.append((test_name, condition, message))
        print(f"  {status}: {test_name}")
        if not condition:
            print(f"    └── {message}")
    
    def print_results(self):
        """Print final test results"""
        print("\n" + "=" * 70)
        print("📊 FINAL TEST RESULTS")
        print("=" * 70)
        
        passed = sum(1 for _, condition, _ in self.test_results if condition)
        total = len(self.test_results)
        
        print(f"\n✅ PASSED: {passed}/{total} tests")
        print(f"❌ FAILED: {total - passed}/{total} tests")
        
        if total - passed > 0:
            print("\n❌ FAILED TESTS:")
            for test_name, condition, message in self.test_results:
                if not condition:
                    print(f"  • {test_name}: {message}")
        
        success_rate = (passed / total) * 100
        print(f"\n🎯 SUCCESS RATE: {success_rate:.1f}%")
        
        if success_rate == 100:
            print("\n🎉 ALL UNIVERSITY REQUIREMENTS VERIFIED SUCCESSFULLY!")
            print("   Your system is ready for demonstration and evaluation.")
        else:
            print(f"\n⚠️  System needs attention before university presentation.")

async def main():
    """Run business logic verification"""
    tester = BusinessLogicTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
