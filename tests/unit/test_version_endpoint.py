"""Unit tests for version API endpoint."""

from fastapi.testclient import TestClient

from backend.web_app import app
from backend.defaults import APP_VERSION, APP_CHANGELOG


class TestVersionEndpoint:
    """Tests for GET /api/version endpoint."""

    def setup_method(self):
        """Create test client."""
        self.client = TestClient(app)

    def test_version_returns_current_version(self):
        """Test that /api/version returns the current app version."""
        response = self.client.get("/api/version")
        assert response.status_code == 200

        data = response.json()
        assert data["version"] == APP_VERSION

    def test_version_returns_changelog(self):
        """Test that /api/version returns changelog entries."""
        response = self.client.get("/api/version")
        data = response.json()

        assert "changelog" in data
        assert isinstance(data["changelog"], list)
        assert len(data["changelog"]) > 0

        # Each entry should have version and text
        for entry in data["changelog"]:
            assert "version" in entry
            assert "text" in entry

    def test_version_changelog_matches_defaults(self):
        """Test that changelog matches APP_CHANGELOG from defaults."""
        response = self.client.get("/api/version")
        data = response.json()

        assert data["changelog"] == APP_CHANGELOG

    def test_version_first_changelog_matches_current_version(self):
        """Test that the first changelog entry matches the current version."""
        response = self.client.get("/api/version")
        data = response.json()

        first_entry = data["changelog"][0]
        assert first_entry["version"] == APP_VERSION
