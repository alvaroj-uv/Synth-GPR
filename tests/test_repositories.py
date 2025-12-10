"""
Unit tests for Scene Repository implementations.
"""

import pytest
from pathlib import Path
import tempfile
import shutil

from src.repositories import (
    SceneRepository,
    SceneMetadata,
    InMemorySceneRepository,
    FileSystemSceneRepository,
)


# Sample test data
SAMPLE_GPRMAX_CONTENT = """#title: Test Scene
#domain: 0.5 1.5 0.005
#material: 5.0 0.01 1.0 0.0 subgrade
#box: 0 0 0 0.5 0.6 0.005 subgrade
"""

SAMPLE_METADATA = SceneMetadata(
    id="s_001",  # Matches scene_id used in tests
    label="C",
    pvc=5.0,
    fi=2.0,
    classification="Clean",
    porosity=0.4,
    rock_count=150,
)


class TestInMemoryRepository:
    """Tests for InMemorySceneRepository."""
    
    def setup_method(self):
        """Create fresh repository for each test."""
        self.repo = InMemorySceneRepository()
    
    def test_save_and_find_by_id(self):
        """Can save and retrieve scene."""
        self.repo.save("s_001", SAMPLE_GPRMAX_CONTENT, SAMPLE_METADATA)
        
        content = self.repo.find_by_id("s_001")
        assert content == SAMPLE_GPRMAX_CONTENT
    
    def test_find_nonexistent_returns_none(self):
        """Finding nonexistent scene returns None."""
        assert self.repo.find_by_id("nonexistent") is None
    
    def test_get_metadata(self):
        """Can retrieve metadata."""
        self.repo.save("s_001", SAMPLE_GPRMAX_CONTENT, SAMPLE_METADATA)
        
        metadata = self.repo.get_metadata("s_001")
        assert metadata is not None
        assert metadata.id == "s_001"  # Fixed
        assert metadata.classification ==  "Clean"
    
    def test_find_all(self):
        """find_all returns all metadata."""
        self.repo.save("s_001", SAMPLE_GPRMAX_CONTENT, SAMPLE_METADATA)
        self.repo.save("s_002", SAMPLE_GPRMAX_CONTENT,
                       SceneMetadata("s_002", "F", 30.0, 12.0, "Fouled", 0.4, 100))
        
        all_scenes = self.repo.find_all()
        assert len(all_scenes) == 2
    
    def test_find_by_classification(self):
        """Can filter by classification."""
        self.repo.save("s_001", SAMPLE_GPRMAX_CONTENT, SAMPLE_METADATA)
        self.repo.save("s_002", SAMPLE_GPRMAX_CONTENT,
                       SceneMetadata("s_002", "F", 30.0, 12.0, "Fouled", 0.4, 100))
        
        clean = self.repo.find_by_classification("Clean")
        assert len(clean) == 1
        assert clean[0].id == "s_001"  # Fixed
        
        fouled = self.repo.find_by_classification("Fouled")
        assert len(fouled) == 1
        assert fouled[0].id == "s_002"
    
    def test_count(self):
        """count() returns correct number."""
        assert self.repo.count() == 0
        
        self.repo.save("s_001", SAMPLE_GPRMAX_CONTENT, SAMPLE_METADATA)
        assert self.repo.count() == 1
        
        self.repo.save("s_002", SAMPLE_GPRMAX_CONTENT, SAMPLE_METADATA)
        assert self.repo.count() == 2
    
    def test_exists(self):
        """exists() checks correctly."""
        assert not self.repo.exists("s_001")
        
        self.repo.save("s_001", SAMPLE_GPRMAX_CONTENT, SAMPLE_METADATA)
        assert self.repo.exists("s_001")
    
    def test_clear(self):
        """clear() removes all data."""
        self.repo.save("s_001", SAMPLE_GPRMAX_CONTENT, SAMPLE_METADATA)
        assert self.repo.count() == 1
        
        self.repo.clear()
        assert self.repo.count() == 0


class TestFileSystemRepository:
    """Tests for FileSystemSceneRepository."""
    
    def setup_method(self):
        """Create temporary directory for each test."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.repo = FileSystemSceneRepository(self.temp_dir)
    
    def teardown_method(self):
        """Clean up temporary directory."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_save_creates_in_file(self):
        """Saving creates .in file."""
        self.repo.save("s_001", SAMPLE_GPRMAX_CONTENT, SAMPLE_METADATA)
        
        in_file = self.temp_dir / "s_001.in"
        assert in_file.exists()
        assert in_file.read_text() == SAMPLE_GPRMAX_CONTENT
    
    def test_save_creates_metadata_csv(self):
        """Saving creates metadata.csv."""
        self.repo.save("s_001", SAMPLE_GPRMAX_CONTENT, SAMPLE_METADATA)
        
        metadata_csv = self.temp_dir / "metadata.csv"
        assert metadata_csv.exists()
    
    def test_find_by_id_from_file(self):
        """Can retrieve .in file from disk."""
        self.repo.save("s_001", SAMPLE_GPRMAX_CONTENT, SAMPLE_METADATA)
        
        content = self.repo.find_by_id("s_001")
        assert content == SAMPLE_GPRMAX_CONTENT
    
    def test_get_metadata_from_csv(self):
        """Can retrieve metadata from CSV."""
        self.repo.save("s_001", SAMPLE_GPRMAX_CONTENT, SAMPLE_METADATA)
        
        metadata = self.repo.get_metadata("s_001")
        assert metadata is not None
        assert metadata.classification == "Clean"
    
    def test_find_all_reads_csv(self):
        """find_all reads from CSV."""
        self.repo.save("s_001", SAMPLE_GPRMAX_CONTENT, SAMPLE_METADATA)
        self.repo.save("s_002", SAMPLE_GPRMAX_CONTENT,
                       SceneMetadata("s_002", "F", 30.0, 12.0, "Fouled", 0.4, 100))
        
        all_scenes = self.repo.find_all()
        assert len(all_scenes) == 2
    
    def test_find_by_classification_filters_csv(self):
        """find_by_classification filters CSV data."""
        self.repo.save("s_001", SAMPLE_GPRMAX_CONTENT, SAMPLE_METADATA)
        self.repo.save("s_002", SAMPLE_GPRMAX_CONTENT,
                       SceneMetadata("s_002", "F", 30.0, 12.0, "Fouled", 0.4, 100))
        
        clean = self.repo.find_by_classification("Clean")
        assert len(clean) == 1
    
    def test_exists_checks_file(self):
        """exists() checks filesystem."""
        assert not self.repo.exists("s_001")
        
        self.repo.save("s_001", SAMPLE_GPRMAX_CONTENT, SAMPLE_METADATA)
        assert self.repo.exists("s_001")
    
    def test_count_from_csv(self):
        """count() reads from CSV."""
        assert self.repo.count() == 0
        
        self.repo.save("s_001", SAMPLE_GPRMAX_CONTENT, SAMPLE_METADATA)
        assert self.repo.count() == 1
