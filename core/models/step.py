from copy import copy
import os

class Step:
    def __init__(self, name=None, workingDir=None, binary=None, args=None):
        self.name = name

        if not os.path.isdir(workingDir):
            raise Exception("Step workingDir must be an existing directory")

        self.workingDir = workingDir
        self.working_dir = workingDir
        self.binary = binary

        if not os.path.isfile(self.binary_path):
            raise Exception("Step workingDir/binary must be an existing file")

        self.args = args
        self._command_template = self._parse_args()

    def command(self, params, param_values):
        param_values_names = set(param_values.keys())
        param_names = set(params.keys())
        param_names_without_default = set(param for param in params.keys() if params[param].value is None)

        if not param_names_without_default.issubset(param_values_names):
            raise Exception(f"Param values for all the parameters defined in spec is required", param_names)

        value_injected_params = {}
        for param_name in param_values:
            value_injected_params[param_name] = params[param_name].inject_value(param_values[param_name], copy=True)


        command = copy(self._command_template)
        for param_name in value_injected_params:
            replace_operations = []
            value = value_injected_params[param_name].value
            if value_injected_params[param_name].type.lower().endswith("path"):
                value = value_injected_params[param_name].value
                replace_string = "${params." + param_name + ".basename}"
                value = f'{os.path.basename(value)}'
                replace_operations.append((replace_string, value))

                value = value_injected_params[param_name].value
                replace_string = "${params." + param_name + ".basename_noext}"
                value = f'{os.path.splitext(os.path.basename(value))[0]}'
                replace_operations.append((replace_string, value))
                
                value = value_injected_params[param_name].value
                replace_string = "${params." + param_name + ".dirname}"
                value = f'{os.path.dirname(value)}'
                replace_operations.append((replace_string, value))

                value = value_injected_params[param_name].value
                replace_string = "${params." + param_name + ".extension}"
                value = f'{os.path.splitext(value)[-1]}'
                replace_operations.append((replace_string, value))
                
                value = value_injected_params[param_name].value
                replace_string = "${params." + param_name + "}"
                value = f'{value}'
                replace_operations.append((replace_string, value))
            else:
                replace_string = "${params." + param_name + "}"
                replace_operations.append((replace_string, value))

            for replace_text, replace_value in replace_operations:
                command = command.replace(replace_text, replace_value)

        if '${' in command:
            raise Exception("All expressions could not be substituted. Check you have passed all the params", command)
                
        return command

    @property
    def binary_path(self):
        return os.path.join(self.workingDir, self.binary)

    def _parse_args(self):
        command = f"{self.binary}"
        for arg in self.args:
            command += " " + arg

        return command
