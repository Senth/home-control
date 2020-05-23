from .tradfri_gateway import TradfriGateway, Lights, Groups
from .effect import Effects
from .info_wrapper import InfoWrapper
import logging
import threading
import time

logger = logging.getLogger(__name__)


class Executor:
    _threads = []

    def __init__(self, data):
        self._data = data
        self._lights_and_groups = []

        if self.needs_update():
            Lights.update()
            Groups.update()

        if self.is_light_or_group_action():
            self.get_light_and_groups()

    def get_light_and_groups(self):
        if 'name' in self._data:
            names = self._data['name'].split(';')
            for name in names:
                # Remove 'the ' that we get from IFTTT google assistant
                fixed_name = name.lower().replace('the', '')
                fixed_name = fixed_name.strip()

                light = Lights.find_light(fixed_name)
                if light:
                    self._lights_and_groups.append(light)
                    continue

                group = Groups.find_group(fixed_name)
                if group:
                    # Special case, moods can only handle one group
                    if 'mood' in self._data:
                        self._lights_and_groups = group
                        return

                    self._lights_and_groups.append(group)
                    continue

                logger.warning("Executor.get_light_and_groups() Didn't find device or group with name: " + name)

    def execute(self):
        # Special case for effects
        if 'effect' in self._data:
            self.create_effect_executor()
            return

        # Get function to call for the action
        function, args, kwargs = self.get_action_function()

        if function:
            # Delayed action
            if self.is_delay():
                self.create_delayed_executor(function, args, kwargs)

            # Run the action directly
            else:
                logger.debug("Executor.execute() Args: {} KWArgs: {}.".format(str(args), str(kwargs)))
                return function(*args, **kwargs)

    @staticmethod
    def terminate_running_actions():
        logger.debug("Executor.terminate_running_actions() for {} threads".format(len(Executor._threads)))
        for thread in Executor._threads:
            thread.terminate()
        Executor._threads = []

    def get_action_function(self):
        if 'action' not in self._data:
            logger.warning("Executor.get_action_function() No 'action' specified.")
            return None

        action = self._data['action']

        # Kill all running/scheduled tasks
        if action == 'kill':
            return Executor.terminate_running_actions, [], {}

        # -----------------------
        # --- Set Light/Group ---
        # -----------------------

        # On/Off/Toggle
        elif action == 'power' and 'value' in self._data:
            value = self._data['value']
            if value == 1:
                return TradfriGateway.turn_on, [self._lights_and_groups], {}
            elif value == 0:
                return TradfriGateway.turn_off, [self._lights_and_groups], {}
            elif value == 'toggle':
                return TradfriGateway.toggle, [self._lights_and_groups], {}

        # Dim
        elif action == 'dim' and 'value' in self._data:
            value = self._data['value']
            # Use transition time
            if 'transition_time' in self._data:
                transition_time = int(self._data['transition_time'])
                logger.debug("Executor.get_action_function() Dim to {} with transition time {}.".
                             format(value, transition_time))
                return TradfriGateway.dim, [self._lights_and_groups, value], {"transition_time": transition_time}
            else:
                return TradfriGateway.dim, [self._lights_and_groups, value], {}

        # Set Mood
        elif action == 'mood' and 'mood' in self._data:
            mood_name = self._data['mood']
            logger.debug('Executor.get_action_function() Turn on mood: ' + mood_name)
            return Groups.set_mood, [self._lights_and_groups], {"mood_name": mood_name}


        # -----------------------
        # --- Get information ---
        # -----------------------
        elif action == 'get_day_info':
            return InfoWrapper.get_day_info, [], {}

        logger.warning("Executor.get_action_function() Action {} not found/implemented.".format(action))
        return None

    def is_delay(self):
        return 'delay' in self._data

    def create_effect_executor(self):
        effect_name = self._data['effect']
        logger.debug('Executor.get_action_function() Create effect ' + effect_name)
        effect = Effects.from_name(effect_name)
        effect_executor = EffectExecutor(effect)
        effect_executor.start()
        Executor._threads.append(effect_executor)

    def create_delayed_executor(self, action, args, kwargs):
        delay = self._data['delay']

        delay_magnitude = None
        if 'delay_magnitude' in self._data:
            delay_magnitude = self._data['delay_magnitude']

        delayed_executor = DelayedExecutor(action, args, kwargs, delay, delay_magnitude)
        delayed_executor.start()
        Executor._threads.append(delayed_executor)

    def needs_update(self):
        """Some lights and groups need to have up-to-date information to work with the action"""
        if 'action' in self._data and 'value' in self._data:
            if self._data['action'] == 'power' and self._data['value'] == 'toggle':
                return True
        return False

    def is_light_or_group_action(self):
        if 'action' in self._data:
            action = self._data['action']
            return action == 'power' or action == 'dim' or action == 'effect' or action == 'mood'


class ThreadExecutor(threading.Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None):
        super().__init__(group, target, name, args, kwargs)
        self._terminate = False

    def terminate(self):
        self._terminate = True


class DelayedExecutor(ThreadExecutor):
    def __init__(self, action, args, kwargs, delay, delay_magnitude):
        super().__init__(args=[], kwargs={})
        self.args = args
        self.kwargs = kwargs
        self._action = action
        self._delay = DelayedExecutor.calculate_real_delay(delay, delay_magnitude)

    @staticmethod
    def calculate_real_delay(delay, delay_magnitude):
        logger.debug("DelayedExecutor.calculate_real_delay() Delay: " + str(delay) + ", Magnitude: " + str(delay_magnitude))
        delay_multiplier = 1
        if delay_magnitude == 'seconds' or delay_magnitude == 'second':
            delay_multiplier = 1
        elif delay_magnitude == 'minutes' or delay_magnitude == 'minute' or not delay_magnitude:
            delay_multiplier = 60
        elif delay_magnitude == 'hours' or delay_magnitude == 'hour':
            delay_multiplier = 60 * 60

        return delay * delay_multiplier

    def run(self):
        logger.debug("DelayedExecutor.run() Delaying execution with " + str(self._delay) + " seconds.")
        time.sleep(self._delay)

        if not self._terminate:
            self._action(*self.args, **self.kwargs)


class EffectExecutor(ThreadExecutor):
    def __init__(self, effect):
        super().__init__()
        self.effect = effect

    def terminate(self):
        self.effect.abort()

    def run(self):
        self.effect.run()

