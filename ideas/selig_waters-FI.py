import pandas as pd
import numpy as np
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt

class BallastFoulingAnalyzer:
    def __init__(self, dataframe):
        """
        Initialize with a pandas DataFrame containing sieve analysis data.
        Columns should be sieve sizes in mm (float).
        One column should be 'SampleID' or 'Milepost'.
        """
        self.df = dataframe
        # Identify sieve columns (assumes column names that are floats are sieves)
        self.sieve_cols = [c for c in df.columns if isinstance(c, (int, float))]
        self.sieve_cols.sort(reverse=True) # Standard geotechnical order: largest to smallest

    def _interpolate_passing(self, diameters, passing, target_diam_mm):
        """
        Performs Log-Linear interpolation to find % passing at target diameter.
        """
        # Remove invalid data (NaNs or negative values)
        valid = (passing >= 0) & (~np.isnan(passing))
        if not valid.any():
            return np.nan
        
        d_valid = np.array(diameters)[valid]
        p_valid = np.array(passing)[valid]
        
        # Sort by diameter ascending for interpolation
        sort_idx = np.argsort(d_valid)
        d_sorted = d_valid[sort_idx]
        p_sorted = p_valid[sort_idx]
        
        # Log-transform diameters (handling zero/pan)
        # We perform interpolation in log10 space for diameter
        with np.errstate(divide='ignore'):
            d_log = np.log10(d_sorted)
            target_log = np.log10(target_diam_mm)
            
        # Create interpolator
        # fill_value="extrapolate" handles cases where target is slightly outside range
        # though strictly one should check bounds.
        f = interp1d(d_log, p_sorted, kind='linear', bounds_error=False, fill_value="extrapolate")
        
        result = float(f(target_log))
        
        # Clip result to 0-100% physically possible range
        return max(0.0, min(100.0, result))

    def calculate_metrics(self):
        """
        Calculates P4, P200, and Selig & Waters FI for all samples.
        """
        results =
        
        for index, row in self.df.iterrows():
            # Extract sieve data for this row
            pass_values = row[self.sieve_cols].values
            diameters = self.sieve_cols
            
            # Interpolate critical values
            P4 = self._interpolate_passing(diameters, pass_values, 4.75)
            P200 = self._interpolate_passing(diameters, pass_values, 0.075)
            
            # Calculate FI
            FI = P4 + P200
            
            # Determine Category
            if FI < 1:
                cat = "Clean"
            elif FI < 10:
                cat = "Moderately Clean"
            elif FI < 20:
                cat = "Moderately Fouled"
            elif FI < 40:
                cat = "Fouled"
            else:
                cat = "Highly Fouled"
                
            results.append({
                "SampleID": row.get("SampleID", index),
                "P4_estimated": round(P4, 2),
                "P200_estimated": round(P200, 2),
                "SeligWaters_FI": round(FI, 2),
                "Category": cat
            })
            
        return pd.DataFrame(results)

# Example Usage Scenario
# Define dummy data representing a track section
data = {
    "SampleID": ["MP_100.1", "MP_100.2", "MP_100.3"],
    63.0:  ,
    50.0:  ,
    25.0:  ,
    9.5:   ,  # Percentage Fouling approx source
    2.0:   ,   # Note: 4.75mm is missing, requiring interpolation
    0.063: [0.5, 4, 8]    # Note: 0.075mm is missing, requiring interpolation
}

df = pd.DataFrame(data)
analyzer = BallastFoulingAnalyzer(df)
results = analyzer.calculate_metrics()
print(results.to_markdown(index=False))