from datetime import datetime

from instance import instance_logging
from scene.abstract_scene import AbstractScene

log = instance_logging(__name__, 10)


class DaytimeScene(AbstractScene):
    def run(self):
        state = {'bri': 200, 'ct': 499, 'transitiontime': 6}

        hour = datetime.now().hour
        if hour >= 1:
            state.update({'bri': 10, 'ct': 499})
        if hour >= 7:
            state.update({'bri': 150, 'ct': 100})
        if hour >= 10:
            state.update({'bri': 230, 'ct': 100})
        if hour >= 18:
            state.update({'bri': 200, 'ct': 300})
        if hour >= 20:
            state.update({'bri': 150, 'ct': 400})
        if hour >= 22:
            state.update({'bri': 50, 'ct': 499})

        result = self._api().lights_state(self.event['id'], state)

        log.info(f'Hour: {hour}; Applied: {state}; Result: {result}')
