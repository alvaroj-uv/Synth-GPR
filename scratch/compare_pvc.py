import json

print(f"{'PVC Target':<15} | {'Global MC PVC':<15} | {'Lab FI (15cm)':<15} | {'LDCP FI (1D)':<15} | {'CRIM Bulk EPS':<15} | {'Clean Depth':<15}")
print("-" * 105)

for pvc in [20, 50, 80]:
    try:
        with open(f'output_test/final_{pvc}.in', 'r') as f:
            lines = f.readlines()
            meta = {}
            for l in lines:
                if l.startswith('## ') and ':' in l:
                    key, val = l[3:].split(':', 1)
                    meta[key.strip()] = val.strip()
            
            mc_pvc = float(meta.get('mc_pvc_measured', 0))
            lab_fi = float(meta.get('Lab_FI', 0))
            ldcp_fi = float(meta.get('Lab_LDCP_FI_est', 0))
            bulk_eps = float(meta.get('Lab_bulk_eps', 0))
            clean_mm = float(meta.get('Lab_clean_ballast_mm', 0))
            lab_class = meta.get('Lab_Class', '')
            
            print(f"{pvc:>13}% | {mc_pvc:>14.1f}% | {lab_fi:>15.1f} ({lab_class}) | {ldcp_fi:>15.1f} | {bulk_eps:>15.2f} | {clean_mm:>11.0f} mm")
    except Exception as e:
        print(f"Error reading PVC {pvc}: {e}")

