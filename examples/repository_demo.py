"""
Example: Using Scene Repository

Demonstrates how repositories decouple persistence from domain logic.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.repositories import (
    SceneRepository,
    SceneMetadata,
    FileSystemSceneRepository,
    InMemorySceneRepository,
)


# Sample .in file content
SAMPLE_SCENE_CONTENT = """#title: Clean Ballast Test
#domain: 0.5 1.5 0.005
#dx_dy_dz: 0.005 0.005 0.005
#time_window: 3e-08

#material: 5.0 0.01 1.0 0.0 subgrade
#material: 6.0 0.015 1.0 0.0 formation
#material: 4.0 0.001 1.0 0.0 bal_rock

#box: 0 0 0 0.5 0.5 0.005 subgrade
#box: 0 0.5 0 0.5 0.6 0.005 formation
#cylinder: 0.25 0.75 0 0.25 0.75 0.005 0.02 bal_rock

#waveform: ricker 1.0 1.5e9 my_ricker
#hertzian_dipole: z 0.25 1.4 0.0025 my_ricker
#rx: 0.25 1.4 0.0025
"""


def example_file_system_repository():
    """Example: FileSystemSceneRepository for production use."""
    print("=" * 60)
    print("Example 1: FileSystemSceneRepository (Production)")
    print("=" * 60)
    
    # Create repository (uses filesystem + CSV)
    output_dir = Path("output/examples/repository_demo")
    repo = FileSystemSceneRepository(output_dir)
    
    # Save scenes
    for i in range(3):
        scene_id = f"s_{i:04d}"
        pvc = i * 15.0  # 0%, 15%, 30%
        
        metadata = SceneMetadata(
            id=scene_id,
            label="C" if pvc < 10 else "F",
            pvc=pvc,
            fi=pvc * 0.4,
            classification="Clean" if pvc < 10 else "Fouled",
            porosity=0.4,
            rock_count=150 - i * 10
        )
        
        repo.save(scene_id, SAMPLE_SCENE_CONTENT, metadata)
        print(f"Saved {scene_id}: {metadata.classification}")
    
    # Query scenes
    print(f"\nTotal scenes: {repo.count()}")
    
    # Find by classification
    clean_scenes = repo.find_by_classification("Clean")
    print(f"Clean scenes: {len(clean_scenes)}")
    
    fouled_scenes = repo.find_by_classification("Fouled")
    print(f"Fouled scenes: {len(fouled_scenes)}")
    
    # Retrieve specific scene
    scene_content = repo.find_by_id("s_0001")
    if scene_content:
        print(f"\nRetrieved s_0001 ({len(scene_content)} bytes)")
    
    print(f"\nFiles created in: {output_dir}")
    print(f"  - metadata.csv")
    print(f"  - s_0000.in, s_0001.in, s_0002.in")
    print()


def example_in_memory_repository():
    """Example: InMemoryRepository for testing."""
    print("=" * 60)
    print("Example 2: InMemoryRepository (Testing)")
    print("=" * 60)
    
    # Create in-memory repository (no file I/O)
    repo = InMemorySceneRepository()
    
    # Save some test scenes
    for i in range(5):
        scene_id = f"test_{i}"
        metadata = SceneMetadata(
            id=scene_id,
            label="C",
            pvc=5.0,
            fi=2.0,
            classification="Clean",
            porosity=0.4,
            rock_count=100
        )
        repo.save(scene_id, SAMPLE_SCENE_CONTENT, metadata)
    
    print(f"Created {repo.count()} test scenes (in memory, no files)")
    
    # Test queries
    all_scenes = repo.find_all()
    print(f"All scenes: {[s.id for s in all_scenes]}")
    
    # Check existence
    print(f"test_0 exists? {repo.exists('test_0')}")
    print(f"nonexistent exists? {repo.exists('nonexistent')}")
    
    # Clear (useful for test cleanup)
    repo.clear()
    print(f"After clear: {repo.count()} scenes")
    print()


def example_swappable_backends():
    """Example: Swapping repository backends without changing code."""
    print("=" * 60)
    print("Example 3: Swappable Backends")
    print("=" * 60)
    
    def process_scenes(repo: SceneRepository, label: str):
        """
        Business logic that works with ANY repository implementation.
        
        This function doesn't care if it's filesystem, memory, or database.
        """
        print(f"\n{label}:")
        print(f"  Total scenes: {repo.count()}")
        
        # Process all scenes
        for metadata in repo.find_all():
            print(f"  - {metadata.id}: {metadata.classification}")
    
    # Same code works with different repositories!
    
    # 1. In-memory (fast for tests)
    mem_repo = InMemorySceneRepository()
    mem_repo.save("s_001", SAMPLE_SCENE_CONTENT,
                  SceneMetadata("s_001", "C", 5.0, 2.0, "Clean", 0.4, 150))
    process_scenes(mem_repo, "In-Memory Repository")
    
    # 2. Filesystem (production)
    fs_repo = FileSystemSceneRepository("output/examples/swap_test")
    fs_repo.save("s_001", SAMPLE_SCENE_CONTENT,
                 SceneMetadata("s_001", "C", 5.0, 2.0, "Clean", 0.4, 150))
    process_scenes(fs_repo, "Filesystem Repository")
    
    # 3. Future: Could easily add DatabaseRepository, CloudRepository, etc.
    #    without changing process_scenes() function!
    print()


def example_benefits_summary():
    """Summary of repository pattern benefits."""
    print("=" * 60)
    print("Repository Pattern Benefits")
    print("=" * 60)
    print("✓ Decoupling:")
    print("  - Domain logic doesn't know about files/databases")
    print("  - Change storage without touching business code")
    
    print("\n✓ Testing:")
    print("  - Use InMemoryRepository for fast unit tests")
    print("  - No file I/O during testing")
    
    print("\n✓ Flexibility:")
    print("  - Easy to add new backends (SQLite, PostgreSQL, S3)")
    print("  - Query by classification without hardcoded file searches")
    
    print("\n✓ Single Responsibility:")
    print("  - Repository handles ONLY persistence")
    print("  - Domain objects handle ONLY business logic")
    
    print("\n✓ Backward Compatibility:")
    print("  - FileSystemRepository uses existing CSV structure")
    print("  - Works with current pipeline scripts")


if __name__ == "__main__":
    example_file_system_repository()
    example_in_memory_repository()
    example_swappable_backends()
    example_benefits_summary()
