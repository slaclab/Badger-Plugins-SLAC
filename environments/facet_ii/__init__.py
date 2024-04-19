import logging
import time
from typing import Dict, List

import numpy as np
from badger import environment


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
    # stats: str = 'percent_80'
    # use_check_var: bool = True  # if check var reaches the target value
    trim_delay: float = 3.0  # in second
    sample_delay: float = 0.1
    # fault_timeout: float = 5.0  # in second

    def get_bounds(self, variable_names):
        pass

    def get_variables(self, variable_names: List[str]) -> Dict:
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
            v: channel_outputs[channel_names[i]] for i, v in enumerate(variable_names)
        }

        return variable_outputs

    def set_variables(self, variable_inputs: Dict[str, float]):
        assert self.interface, "Must provide an interface!"

        self.interface.set_values(variable_inputs)

        # if not self.use_check_var:
        if self.trim_delay:
            time.sleep(self.trim_delay)  # extra time for stablizing orbits

    def get_observables(self, observable_names: List[str]) -> Dict:
        assert self.interface, "Must provide an interface!"

        # Make sure machine is not in a fault state
        # self.check_fault_status()

        # measure all of the things
        # specifically measure multiple samples of several observables and then take
        # the mean

        data = []
        for i in range(self.n_samples):
            data += [self._get_single_sample()]
            time.sleep(self.sample_delay)

        data = np.mean(np.array(data), axis=-1)

        observable_outputs = {
            "eloss": data[-3],
            "denerg": data[-2],
            "iprad": data[-5] / 1e5,
            "dmprad": data[-4] / 1e5,
            "blen": data[-1],
            "blenh": data[-1],
            "blenl": data[-1],
            "eloss1": data[-3],
        }

        print(observable_outputs)

        return observable_outputs

    def _get_single_sample(self):
        valid = False
        ts = 0
        datarec = None
        while not valid:
            datarec = epics.caget_many(self.pv_name_list)
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
            "SIOC:SYS1:ML00:AO552",  #  - X LVDT sextupole 2145
            "SIOC:SYS1:ML00:AO553",  #  - X Pot sextupole 2145
            "SIOC:SYS1:ML00:AO557",  # - Y LVDT sextupole 2145
            "SIOC:SYS1:ML00:AO558",  # - Y Pot sextupole 2145
            "SIOC:SYS1:ML00:AO517",  #  - X LVDT sextupole 2335
            "SIOC:SYS1:ML00:AO518",  #  - X Pot sextupole 2335
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

    # def get_system_states(self):
    #     assert self.interface, 'Must provide an interface!'
    #
    #     ignore_small_value = lambda x: x if x > 10 else 0
    #
    #     general_pvs = [
    #         'BEND:DMPH:400:BDES',
    #         'SIOC:SYS0:ML00:AO627',
    #         'BEND:DMPS:400:BDES',
    #         'SIOC:SYS0:ML00:AO628',
    #         # 'IOC:IN20:EV01:RG02_DESRATE',  # this one has to be treated specifically
    #         'SIOC:SYS0:ML00:CALC038',
    #         'SIOC:SYS0:ML00:CALC252',
    #         'BPMS:DMPH:693:TMITCUH1H',
    #         'BPMS:DMPS:693:TMITCUS1H',
    #     ]
    #     matching_quads = [
    #         'QUAD:IN20:361:BCTRL',
    #         'QUAD:IN20:371:BCTRL',
    #         'QUAD:IN20:425:BCTRL',
    #         'QUAD:IN20:441:BCTRL',
    #         'QUAD:IN20:511:BCTRL',
    #         'QUAD:IN20:525:BCTRL',
    #         'QUAD:LI21:201:BCTRL',
    #         'QUAD:LI21:211:BCTRL',
    #         'QUAD:LI21:271:BCTRL',
    #         'QUAD:LI21:278:BCTRL',
    #         'QUAD:LI26:201:BCTRL',
    #         'QUAD:LI26:301:BCTRL',
    #         'QUAD:LI26:401:BCTRL',
    #         'QUAD:LI26:501:BCTRL',
    #         'QUAD:LI26:601:BCTRL',
    #         'QUAD:LI26:701:BCTRL',
    #         'QUAD:LI26:801:BCTRL',
    #         'QUAD:LI26:901:BCTRL',
    #         'QUAD:LTUH:620:BCTRL',
    #         'QUAD:LTUH:640:BCTRL',
    #         'QUAD:LTUH:660:BCTRL',
    #         'QUAD:LTUH:680:BCTRL',
    #         'QUAD:LTUS:620:BCTRL',
    #         'QUAD:LTUS:640:BCTRL',
    #         'QUAD:LTUS:660:BCTRL',
    #         'QUAD:LTUS:680:BCTRL',
    #         'QUAD:LI21:221:BCTRL',
    #         'QUAD:LI21:251:BCTRL',
    #         'QUAD:LI24:740:BCTRL',
    #         'QUAD:LI24:860:BCTRL',
    #         'QUAD:LTUH:440:BCTRL',
    #         'QUAD:LTUH:460:BCTRL',
    #         'QUAD:IN20:121:BCTRL',
    #         'QUAD:IN20:122:BCTRL',
    #     ]
    #
    #     states_general = self.interface.get_values(general_pvs)
    #     states_quads = self.interface.get_values(matching_quads)
    #
    #     system_states = {
    #         'HXR electron energy [GeV]': states_general['BEND:DMPH:400:BDES'],
    #         'HXR photon energy [eV]': round(states_general['SIOC:SYS0:ML00:AO627']),
    #         'SXR electron energy [GeV]': states_general['BEND:DMPS:400:BDES'],
    #         'SXR photon energy [eV]': round(states_general['SIOC:SYS0:ML00:AO628']),
    #         'Rate [Hz]': self.interface.get_value('IOC:IN20:EV01:RG02_DESRATE', as_string=True),
    #         'Charge at gun [pC]': ignore_small_value(states_general['SIOC:SYS0:ML00:CALC038']),
    #         'Charge after BC1 [pC]': ignore_small_value(states_general['SIOC:SYS0:ML00:CALC252']),
    #         'Charge at HXR dump [pC]': ignore_small_value(states_general['BPMS:DMPH:693:TMITCUH1H'] * 1.602e-7),
    #         'Charge at SXR dump [pC]': ignore_small_value(states_general['BPMS:DMPS:693:TMITCUS1H'] * 1.602e-7),
    #     }
    #     system_states.update(states_quads)
    #
    #     return system_states
