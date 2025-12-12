#!/bin/bash
# Fix gprMax output file naming issue
# gprMax with -n flag creates files like s_00011.out instead of s_0001.out

echo "Fixing .out file names..."

count=0
for out_file in s_*[0-9][0-9].out; do
    if [ -f "$out_file" ]; then
        # Extract the base name (e.g., s_00011 -> s_0001)
        # Remove duplicate digits: s_00011 -> s_0001
        base=$(basename "$out_file" .out)
        
        # Fix pattern: s_XXXYY -> s_XXXY where YY is duplicate of last digit
        # s_00011 -> s_0001, s_00022 -> s_0002, etc.
        if [[ $base =~ ^(s_[0-9]+)([0-9])\2$ ]]; then
            correct_name="${BASH_REMATCH[1]}${BASH_REMATCH[2]}.out"
            
            if [ "$out_file" != "$correct_name" ]; then
                mv "$out_file" "$correct_name"
                echo "  $out_file -> $correct_name"
                ((count++))
            fi
        fi
    fi
done

echo ""
echo "✅ Fixed $count file names"
