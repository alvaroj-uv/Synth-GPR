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
import logging
import random
from pathlib import Path
from typing import List

from .config import GeneratorConfig
from .logging_config import get_logger
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
        self.logger = get_logger(__name__)

    def generate_samples(
        self,
        output_dir: Path | str,
        n_samples: int,
        start_id: int = 0,
    ) -> list[str]:
        """
        Generate n samples to output directory.

        All metadata is embedded in .in file CONFIG_* headers.
        Each generated .in file is self-contained with complete configuration.

        Args:
            output_dir: Directory to save .in files
            n_samples: Number of samples to generate
            start_id: Starting sample ID

        Returns:
            List of written file paths
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        if self.config.base_seed is not None:
            seed = self.config.base_seed + start_id
            random.seed(seed)
            try:
                import numpy as np
                np.random.seed(seed)
            except ImportError:
                pass

        generated_files = []

        for i in range(n_samples):
            sample_id = start_id + i
            
            # Sample random parameters
            params = self.sampler.sample()
            
            # Create WorkOrder using factory method
            work_order = WorkOrder.from_sampled_params(sample_id, params)
            wos = WorkOrderSystem(work_order)
            
            # Run production pipeline (returns SceneCheckpoint)
            try:
                checkpoint = self.pipeline.run(wos)
                
                # Export metadata to work_order blackboard for inspection
                metadata = wos.export_metadata()
                metadata.update(checkpoint.metadata)

                # Carry sampler-only keys that aren't in SceneParameters
                for k in ('FI_bottom', 'FI_top', 'pvc_bottom', 'pvc_top'):
                    if k in params and k not in metadata:
                        metadata[k] = params[k]
                
                # Log explicit virtual lab results
                self.logger.debug(f"Virtual Lab Results for Sample {sample_id}:")
                self.logger.debug(f"  Classification: Target={metadata.get('FI_class', 'N/A')} | Lab_Class={metadata.get('Lab_Class', 'N/A')} | Lab_FI={metadata.get('Lab_FI', 0):.1f} | PVC={metadata.get('pvc', 0):.2f}%")
                self.logger.debug(f"  Virtual LDCP: FI_est={metadata.get('Lab_LDCP_FI_est', 0):.1f} | qs_mean={metadata.get('Lab_LDCP_qs_mean', 0):.2f} MPa")
                self.logger.debug(f"  GPR Physics: bulk_eps={metadata.get('Lab_bulk_eps', 0):.3f} | clean_depth={metadata.get('Lab_clean_ballast_mm', 0):.1f} mm | rocks={checkpoint.rock_count}")
                
                # Validation check (non-blocking, just informational)
                validation_errors = checkpoint.validate_all()
                if validation_errors:
                    self.logger.warning(f"Validation warnings for sample {sample_id}: {len(validation_errors)} issue(s)")
                    for err in validation_errors[:3]:  # Show first 3
                        self.logger.warning(f"  - {err}")
                
                # Save to file using GPRMaxFileWriter
                from .file_writer import GPRMaxFileWriter
                filename = f"s_{sample_id:04d}.in"
                filepath = output_dir / filename

                written_path = GPRMaxFileWriter.save_scene_checkpoint(
                    checkpoint,
                    output_path=str(filepath),
                    scenario_type="Sim",
                    config=self.config,  # Embed config for replication
                    sample_id=sample_id  # For computing actual seed in batch mode
                )
                generated_files.append(written_path)
                
                # Add Config Constants that aren't in params or blackboard
                metadata.update({
                    'tx_x': self.config.tx_x,
                    'rx_x': self.config.rx_x,
                    'antenna_clearance_above_ballast': self.config.antenna_clearance_above_ballast,
                    'center_freq': self.config.center_freq,
                })
                
                self.logger.info(f"Sample {sample_id}: 1 file generated")
                
            except Exception as e:
                self.logger.error(f"Sample {sample_id} failed: {e}")
                import traceback
                self.logger.error(f"Traceback: {traceback.format_exc()}")
        
        return generated_files
