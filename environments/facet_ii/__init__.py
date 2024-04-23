import time
import numpy as np
from badger import environment
from badger.errors import BadgerNotImplementedError


class Environment(environment.Environment):
    name = "facet_ii"
    variables = {
        "SIOC:SYS1:ML00:AO551": [-1.0, 1.7],  # - X sextupole 2145
        "SIOC:SYS1:ML00:AO556": [-0.4, 1.8],  # - Y sextupole 2145
        "SIOC:SYS1:ML00:AO501": [-0.5, 1.7],  # - X set sextupole 2165
        "SIOC:SYS1:ML00:AO506": [-2.25, 0.25],  # - Y set sextupole 2165
        "SIOC:SYS1:ML00:AO516": [-1.5, 0.7],  # X set sextupole 2335
        "SIOC:SYS1:ML00:AO521": [-0.8, 1.5],  # Y set sextupole 2335 (check)
        "SIOC:SYS1:ML00:AO566": [-1.6, 0.8],  # - X sextupole 2365
        "SIOC:SYS1:ML00:AO571": [-1.1, 1.3],  # - Y sextupole 2365
    }
    observables = ["eloss", "dmprad", "iprad", "blenl", "blenh", "eloss1"]

    # Env params
    readonly: bool = False
    n_samples: int = 10
    # use_check_var: bool = True  # if check var reaches the target value
    trim_delay: float = 3.0  # in second
    sample_delay: float = 0.1
    # fault_timeout: float = 5.0  # in second

    def get_bounds(self, variable_names):
        pass

    def get_variables(self, variable_names: list[str]) -> dict:
        assert self.interface, "Must provide an interface!"

        channel_names = []
        for v in variable_names:
            if v.endswith(":BCTRL"):
                prefix = v[: v.rfind(":")]
                readback = prefix + ":BACT"
            else:
                readback = v
            channel_names.append(readback)
        channel_outputs = self.interface.get_values(channel_names)

        variable_outputs = {
            v: channel_outputs[channel_names[i]] for i, v in
            enumerate(variable_names)
        }

        return variable_outputs

    def set_variables(self, variable_inputs: dict[str, float]):
        assert self.interface, "Must provide an interface!"

        self.interface.set_values(variable_inputs)

        # if not self.use_check_var:
        if self.trim_delay:
            time.sleep(self.trim_delay)  # extra time for stablizing orbits

    def get_observables(self, observable_names: list[str]) -> dict:
        assert self.interface, "Must provide an interface!"

        # Make sure machine is not in a fault state
        # self.check_fault_status()

        # measure all of the things
        # specifically measure multiple samples of several observables and
        # then take the mean

        observable_outputs = {}

        data = []
        for _ in range(self.n_samples):
            data += [self._get_single_sample()]
            time.sleep(self.sample_delay)

        data = np.mean(np.array(data), axis=-1)

        all_outputs = {
            "eloss": data[-3],
            "denerg": data[-2],
            "iprad": data[-5] / 1e5,
            "dmprad": data[-4] / 1e5,
            "blen": data[-1],
            "blenh": data[-1],
            "blenl": data[-1],
            "eloss1": data[-3],
        }
        # print(all_outputs)

        try:
            observable_outputs = {
                key: all_outputs[key] for key in observable_names
            }
        except KeyError:
            raise BadgerNotImplementedError

        return observable_outputs

    def _get_single_sample(self):
        valid = False
        ts = 0
        datarec = None
        while not valid:
            data_dict = self.interface.get_values(self.pv_name_list)
            datarec = [data_dict[pv] for pv in self.pv_name_list]
            if datarec[-1] > 3100:
                if datarec[-1] < 3600:
                    valid = True
                else:
                    ts = ts + 1
            else:
                ts = ts + 1
            if ts > 10:
                break

        return datarec

    @property
    def pv_name_list(self):
        return [
            "SIOC:SYS1:ML00:AO502",  # - X LVDT sextupole 2165
            "SIOC:SYS1:ML00:AO503",  # - X Pot sextupole 2165
            "SIOC:SYS1:ML00:AO507",  # - Y LVDT sextupole 2165
            "SIOC:SYS1:ML00:AO508",  # - Y Pot sextupole 2165
            "SIOC:SYS1:ML00:AO552",  # - X LVDT sextupole 2145
            "SIOC:SYS1:ML00:AO553",  # - X Pot sextupole 2145
            "SIOC:SYS1:ML00:AO557",  # - Y LVDT sextupole 2145
            "SIOC:SYS1:ML00:AO558",  # - Y Pot sextupole 2145
            "SIOC:SYS1:ML00:AO517",  # - X LVDT sextupole 2335
            "SIOC:SYS1:ML00:AO518",  # - X Pot sextupole 2335
            "SIOC:SYS1:ML00:AO522",  # - Y LVDT sextupole 2335
            "SIOC:SYS1:ML00:AO523",  # - Y Pot sextupole 2335
            "SIOC:SYS1:ML00:AO567",  # - X LVDT sextupole 2365
            "SIOC:SYS1:ML00:AO568",  # - X Pot sextupole 2365
            "SIOC:SYS1:ML00:AO572",  # - Y LVDT sextupole 2365
            "SIOC:SYS1:ML00:AO573",  # - Y Pot sextupole 2365
            "SIOC:SYS1:ML00:AO551",  # - X sextupole 2145
            "SIOC:SYS1:ML00:AO556",  # - Y sextupole 2145
            "SIOC:SYS1:ML00:AO501",  # - X set sextupole 2165
            "SIOC:SYS1:ML00:AO506",  # - Y set sextupole 2165
            "SIOC:SYS1:ML00:AO516",  # X set sextupole 2335
            "SIOC:SYS1:ML00:AO521",  # Y set sextupole 2335 (check)
            "SIOC:SYS1:ML00:AO566",  # - X sextupole 2365
            "SIOC:SYS1:ML00:AO571",  # - Y sextupole 2365
            "BPMS:LI20:2147:X57",  # for S1EL
            "BPMS:LI20:2160:X57",  # for S2EL 2165
            "BPMS:LI20:2340:X57",  # for S2ER
            "BPMS:LI20:2360:X57",  # for S1ER
            "BPMS:LI20:2147:Y57",  # for S1ELß
            "BPMS:LI20:2160:Y57",  # for S2EL 2165
            "BPMS:LI20:2340:Y57",  # for S2ER
            "BPMS:LI20:2360:Y57",  # for S1ER
            "BPMS:LI20:2147:TMIT57",  # for S1EL
            "BPMS:LI20:2160:TMIT57",  # for S2EL 2165
            "BPMS:LI20:2340:TMIT57",  # for S2ER
            "BPMS:LI20:2360:TMIT57",  # for S1ER
            "TCAV:LI20:2400:ADES",
            "TCAV:LI20:2400:PDES",
            "RADM:LI20:1:CH01:MEAS",  # ip rad
            "RADM:LI20:2:CH01:MEAS",  # dump rad
            "SIOC:SYS1:ML02:AO531",  # total e loss : maximized
            "SIOC:SYS1:ML02:AO530",  # max decelerated energy : minimize
            "BLEN:LI14:888:BZ14888B_S_SUM",  # bc14 blen readback, 3800 +/- 200
        ]

    # def check_fault_status(self):
    # assert self.interface, 'Must provide an interface!'

    # ts_start = time.time()
    # while True:
    #    rate_MPS = self.interface.get_value('IOC:BSY0:MP01:PC_RATE',
    #                                        as_string=True)
    #    permit_BCS = self.interface.get_value('BCS:MCC0:1:BEAMPMSV',
    #                                          as_string=True)

    #    if (rate_MPS == '120 Hz') and (permit_BCS == 'OK'):
    #        break
    #    else:
    #        ts_curr = time.time()
    #        dt = ts_curr - ts_start
    #        if dt > self.fault_timeout:
    #            raise BadgerEnvObsError

    #       time.sleep(0.1)
