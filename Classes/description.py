import logging

class Description:
    def __init__(self, id, name, description, method,
                 service_location, parameters, test_group, expected_result,
                 var_names, patterns, loop_cnt):
        self.id = id if id is not None else "NOT SET"
        self.name = name if name is not None else "NOT SET"
        self.description = description if description is not None else "NOT SET"
        self.method = method if method is not None else "NOT SET"
        self.service_location = service_location if service_location is not None else "NOT SET"
        self.parameters = dict(parameters) if dict(parameters) is not None else dict()
        self.test_group = test_group if test_group is not None else "NOT SET"
        self.expected_result = expected_result if expected_result is not None else "NOT SET"
        self.var_names = list(var_names) if list(var_names) is not None else []
        self.patterns = list(patterns) if list(patterns) is not None else []
        self.loop_cnt = loop_cnt

    def __str__(self):
        return str(self.test_group) + "\n " + \
               str(self.id) + "\n " + \
               str(self.name) + "\n " + \
               str(self.description) + "\n " + \
               str(self.method) + "\n " + \
               str(self.service_location) + "\n " + \
               str(self.parameters) + "\n " + \
               str(self.expected_result) + "\n" + \
               str(self.loop_cnt) + "\n" + \
               str(self.var_names) + "\n" + \
               str(self.parameters) + "\n"

    def print_parameters(self):
        for key, value in self.parameters.items():
            if len(value) < 1000:
                logging.info(key + " " +value)
            else:
                logging.info("parameters are too long.. reducing output")
                logging.info((key) + " " + value[:1000])

        # @property
        # def id(self):
        #     return self.id
        #
        # @id.setter
        # def id(self, id):
        #     self.id = id
