import gzip

def combine_files():
    """
    Combine two gzipped files into a single uncompressed file.

    Reads the contents of 'rockyou_1.txt.gz' and 'rockyou_2.txt.gz' and combines them into a new file 'rockyou.txt'.
    The resulting file is uncompressed.

    Note: This function assumes that the input files are in the gzip format.

    Raises:
        IOError: If there is an error reading or writing the files.
    """
    try:
        with gzip.open('rockyou_1.txt.gz', 'rb') as f_in1:
            with gzip.open('rockyou_2.txt.gz', 'rb') as f_in2:
                with open('rockyou.txt', 'wb') as f_out:
                    f_out.write(f_in1.read())
                    f_out.write(f_in2.read())
    except IOError as caught_error:
        print(f"Error occurred while combining files: {str(caught_error)}")
