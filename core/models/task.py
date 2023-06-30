import os
import subprocess
import yaml
from copy import deepcopy
from yaml.loader import SafeLoader
from time import sleep

from core.models.param import Param
from core.models.step import Step


class Task:
    def __init__(self, filepath):
        if not os.path.isfile(filepath) and not (filepath.endswith(".yml") or filepath.endswith(".yaml")):
            raise Exception("Task only accepts yaml files, .yml or .yaml")

        with open(filepath, 'r') as fi:
            self._raw = yaml.load(fi, SafeLoader)

        self.description = self._raw["metadata"].get("description", "No description")
        self.name = self._raw["metadata"]["name"]

        self._parse_params()
        self._parse_steps()

    def run(self, param_values):
        param_values_merged = {}
        for param_name, param_obj in self._params.items():
            if param_obj.value is not None:
                param_values_merged[param_name] = param_obj.value

        param_values_merged.update(param_values)

        for step_name in self._step_order:
            step = self._steps[step_name]
            command = step.command(self._params, param_values_merged)
            print("\nRunning step: ", step_name)
            os.chdir(step.working_dir)
            proc = subprocess.Popen(command, bufsize=0, stdout=subprocess.PIPE)
            for line in iter(proc.stdout.readline, b''):
                print("outs:", line.decode('utf-8')[:-1])

            proc.stdout.close()
            proc.wait()
            ret_code = proc.returncode

            print("Finished step: ", step_name, "with exit code", ret_code)

    def _parse_params(self):
        params = self._get('spec.params', [])
        if not params:
            return
            
        self._params = {}
        for param in params:
            self._params[param["name"]] = Param(param["name"], type=param["type"], default=param.get("default", None), description=param.get("description", None))

    def _parse_steps(self):
        steps = self._get('spec.steps', [])
        
        if not steps:
            raise Exception("Task must have at least one step")

        self._steps = {}
        self._step_order = []

        for step in steps:
            self._steps[step["name"]] = Step(**step)
            self._step_order.append(step["name"])

    def _get(self, path, default=None):
        path_steps = path.strip().split('.')

        if not path_steps:
            return None

        try:
            returned = deepcopy(self._raw)
            for path_step in path_steps:
                if path_step.startswith('[') and path_step.endswith(']'):
                    path_step = int(path_step.replace('[', '').replace(']', ''))
                returned = returned[path_step]
        except:
            return default

        return returned
