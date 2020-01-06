#!/usr/bin/env python3

import string
import random

# number of records
N = 1000

for i in range(N):
    # name as 12 random lower-ascii characters
    name = "".join(random.choices(string.ascii_lowercase, k=12))

    # age as 1 .. 99
    age = random.randrange(1, 100)
    print("{}, {}".format(name, age))
