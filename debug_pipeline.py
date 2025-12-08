from src.dataset_generator import DatasetGenerator
from src.config import GeneratorConfig

# Create minimal config
cfg = GeneratorConfig(
    base_seed=42,
    granular_mode=True,
    pvc_min=10.0,
    pvc_max=30.0
)

# Create generator
gen = DatasetGenerator(cfg)

# Test parameter sampling
params = gen._sample_parameters()
print(f"Sampled parameters: {params}")

# Test single sample generation with debug
print("\nGenerating 1 sample with debug...")

from src.work_order import WorkOrder, WorkOrderSystem

wo_params = {
    'pvc': params['pvc'],
    'moisture': params['moisture'],
    'ballast_thickness': params['ballast_thickness'],
    'antenna_offset': 0.0
}

wo = WorkOrder(id="debug_test", params=wo_params)
wos = WorkOrderSystem(wo)

# Run pipeline with error checking
try:
    files = gen.pipeline.run(wos, "output/debug")
    print(f"\nGenerated files: {files}")
    
    # Check for errors
    issues = wos.export_issues()
    if issues:
        print(f"\n⚠️ Issues detected ({len(issues)}):")
        for issue in issues:
            print(f"  [{issue['severity']}] {issue['worker']}: {issue['description']}")
    else:
        print("\n✓ No issues detected")
        
except Exception as e:
    print(f"\n✗ Exception: {e}")
    import traceback
    traceback.print_exc()
