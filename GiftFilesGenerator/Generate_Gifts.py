#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

course_id = '001.2.5'
topic_count = 6
questions_count = 10

for t in range(1, topic_count+1, 1):
    filename = '{0}.{1}.gift'.format(course_id, t)
    if os.path.exists(filename):
        print("Skip. File already exist. {0}".format(filename))
        continue

    print("Generate {0}".format(filename))
    with open(filename, 'w', encoding="utf-8") as f:
        for q in range(1, questions_count + 1, 1):
            f.write('::{0}.{1}.{2}::? {{\n=\n~\n~\n~\n~\n}}\n\n'.format(course_id, t, q))
