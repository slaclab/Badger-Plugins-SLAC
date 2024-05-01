import time
import numpy as np
from badger import environment
from badger.errors import BadgerInterfaceChannelError


class Environment(environment.Environment):

    name = 'sphere_epics'
    variables = {
        'SPHERE:X1': [-1, 1],
        'SPHERE:X2': [-1, 1],
    }
    observables = ['SPHERE:F']

    timeout: float = 3  # timeout in seconds

    def get_variables(self, variable_names: list[str]) -> dict:
        assert self.interface, 'Must provide an interface!'

        # Fetch the interface until all values are not None
        time_start = time.time()
        variable_outputs = self.interface.get_values(variable_names)
        while None in variable_outputs.values():
            time.sleep(0.1 * np.random.rand())
            time_elapsed = time.time() - time_start
            if time_elapsed > self.timeout:
                raise BadgerInterfaceChannelError

            variable_outputs = self.interface.get_values(variable_names)

        return variable_outputs
