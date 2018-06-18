import sys, inspect
import ast
import requests
import logging
import exrex # https://github.com/asciimoo/exrex
from Classes.description import Description

class TestExecutor:
    def __init__(self, test_description):
        self.test_description = test_description

    def run(self):

        logging.debug(self.test_description.loop_cnt)
        for i in range(0, int(self.test_description.loop_cnt)):
            logging.info("Executing test: "+ self.test_description.name + ", " + str(i+1) + " of " + str(self.test_description.loop_cnt))
            logging.info("Description: " + self.test_description.description)
            logging.info("Test Location: " + self.test_description.service_location)
            logging.info("Expected result: " + self.test_description.expected_result)
            logging.info("Method: " + self.test_description.method)

            logging.debug("Params: "+ str(self.test_description.parameters))
            logging.debug("Variables: "+ str(self.test_description.var_names))
            logging.debug("Patterns: " + str(self.test_description.patterns))

            if not len(self.test_description.patterns) == len (self.test_description.var_names):
                logging.error("[-] Error: Could not execute test, variables and patterns are not equal")
                break;
            tmp_params = str(self.test_description.parameters)

            # Only interesting if we deal with patterns
            for i in range(len(self.test_description.var_names)):
                try:
                    pattern_instance = exrex.getone(self.test_description.patterns[i])
                    tmp_var = self.test_description.var_names[i]
                    tmp_var = "$"+tmp_var
                    logging.debug("pattern_instance:"+pattern_instance)
                    logging.debug("tmp_var:" + tmp_var)
                    logging.debug("tmp_params:" + tmp_params)
                    tmp_params = tmp_params.replace(tmp_var,pattern_instance)
                    logging.debug("tmp_params w. pattern instance" + tmp_params)
                except:
                    logging.error("[-] Error: when generating and mapping pattern instance to argument")

            try:
                tmp_params_dict = ast.literal_eval(tmp_params)
            except:
                logging.error("([-] Error: Could not create parameters, format seems to be corrupt.")
                logging.error("([-] Error: skipping test.")
                continue

            logging.info("Parameters: ")
            self.test_description.print_parameters()

            try:
                if "POST" in self.test_description.method:
                    payload = tmp_params_dict
                    r = requests.post(self.test_description.service_location, data=payload)

                    logging.info("Service Response:" +r.text)
                else:
                    logging.error("[-] Error: Method not implemented yet, skipping test")
            except:
                logging.error("[-] Test, " + self.test_description.name + " could not be executed.\n")
                sys.exit(-1)

            if self.test_description.expected_result in r.text:
               logging.debug("Result: "+r.text)
               logging.info("[+] Test " + self.test_description.name + " executed successfully")

            else:
                logging.error("[-] Test " + self.test_description.name + " did not execute successfully")

            logging.info("\n\n\n")
