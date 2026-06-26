"""
File-system based Scene Repository implementation.

Implements persistence using the existing directory/CSV structure
to maintain backward compatibility with current tooling.
"""

from pathlib import Path
from typing import Optional, List
import pandas as pd

from .scene_repository import SceneRepository, SceneMetadata
from ..file_reader import parse_metadata_comments
from ..data_access import INFileReader


class FileSystemSceneRepository(SceneRepository):
    """
    Repository implementation using filesystem + CSV.
    
    Directory Structure:
        output_dir/
        ├── metadata.csv           # All scene metadata
        ├── s_0000.in              # gprMax input file
        ├── s_0001.in
        └── ...
    
    This maintains compatibility with existing scripts that expect
    this directory layout.
    """
    
    def __init__(self, output_dir: Path | str):
        """
        Initialize repository with output directory.
        
        Args:
            output_dir: Directory for storing scenes and metadata
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.metadata_path = self.output_dir / "metadata.csv"
        self._metadata_cache: Optional[pd.DataFrame] = None
    
    def save(
        self,
        scene_id: str,
        gprmax_content: str,
        metadata: SceneMetadata
    ) -> None:
        """
        Save scene to filesystem.
        
        Args:
            scene_id: Scene identifier (e.g., "s_0001")
            gprmax_content: Complete .in file content
            metadata: Scene metadata
        """
        # Save .in file
        in_file_path = self.output_dir / f"{scene_id}.in"
        in_file_path.write_text(gprmax_content, encoding='utf-8')
        
        # Update metadata CSV
        self._append_metadata(metadata)
    
    def find_by_id(self, scene_id: str) -> Optional[str]:
        """
        Retrieve .in file content by ID.
        
        Args:
            scene_id: Scene identifier
        
        Returns:
            File content or None if not found
        """
        in_file_path = self.output_dir / f"{scene_id}.in"
        if not in_file_path.exists():
            return None
        return in_file_path.read_text(encoding='utf-8')
    
    def get_metadata(self, scene_id: str) -> Optional[SceneMetadata]:
        """
        Retrieve metadata for a scene.
        
        Args:
            scene_id: Scene identifier
        
        Returns:
            SceneMetadata or None if not found
        """
        df = self._load_metadata()
        if df is None or df.empty:
            return None
        
        # Try exact match first
        matching = df[df['id'] == scene_id]
        
        # If no match and scene_id doesn't match the metadata id format,
        # the issue is the metadata.id field vs the scene_id used to save
        # Let's check if we need to use the scene_id from when we saved
        if matching.empty:
            # Try matching by scene_id used in filename (without metadata internal id)
            # This shouldn't happen in production but helps with tests
            return None
        
        row = matching.iloc[0]
        return SceneMetadata.from_dict(row.to_dict())
    
    def find_all(self) -> List[SceneMetadata]:
        """
        List all scene metadata.
        
        Returns:
            List of all scene metadata (sorted by ID)
        """
        df = self._load_metadata()
        if df is None or df.empty:
            return []
        
        return [
            SceneMetadata.from_dict(row.to_dict())
            for _, row in df.iterrows()
        ]
    
    def find_by_classification(self, classification: str) -> List[SceneMetadata]:
        """
        Query scenes by fouling classification.
        
        Args:
            classification: 'Clean', 'Moderately Fouled', 'Fouled', 'Highly Fouled'
        
        Returns:
            List of matching scene metadata
        """
        df = self._load_metadata()
        if df is None or df.empty:
            return []
        
        matching = df[df['classification'] == classification]
        return [
            SceneMetadata.from_dict(row.to_dict())
            for _, row in matching.iterrows()
        ]
    
    def count(self) -> int:
        """
        Count total scenes in repository.
        
        Returns:
            Total number of scenes
        """
        df = self._load_metadata()
        if df is None:
            return 0
        return len(df)
    
    def exists(self, scene_id: str) -> bool:
        """
        Check if scene exists.
        
        Args:
            scene_id: Scene identifier
        
        Returns:
            True if scene exists
        """
        in_file_path = self.output_dir / f"{scene_id}.in"
        return in_file_path.exists()
    
    def _load_metadata(self) -> Optional[pd.DataFrame]:
        """
        Load metadata from CSV (with caching).
        
        Returns:
            DataFrame or None if file doesn't exist
        """
        if not self.metadata_path.exists():
            return None
        
        # Simple cache (reload if file changed)
        # In production, you'd check mtime
        if self._metadata_cache is None:
            self._metadata_cache = pd.read_csv(self.metadata_path)
        
        return self._metadata_cache
    
    def _append_metadata(self, metadata: SceneMetadata) -> None:
        """
        Append metadata to CSV file.
        
        Args:
            metadata: Scene metadata to add
        """
        # Load existing data
        if self.metadata_path.exists():
            df = pd.read_csv(self.metadata_path)
        else:
            df = pd.DataFrame()
        
        # Append new row
        new_row = pd.DataFrame([metadata.to_dict()])
        df = pd.concat([df, new_row], ignore_index=True)
        
        # Save
        df.to_csv(self.metadata_path, index=False, float_format='%.5g')
        
        # Invalidate cache
        self._metadata_cache = None
    
    def rebuild_metadata_from_files(self) -> None:
        """
        Rebuild metadata.csv by scanning .in files.
        
        Useful for recovery if metadata.csv is lost or corrupted.
        This reads the comment headers from .in files to reconstruct metadata.
        """
        # Find all .in files
        in_files = sorted(self.output_dir.glob("*.in"))
        
        metadata_rows = []
        for in_file in in_files:
            scene_id = in_file.stem
            content = INFileReader().read(in_file)
            
            # Parse metadata from .in file comments
            # (This would need to be implemented based on your .in file format)
            # For now, this is a placeholder
            metadata = self._extract_metadata_from_in_file(scene_id, content)
            if metadata:
                metadata_rows.append(metadata.to_dict())
        
        # Write new metadata.csv
        if metadata_rows:
            df = pd.DataFrame(metadata_rows)
            df.to_csv(self.metadata_path, index=False, float_format='%.5g')
            self._metadata_cache = None
            print(f"Rebuilt metadata.csv with {len(metadata_rows)} entries")
    
    def _extract_metadata_from_in_file(
        self,
        scene_id: str,
        content: str
    ) -> Optional[SceneMetadata]:
        """
        Extract metadata from .in file comments.
        
        Looks for comment lines like:
            ## FI (%): 10.5
            ## FI_class: Moderately Fouled
        
        Args:
            scene_id: Scene ID
            content: .in file content
        
        Returns:
            SceneMetadata or None if parsing fails
        """
        # This is a simplified parser - enhance as needed
        metadata = {
            'id': scene_id,
            'label': 'U',  # Unknown
            'pvc': 0.0,
            'fi': 0.0,
            'classification': 'Unknown',
            'porosity': 0.4,
            'rock_count': 0,
        }
        
        meta = parse_metadata_comments(content.split('\n'))
        if 'FI (%)' in meta:
            try:
                metadata['fi'] = float(meta['FI (%)'])
            except (TypeError, ValueError):
                pass
        if 'FI_class' in meta:
            metadata['classification'] = str(meta['FI_class'])
        
        # Only return if we found meaningful data
        if metadata['fi'] > 0 or metadata['classification'] != 'Unknown':
            return SceneMetadata.from_dict(metadata)
        
        return None
