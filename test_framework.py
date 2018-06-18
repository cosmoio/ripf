#!/usr/bin/python

import logging, getopt, ast
import os, sys
import exrex # https://github.com/asciimoo/exrex
from Classes.description import Description
from Classes.parser import Parser
from Classes.test_executor import TestExecutor
import signal

debug = False
program_name = "  Yet Another (Tiny Rest) Testing Framework  "
program_end = "  END OF TEST  "
size = 90



def main():
    global debug
    global current_folder


    rows, columns = os.popen('stty size', 'r').read().split()
    size = int(columns)-10
    current_folder = os.getcwd()
    file_path = current_folder+"/"+"tests.desc"

    try:
        options, remainder = getopt.getopt(sys.argv[1:], 'g:adf:', ['group=',
                                                                   'debug',
                                                                   'all=',
                                                                    'file='
                                                                   ])
    except getopt.GetoptError as err:
        logging.error(err)
        sys.exit(2)

#    logging.debug('OPTIONS   :', options)

    group = None
    file = None
    for opt, arg in options:
        if opt in ('-g', '--group'):
            group = arg
            logging.debug("Setting testing groups to: "+group)
        elif opt in ('-a', '--all'):
            group = "all"
        elif opt in ('-d', '--debug'):
            debug = True
            logging.debug("Debug activated")
        elif opt in ('-f', '--file'):
            file = arg
    if group is None:
        print(program_name+"\n  Usage: [-a, --all] [-d, --debug] [-g groupname | all] [-f, --file]")
        sys.exit(-1)

    if debug:
        logging.root.setLevel(logging.DEBUG)
    else:
        logging.root.setLevel(logging.INFO)

    logging.basicConfig(filename=file, format='%(levelname)s:%(message)s', level=logging.DEBUG)

    logging.info("#"*size)
    logging.info(program_name.center(size,"#"))
    logging.info("#"*size)
    logging.info("\n\n\n")


    logging.debug("Opening "+file_path)
    parser = Parser(file_path)
    list_test_descriptions = parser.parse_tests()

    logging.info("[+] Starting Tests")

    if str(group) in "all":
        for description in list_test_descriptions:
            test_executor = TestExecutor(description)
            test_executor.run()
    else:
        for description in list_test_descriptions:
            if str(group) in description.test_group:
                test_executor = TestExecutor(description)
                test_executor.run()

    logging.info(program_end.center(size,"#"))



        
if __name__ == "__main__":
    main()
