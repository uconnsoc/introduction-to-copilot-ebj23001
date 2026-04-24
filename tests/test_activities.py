"""
FastAPI tests for the Mergington High School Activities API

Tests follow the AAA (Arrange-Act-Assert) pattern for clarity and maintainability.
- Arrange: Set up test data and preconditions
- Act: Execute the API request
- Assert: Validate response and side effects
"""

import pytest
from fastapi.testclient import TestClient


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_all_activities_returns_200(self, client, reset_activities):
        """Should return all available activities with 200 status"""
        # Arrange
        # (activities fixture provides initial data)

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Gym Class" in activities

    def test_get_activities_includes_participant_info(self, client, reset_activities):
        """Should include max_participants and participants list"""
        # Arrange
        # (activities fixture provides initial data)

        # Act
        response = client.get("/activities")

        # Assert
        activities = response.json()
        chess_club = activities["Chess Club"]
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)
        assert chess_club["max_participants"] == 12


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_new_student_success(self, client, reset_activities):
        """Should successfully sign up a new student for an activity"""
        # Arrange
        email = "new_student@mergington.edu"
        activity_name = "Basketball Team"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"

    def test_signup_updates_participants_list(self, client, reset_activities):
        """Should add student to the activity's participants list"""
        # Arrange
        email = "new_student@mergington.edu"
        activity_name = "Soccer Club"

        # Act
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        response = client.get("/activities")

        # Assert
        activities = response.json()
        assert email in activities[activity_name]["participants"]

    def test_signup_activity_not_found(self, client, reset_activities):
        """Should return 404 when activity does not exist"""
        # Arrange
        email = "student@mergington.edu"
        activity_name = "Nonexistent Club"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_duplicate_student_rejected(self, client, reset_activities):
        """Should reject duplicate signup with 400 status"""
        # Arrange
        email = "michael@mergington.edu"  # Already in Chess Club
        activity_name = "Chess Club"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up for this activity"

    def test_signup_multiple_students_same_activity(self, client, reset_activities):
        """Should allow multiple different students to sign up for same activity"""
        # Arrange
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"
        activity_name = "Basketball Team"

        # Act
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email1}
        )
        response2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email2}
        )

        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        activities = client.get("/activities").json()
        assert email1 in activities[activity_name]["participants"]
        assert email2 in activities[activity_name]["participants"]

    def test_signup_preserves_existing_participants(self, client, reset_activities):
        """Should preserve existing participants when adding new student"""
        # Arrange
        email = "new_student@mergington.edu"
        activity_name = "Chess Club"
        # Chess Club already has michael and daniel

        # Act
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        response = client.get("/activities")

        # Assert
        activities = response.json()
        participants = activities[activity_name]["participants"]
        assert "michael@mergington.edu" in participants
        assert "daniel@mergington.edu" in participants
        assert email in participants
        assert len(participants) == 3


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_success(self, client, reset_activities):
        """Should successfully unregister student from activity"""
        # Arrange
        email = "michael@mergington.edu"  # Already in Chess Club
        activity_name = "Chess Club"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Unregistered {email} from {activity_name}"

    def test_unregister_removes_from_participants(self, client, reset_activities):
        """Should remove student from the activity's participants list"""
        # Arrange
        email = "michael@mergington.edu"
        activity_name = "Chess Club"

        # Act
        client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        response = client.get("/activities")

        # Assert
        activities = response.json()
        assert email not in activities[activity_name]["participants"]

    def test_unregister_preserves_other_participants(self, client, reset_activities):
        """Should preserve other participants when removing one"""
        # Arrange
        email_to_remove = "michael@mergington.edu"
        email_to_keep = "daniel@mergington.edu"
        activity_name = "Chess Club"

        # Act
        client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email_to_remove}
        )
        response = client.get("/activities")

        # Assert
        activities = response.json()
        participants = activities[activity_name]["participants"]
        assert email_to_remove not in participants
        assert email_to_keep in participants

    def test_unregister_activity_not_found(self, client, reset_activities):
        """Should return 404 when activity does not exist"""
        # Arrange
        email = "student@mergington.edu"
        activity_name = "Nonexistent Club"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_unregister_student_not_signed_up(self, client, reset_activities):
        """Should return 404 when student is not signed up for activity"""
        # Arrange
        email = "not_signed_up@mergington.edu"
        activity_name = "Chess Club"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Student not signed up for this activity"

    def test_unregister_then_signup_again(self, client, reset_activities):
        """Should allow student to sign up again after unregistering"""
        # Arrange
        email = "student@mergington.edu"
        activity_name = "Basketball Team"

        # Act
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        activities = client.get("/activities").json()
        assert email in activities[activity_name]["participants"]
