import gzip

with gzip.open('rockyou_1.txt.gz', 'rb') as f_in1:
    with gzip.open('rockyou_2.txt.gz', 'rb') as f_in2:
        with open('rockyou.txt', 'wb') as f_out:
            f_out.write(f_in1.read())
            f_out.write(f_in2.read())
