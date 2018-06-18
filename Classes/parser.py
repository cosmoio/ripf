import sys, logging
import ast
import exrex # https://github.com/asciimoo/exrex
from Classes.description import Description


class Parser:
    def __init__(self, file_path):
        self.file_path = file_path

    def parse_tests(self):
        try:
            tests_file = open(self.file_path, "r")
        except:
            logging.error("[-] Error: Check your test description file path.\n")
            sys.exit(1)

        lines = tests_file.readlines()
        logging.debug(str(len(lines)) + " line numbers loaded...")

        parameter_parsing = False
        error_level = 0
        id = None
        name = None
        description_text = None
        method = None
        service_location = None
        call_parameters = None
        list_test_descriptions = []
        tmp_param = ""
        test_group = ""
        expected_result = ""
        loop_cnt = 1
        var_names = []
        patterns = []

        # walk over lines
        # find @Test group
        # find [TEST and #]
        # find Name = remove ""
        # find Service Location = remove ""
        # find Parameters = remove [ ]
        # find Expected Result = remove ""
        # find Description = ""
        # any of those not found, raise error

        # Linear descent parser (1 lookahead)
        for i in range(len(lines)):
            line = lines[i].strip()
            if line.startswith("#"):
                logging.debug("Comment: " + line)
                continue

            # Test group parsing
            elif line.startswith("@"):
                test_group = line[1:]
                continue

            # Test header
            elif line.startswith("[") and line.endswith("]"):
                line = line.replace("[", '')
                line = line.replace("]", '')
                id = line
                logging.debug("Test ID: " + id)

            # Name = "Test 1"
            elif "Name =" in line and not parameter_parsing:
                token = line.split("=")
                name = token[1]
                name = name.strip(' "')
                logging.debug("Test Name: " + name)

            elif "Service Location =" in line and not parameter_parsing:
                token = line.split("=")
                service_location = token[1]
                service_location = service_location.strip(' "')
                logging.debug("Service Location: " + service_location)

            elif "Method =" in line and not parameter_parsing:
                token = line.split("=")
                method = token[1]
                method = method.strip(' "')
                logging.debug("Method: " + method)

            elif "Description =" in line and not parameter_parsing:
                token = line.split("=")
                description_text = token[1]
                description_text = description_text.strip(' "')
                logging.debug("Description: " + description_text)

            elif "Expected Result =" in line and not parameter_parsing:
                token = line.split("=")
                expected_result = token[1]
                expected_result = expected_result.strip(' "')
                logging.debug("Expected Result: " + expected_result)

            elif line.startswith("Loop ="):
                token = line.split("=")
                loop_cnt = token[1].strip(' "')
                logging.debug("Loop counter: " + loop_cnt)
                try:
                    loop_cnt = int(loop_cnt)
                except:
                    logging.error("Your loop counter is not a number, setting loop_cnt = 1")
                    loop_cnt = 1
            elif line.startswith("rand_var"):
                var_name = ""
                pattern = ""
                var_name = line[len("rand_var"):]
                if "[" in var_name and var_name.endswith("]"):
                    token = var_name.split("=")
                    var_name = token[0].strip()
                    pattern = token[1].strip()
                    pattern = pattern[1:-1]
                    logging.debug("var_name: " + var_name)
                    logging.debug("pattern: " + pattern)
                    try:
                        exrex.getone(pattern)
                    except:
                        logging.error("Error while parsing your regular expression, defaulting to \"NOT SET\"")
                        pattern = "NOT SET"
                    var_names.append(var_name)
                    patterns.append(pattern)
                else:
                    logging.error("Variable: " + var_name + " has wrong format, no regex component")

            elif "Parameters =" in line or parameter_parsing:
                logging.debug("Parsing Parameters")
                if not parameter_parsing:
                    tokens = line.split("=")
                    parameter = tokens[1].lstrip()      # actual argument   # remove beginning spaces
                    if not parameter.startswith("["):  # is the argument formatted correctly?
                        error_level = 3
                        break

                    tmp_param = parameter[1:]
                    if not line.endswith("]"):
                        parameter_parsing = True
                        continue
                    tmp_param = tmp_param[:-1]
                    # print "Last parameter"
                    parameter_parsing = False
                    call_parameters = tmp_param
                    if id is None or name is None or method is None or service_location is None or call_parameters is None:
                        logging.error("Parse error, not all nonterminals set")
                        break
                    call_parameters = call_parameters.replace("\"", "\\\"")
                    call_parameters = "{" + call_parameters + "}"
                    call_parameters = ast.literal_eval(call_parameters)
                    logging.debug("call_parameters:"+ str(call_parameters))
                    list_test_descriptions = self.add_description(list_test_descriptions, id, name,
                                                                  description_text, method, service_location,
                                                                  call_parameters, test_group, expected_result,
                                                                  loop_cnt, var_names, patterns)
                    # print call_parameters
                else:
                    line = line.strip(' \n\t')
                    tmp_param += line
                    # print "Parameters: "+tmp_param
                    if line.endswith("]"):
                        tmp_param = tmp_param[:-1]
                        # print "Last parameter"
                        parameter_parsing = False
                        call_parameters = tmp_param
                        if id is None or name is None or method is None or service_location is None or call_parameters is None:
                            logging.error("Parse error, not all nonterminals set")
                            break
                        call_parameters = call_parameters.replace("\"", "\\\"")
                        call_parameters = "{" + call_parameters + "}"
                        try:
                            call_parameters = ast.literal_eval(call_parameters)
                        except:
                            logging.error("Error while parsing your arguments, not in correct format.")
                            error_level = 4
                            break
                        list_test_descriptions = self.add_description(list_test_descriptions, id, name,
                                                                      description_text, method, service_location,
                                                                      call_parameters, test_group, expected_result,
                                                                      loop_cnt, var_names, patterns)
                    elif line.endswith(','):
                        continue
                    else:
                        error_level = 2
                        break
        if error_level == 1:
            logging.error("Parse error on line " + str(i) + ": Should end with ','")
            logging.debug("Causing Line: " + lines[i])
        elif error_level == 2:
            logging.error("Parse error on line " + str(i) + ": Parameters could not be parsed end tag ']' missing?")
            logging.debug("Causing Line: " + lines[i])
        elif error_level == 3:
            logging.error("Parse error on line " + str(i) + ": No initializing '[' while parsing arguments")
            logging.debug("Causing Line: " + lines[i])
        elif error_level == 4:
            logging.error("Parse error on line " + str(i) + ": Parameters in wrong format, missing "'"?')
            logging.debug("Causing Line: " + lines[i])
        return list_test_descriptions

    def add_description(self, list_test_descriptions, id, name, description_text, method, service_location,
                        call_parameters, test_group, expected_result, loop_cnt, var_names, patterns):
        description = Description(id, name, description_text, method, service_location, call_parameters, test_group,
                                  expected_result, var_names, patterns, loop_cnt)
        list_test_descriptions.append(description)
        logging.debug("Parsed " + id + " correctly")

        #id = None
        #name = None
        #description = None
        #method = None
        #service_location = None
        call_parameters.clear()
        #tmp_param = ""
        #test_group = ""
        #expected_result = ""
        del var_names[:]
        del patterns[:]
        #loop_cnt = 1
        # del var_names[:]

        return list_test_descriptions
