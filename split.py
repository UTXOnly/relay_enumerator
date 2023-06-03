import os
import gzip

GREEN = '\033[32m'
RED = '\033[31m'
RESET = '\033[0m'


# Define the input file name and output file names
input_file = 'rockyou.txt'
output_file1 = 'rockyou_1.txt.gz'
output_file2 = 'rockyou_2.txt.gz'

# Determine the size of the input file
file_size = os.path.getsize(input_file)
#
# Calculate the number of bytes to read from the input file for each output file
chunk_size = file_size // 2

try:
    with open(input_file, 'rb') as f_in:
        # Read the first half of the input file and write it to the first output file
        print(f'{GREEN}Reading first {RESET}{chunk_size} {GREEN}bytes from {RESET}{input_file}')
        with gzip.open(output_file1, 'wb') as f_out1:
            f_out1.write(f_in.read(chunk_size))
            print(f'{GREEN}Writing {RESET} {chunk_size}{GREEN} bytes to {RESET} {output_file1}')
        
        # Read the second half of the input file and write it to the second output file
        print(f'{GREEN}Reading second {RESET}{chunk_size}{GREEN} bytes from {RESET}{input_file}')
        with gzip.open(output_file2, 'wb') as f_out2:
            f_out2.write(f_in.read(chunk_size))
            print(f'{GREEN}Writing {RESET} {chunk_size}{GREEN} bytes to{RESET} {output_file2}')
    
    # Print a message indicating that the splitting and compression is complete
    print(f'{GREEN}File splitting and compression complete.{RESET}')

except FileNotFoundError:
    print(f'{RED}Error: {RESET}{input_file} {RED}not found.')
    
except Exception as e:
    print(f'{RED}Error: {RESET}{e}')
