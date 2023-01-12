# argvhelper.py

# A Python command line args helper class. Entirely worse than argparse.py!

import sys

class ParamType:
    # Integer number
    # Float number
    # String
    
    def __init__(self, is_valid_delegate, convert_value_delegate):
        self.__is_valid_delegate = is_valid_delegate
        self.__convert_value_delegate = convert_value_delegate
    
    def is_valid(self, str) -> bool:
        return self.__is_valid_delegate(str)
    
    def convert_value(self, str):
        return self.__convert_value_delegate(str)

def __is_int(str):
    try:
        int(str)
        return True
    except:
        return False

def __is_float(str):
    try:
        float(str)
        return True
    except:
        return False

NoValueParam = ParamType(None, None)
IntParam = ParamType(__is_int, lambda s: int(s))
FloatParam = ParamType(__is_float, lambda s: float(s))
StringParam = ParamType(lambda _: True, lambda s: s)

class Param:
    def __init__(self, name:str, type:ParamType):
        self.name = name
        self.param_type = type

class RequiredParam(Param):
    pass

class OptionalParam(Param):
    def __init__(self, name:str, type:ParamType, value_count:int, flag:str):
        self.flag = flag
        self.value_count = value_count
        super().__init__(name, type)

class ArgsHelper:
    def __is_at_end(self) -> bool:
        return self.__current_index >= self.argc

    def __advance(self) -> str:
        self.__current_index += 1
        if not self.__is_at_end():
            return sys.argv[self.__current_index]
        return None

    def __get_param_values(self, param:OptionalParam) -> list:
        param_values = []
        for _ in range(param.value_count):
            param_value_str = self.__advance()
            if param_value_str and param.param_type.is_valid(param_value_str):
                param_values.append(param.param_type.convert_value(param_value_str))
        
        return param_values

    def __fail(self, msg:str):
        self.result_msg = msg
        self.success = False
    
    def __init__(self, required_params:list, optional_params:list, dropped_early_arg_count:int = 1, flag_prefix:str = '-'):
        self.result_msg = "Incomplete"
        self.success = False
        
        self.required_params = required_params
        self.optional_params = optional_params
        self.dropped_early_arg_count = dropped_early_arg_count  # For dropping the script name from the arguments.
        self.__flag_prefix = flag_prefix

        self.argc = len(sys.argv)

        self.__current_index = dropped_early_arg_count - 1
        self.arg_dict = dict()

        # Get required params.
        for param in self.required_params:
            param_str = self.__advance()
            if param_str:
                if param.param_type.is_valid(param_str):
                    self.arg_dict[param.name] = param.param_type.convert_value(param_str)
                else:
                    self.__fail(f"\"{param_str}\" is not valid for parameter \"{param.name}\"")
                    return
            else:
                self.__fail(f"Missing required parameter \"{param.name}\"")
                return

        # Get optional params.
        while not self.__is_at_end():
            param_flag = self.__advance()

            if not param_flag:
                # No more optional params.
                break
            elif not param_flag.startswith(self.__flag_prefix):
                # Optional flag doesn't start with flag prefix.
                self.__fail(f"Unexpected argument: \"{param_flag}\". Expected: flag beginning with \"{self.__flag_prefix}\", or end of arguments")
                return
            
            # Strip off the flag prefix.
            param_flag = param_flag.lstrip(self.__flag_prefix)

            # Find the first optional param with that flag.
            param = next(p for p in self.optional_params if p.flag == param_flag)
            if param:
                # If the param has no user-supplied values (just a flag),
                if param.value_count == 0:
                    # The flag has been set.
                    self.arg_dict[param.name] = []
                # If the param has some number of user-supplied values,
                else:
                    # Read up to that many args as values for the param.
                    param_values = self.__get_param_values(param)
                    
                    # If the expected number of values were provided,
                    if param_values and len(param_values) == param.value_count:
                        # The values have been collected.
                        self.arg_dict[param.name] = param_values
                    # If there were an unexpected number of values,
                    else:
                        self.__fail(f"Insufficient number of arguments ({0 if not param_values else len(param_values)}) provided for parameter \"{param.name}\". Expected: {param.value_count}")
                        return
            else:
                # No optional param with that flag.
                self.__fail(f"Unrecognized flag: \"{param_flag}\"")
                return
        
        # Things worked out alright.
        self.result_msg = "Success"
        self.success = True
    
    def get_value_list(self, param_name:str) -> list:
        if param_name in self.arg_dict.keys():
            return self.arg_dict[param_name]
        return None
    
    def is_set(self, param_name:str) -> bool:
        if param_name in self.arg_dict.keys():
            return self.arg_dict[param_name] != None
        return False

# def __console_program():
#     ah = ArgsHelper([RequiredParam("first", IntParam), RequiredParam("second", FloatParam)], [OptionalParam("third", NoValueParam, 0, '3'), OptionalParam("fourth", StringParam, 2, '4')])
#     print(f"Success = {ah.success}")
#     print(f"Result Message = {ah.result_msg}.")
#     print(f"first = {ah.get_value_list('first')}")
#     print(f"second = {ah.get_value_list('second')}")
#     print(f"third = {ah.is_set('third')}")
#     print(f"fourth = {ah.get_value_list('fourth')}")

# __console_program()