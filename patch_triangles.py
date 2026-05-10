import re
import sys

def main():
    path = r'd:\Codigo\Synth-GPR.bck\Synth-GPR-1\output_test\angular_rocks_400MHz.in'
    with open(path, 'r') as f:
        t = f.read()
    
    t = re.sub(r'^(#triangle: .*) (bal_rock)$', r'\1 0.0132 \2', t, flags=re.MULTILINE)
    
    with open(path, 'w') as f:
        f.write(t)
    print("Patched triangles")

if __name__ == '__main__':
    main()
