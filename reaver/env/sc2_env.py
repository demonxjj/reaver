from pysc2.lib import actions
from pysc2.env.environment import StepType
from .abc_env import Env, Spec, Space


class SC2Env(Env):
    def __init__(self, map_name='MoveToBeacon', spatial_dim=16, step_mul=8, render=False):
        self._env = None
        self.act_wrapper = ActionWrapper()
        self.obs_wrapper = ObservationWrapper()
        self.map_name, self.dim, self.step_mul, self.render = map_name, spatial_dim, step_mul, render

    def start(self):
        # importing here to lazy-load
        from pysc2.env import sc2_env
        self._env = sc2_env.SC2Env(
            map_name=self.map_name,
            visualize=self.render,
            agent_interface_format=sc2_env.parse_agent_interface_format(
                feature_screen=self.dim,
                feature_minimap=self.dim,
                rgb_screen=None,
                rgb_minimap=None
            ),
            step_mul=self.step_mul,
        )

    def step(self, action):
        return self.obs_wrapper(self._env.step(self.act_wrapper(action)))

    def reset(self):
        return self.obs_wrapper(self._env.reset())

    def stop(self):
        self._env.close()

    def obs_spec(self):
        return self.obs_wrapper.wrap_spec(self._env.observation_spec())

    def act_spec(self):
        return self.act_wrapper.wrap_spec(self._env.action_spec())


class ActionWrapper:
    def __call__(self, action):
        return [actions.FunctionCall(action[0], action[1:])]

    def wrap_spec(self, spec):
        return spec[0]


class ObservationWrapper:
    def __call__(self, timestep):
        ts = timestep[0]
        return ts.observation, ts.reward, ts.step_type == StepType.LAST

    def wrap_spec(self, spec):
        return spec[0]
