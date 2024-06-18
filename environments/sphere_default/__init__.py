import numpy as np
from badger import environment
from badger.errors import BadgerNoInterfaceError


class Environment(environment.Environment):

    name = 'sphere_default'
    variables = {f'x{i}': [-1, 1] for i in range(20)}
    observables = ['f']

    # This one is not necessary since it's exactly the same as the default one
    # but it's a good practice to have it here
    def get_variables(self, variable_names: list[str]) -> dict:
        if not self.interface:
            raise BadgerNoInterfaceError

        return self.interface.get_values(variable_names)

    def set_variables(self, variable_inputs: dict[str, float]):
        if not self.interface:
            raise BadgerNoInterfaceError

        self.interface.set_values(variable_inputs)

        # Update the 'f' observable
        variables_all = self.interface.get_values(self.variables)
        x = np.array([variables_all[f'x{i}'] for i in range(20)])
        f = (x ** 2).sum()
        self.interface.set_value('f', f)

    # This one is not necessary since it's exactly the same as the default one
    # but it's a good practice to have it here
    def get_observables(self, observable_names):
        if not self.interface:
            raise BadgerNoInterfaceError

        return self.interface.get_values(observable_names)
