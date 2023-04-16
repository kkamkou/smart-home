from datetime import datetime

from instance import instance_logging
from scene.abstract_scene import AbstractScene

log = instance_logging(__name__, 10)


class DaytimeScene(AbstractScene):
    def run(self):
        state = {
            'bri': self.params.get('default_bri', 200),
            'ct': self.params.get('default_ct', 499),
            'transitiontime': self.params.get('default_transitiontime', 9)
        }

        hour = datetime.now().hour
        if hour >= 1:
            state.update({'bri': 10, 'ct': 370})
        if hour >= 7:
            state.update({'bri': 150, 'ct': 153})
        if hour >= 10:
            state.update({'bri': 230, 'ct': 153})
        if hour >= 18:
            state.update({'bri': 200, 'ct': 230})
        if hour >= 20:
            state.update({'bri': 150, 'ct': 300})
        if hour >= 22:
            state.update({'bri': 50, 'ct': 370})

        result = self._api().lights_state(self.event['id'], state)

        log.info(f'Hour: {hour}; Applied: {state}; Result: {result}')
