#!/bin/bash
# Read the number from the file, add 1, format with leading zeros, and save it back
id=$(cat next_id)  # Replace next_id with your actual file
echo $id
next_id=$((10#$id + 1))  # Use 10# to treat it as a base-10 number
printf "%04d\n" $next_id > next_id
