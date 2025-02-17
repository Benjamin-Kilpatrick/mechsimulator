""" Runs one or more job files

    Example: python run.py jobfile1 jobfile2 ...
    BK_USED
"""
import os
import sys

assert len(sys.argv) > 1, 'At least one input must be given!'
print(os.getcwd())
JOB_FILES = sys.argv[1:]
main.run_jobs(JOB_FILES)
