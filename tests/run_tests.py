import subprocess as sp
import os
import argparse

def get_args():
    parser = argparse.ArgumentParser(description='Run test suite for devlprd')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enables lots of prints from within each test. Gives a better idea of what is going on', default=False)
    # parser.add_argument('-s', '--silent', action='store_true', help='Only prints when something goes wrong') TODO
    return parser.parse_args()

# Custom run script because using unittest discover causes a weird multithreading issue.
if __name__ == '__main__':
    args = get_args()
    results = dict()
    failure = False
    files = [f for f in os.listdir() if "_test.py" in f]
    for file in files:
        print("Running: {}".format(file))
        ret = sp.run('python {}'.format(file), capture_output=(not args.verbose))
        results[file] = ret.returncode


    print("----Summary----")
    for test,result in results.items():
        if result != 0:
            res_str = "FAIL"
            failure = True
        else:
            res_str = "PASS"
        print("[{}] {}".format(res_str, test))

    exit(1 if failure else 0)