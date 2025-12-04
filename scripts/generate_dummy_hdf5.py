import h5py
import numpy as np

def create_dummy_hdf5(filename='test_gprmax.h5'):
    with h5py.File(filename, 'w') as f:
        # Set root attributes
        f.attrs['gprMax'] = '3.1.5'
        f.attrs['Title'] = 'Simulation of a buried pipe'
        f.attrs['Iterations'] = 1000
        f.attrs['nx_ny_nz'] = (100, 100, 100)
        f.attrs['dx_dy_dz'] = (0.01, 0.01, 0.01)
        f.attrs['dt'] = 1e-11
        f.attrs['srcsteps'] = (0.05, 0.0, 0.0)
        f.attrs['rxsteps'] = (0.05, 0.0, 0.0)
        f.attrs['nsrc'] = 2
        f.attrs['nrx'] = 2

        # Create groups
        srcs = f.create_group('srcs')
        tls = f.create_group('tls')
        rxs = f.create_group('rxs')

        # Create subgroups for sources
        src1 = srcs.create_group('src1')
        src1.attrs['Type'] = 'Hertzian Dipole'
        src2 = srcs.create_group('src2')
        src2.attrs['Type'] = 'Hertzian Dipole'

        # Create subgroups for receivers
        rx1 = rxs.create_group('rx1')
        rx1.create_dataset('Ex', data=np.random.rand(1000))
        rx2 = rxs.create_group('rx2')
        rx2.create_dataset('Ex', data=np.random.rand(1000))

        # Create subgroups for transmission lines (optional, just for structure)
        tl1 = tls.create_group('tl1')

    print(f"Created dummy file: {filename}")

if __name__ == "__main__":
    create_dummy_hdf5()
