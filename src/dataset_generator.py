"""
DatasetGenerator - Modern wrapper around ProductionLine factory pattern.

Generates synthetic GPR datasets for railway ballast fouling detection.

Railway Ballast Context:
- Ballast: crushed rocks (20-60mm) laid 250-350mm thick on subgrade
- Role: distribute train loads, provide drainage, absorb vibration
- Fouling: fine materials fill voids → reduced drainage/performance
- Detection: GPR electromagnetic signals correlate with fouling level (PVC)

This generator creates labeled training data for ML-based fouling classification.
Simplified geometry (cylinders) provides sufficient electromagnetic complexity
for GPR while enabling efficient large-scale dataset generation.
"""
import random
from pathlib import Path
from typing import List, Dict, Any
import pandas as pd

from .config import GeneratorConfig
from .physics import classify_pvc, compute_fouling_index, classify_fouling_index, convert_pvc_to_fi
from .work_order import WorkOrder, WorkOrderSystem
from .production_line import ProductionLine
from .sampling import ParameterSampler


class DatasetGenerator:
    """
    Generate synthetic GPR datasets using Worker factory pattern.
    
    Simplified, modern API focused on clarity and maintainability.
    """
    
    def __init__(self, config: GeneratorConfig):
        """
        Initialize generator with configuration.
        
        Args:
            config: GeneratorConfig with all simulation parameters
        """
        self.config = config
        self.pipeline = ProductionLine(config)
        self.sampler = ParameterSampler(config)
        
        # Set random seeds for reproducibility
        if config.base_seed is not None:
            random.seed(config.base_seed)
            try:
                import numpy as np
                np.random.seed(config.base_seed)
            except ImportError:
                pass
    
    def generate_samples(
        self,
        output_dir: Path | str,
        n_samples: int,
        start_id: int = 0,
        save_metadata: bool = True
    ) -> List[str]:
        """
        Generate n samples to output directory.
        
        Args:
            output_dir: Directory to save .in files
            n_samples: Number of samples to generate
            start_id: Starting sample ID
            
        Returns:
            Tuple[List[str], List[Dict]]
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        generated_files = []
        metadata_rows = []
        
        for i in range(n_samples):
            sample_id = start_id + i
            
            # Sample random parameters
            params = self._sample_parameters()
            
            # Create WorkOrder
            work_order = WorkOrder(
                id=f"s{sample_id:04d}",
                params=params
            )
            wos = WorkOrderSystem(work_order)
            
            # Run production pipeline
            try:
                files = self.pipeline.run(wos, str(output_dir))
                generated_files.extend(files)
                
                # Calculate FI_class from actual PVC (for metadata CSV)
                actual_pvc = wos.get('pvc', params['pvc'])
                if self.config.granular_mode:
                    FI_class = classify_pvc(actual_pvc)
                else:
                    # Get actual ballast composition from workers
                    actual_ballast = wos.get('ballast_thickness', params['ballast_thickness'])
                    FI = compute_fouling_index(actual_ballast, 0.0)
                    FI_class = classify_fouling_index(FI)
                
                # Extract metadata
                metadata = self._extract_metadata(sample_id, wos, params)
                metadata['FI_class'] = FI_class  # Use actual FI_class
                metadata_rows.append(metadata)
                
                print(f"[OK] Sample {sample_id}: {len(files)} file(s) generated")
                
            except Exception as e:
                print(f"[ERROR] Sample {sample_id} failed: {e}")
                import traceback
                traceback.print_exc()
        
        # Save metadata CSV
        if save_metadata and metadata_rows:
            self._save_metadata(metadata_rows, output_dir)
        
        return generated_files, metadata_rows
    
    def _sample_parameters(self) -> Dict[str, Any]:
        """
        Sample random parameters from config ranges.
        
        Returns:
            Dictionary of sampled parameters for WorkOrder
        """
        cfg = self.config
        
        # Sample ballast thickness
        ballast_thickness = random.uniform(
            cfg.min_ballast_thickness,
            cfg.max_ballast_thickness
        )
        
        # Sample PVC and moisture
        pvc = random.uniform(cfg.pvc_min, cfg.pvc_max) if cfg.granular_mode else 0.0
        moisture = random.uniform(cfg.moisture_min, cfg.moisture_max)
        
        # Calculate Fouling Index (FI) - critical for ML training
        if cfg.granular_mode:
            FI = convert_pvc_to_fi(pvc)
            FI_class = classify_fouling_index(FI)
        else:
            rock_thickness, fouling_thickness = self._sample_heights()
            FI = compute_fouling_index(rock_thickness, fouling_thickness)
            FI_class = classify_fouling_index(FI)
        
        return {
            'ballast_thickness': ballast_thickness,
            'pvc': pvc,
            'moisture': moisture,
            'antenna_offset': 0.0,
            'FI': FI,
            'FI_class': FI_class
        }
    
    def _sample_heights(self) -> tuple:
        """Sample rock and fouling thicknesses for non-granular mode."""
        cfg = self.config
        total = random.uniform(cfg.min_ballast_thickness, cfg.max_ballast_thickness)
        foul = random.uniform(cfg.min_foul_thickness, cfg.max_foul_thickness)
        foul = min(foul, total)
        rock = total - foul
        return rock, foul
    
    def _extract_metadata(
        self,
        sample_id: int,
        wos: WorkOrderSystem,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extract metadata from WorkOrderSystem.
        
        Args:
            sample_id: Sample identifier
            wos: WorkOrderSystem after pipeline execution
            params: Input parameters
            
        Returns:
            Metadata dictionary
        """
        return {
            'sample_id': sample_id,
            'FI_class': params['FI_class'],
            'pvc': params['pvc'],
            'moisture': params['moisture'],
            'ballast_thickness': params['ballast_thickness'],
            'rock_count': wos.get('rock_count', 0),
            'tx_x': self.config.tx_x,
            'rx_x': self.config.rx_x,
            'tx_rx_y': self.config.tx_rx_y,
            'center_freq': self.config.center_freq,
        }
    
    def _save_metadata(self, metadata_rows: List[Dict], output_dir: Path):
        """
        Save metadata to CSV.
        
        Args:
            metadata_rows: List of metadata dictionaries
            output_dir: Output directory
        """
        df = pd.DataFrame(metadata_rows)
        
        # Format floats
        float_cols = df.select_dtypes(include=['float64', 'float32']).columns
        for col in float_cols:
            df[col] = df[col].apply(lambda x: float(f'{x:.5g}') if pd.notna(x) else x)
        
        csv_path = output_dir / 'metadata.csv'
        df.to_csv(csv_path, index=False, float_format='%.5g')
        print(f"[OK] Metadata saved to {csv_path}")
