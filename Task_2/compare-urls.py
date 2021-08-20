#!/usr/bin/env python3
import sys
from comparator import HttpComparator
from datastream import DataGenerator, Processor

class App:
    def run(self, filename_a, filename_b):
        data_generator = DataGenerator()
        processor = Processor(cmp=HttpComparator(check_headers=False))

        for (a, b, res) in processor.run(data_generator.file_product(filename_a, filename_b)):
            if res is None:
                print(f"Error comparing {a} and {b}")
                continue

            if res:
                print(f"{a} equals {b}")
            else:
                print(f"{a} not equals {b}")

if len(sys.argv) < 3:
    print(f"Usage: {sys.argv[0]} file_a file_b")
    exit(1)

app = App()
app.run(sys.argv[1], sys.argv[2])