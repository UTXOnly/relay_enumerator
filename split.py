# pylint: disable=C0301,C0114,C0115,W0718
# This line is longer than the maximum allowed length
# Missing module docstring
# Missing class docstring
# Catching too general exception Exception (broad-exception-caught)

import os
import gzip

GREEN = os.getenv('GREEN')
RED = os.getenv('RED')
RESET = os.getenv('RESET')
YELLOW = os.getenv('YELLOW')

# Define the input file name and output file names
INPUT_FILE = 'rockyou.txt'
OUTPUT_FILE1 = 'rockyou_1.txt.gz'
OUTPUT_FILE2 = 'rockyou_2.txt.gz'

# Determine the size of the input file
file_size = os.path.getsize(INPUT_FILE)
# Calculate the number of bytes to read from the input file for each output file
chunk_size = file_size // 2

try:
    with open(INPUT_FILE, 'rb') as f_in:
        # Read the first half of the input file and write it to the first output file
        print(f'{GREEN}Reading first {RESET}{chunk_size} {GREEN}bytes from {RESET}{INPUT_FILE}')
        with gzip.open(OUTPUT_FILE1, 'wb') as f_out1:
            f_out1.write(f_in.read(chunk_size))
            print(f'{GREEN}Writing {RESET} {chunk_size}{GREEN} bytes to {RESET} {OUTPUT_FILE1}')
        # Read the second half of the input file and write it to the second output file
        print(f'{GREEN}Reading second {RESET}{chunk_size}{GREEN} bytes from {RESET}{INPUT_FILE}')
        with gzip.open(OUTPUT_FILE2, 'wb') as f_out2:
            f_out2.write(f_in.read(chunk_size))
            print(f'{GREEN}Writing {RESET} {chunk_size}{GREEN} bytes to{RESET} {OUTPUT_FILE2}')
    # Print a message indicating that the splitting and compression is complete
    print(f'{GREEN}File splitting and compression complete.{RESET}')

except FileNotFoundError:
    print(f'{RED}Error: {RESET}{INPUT_FILE} {RED}not found.')

except Exception as e:
    print(f'{RED}Error: {RESET}{e}')
