import tensorflow as tf

from rllab.core.serializable import Serializable

from softqlearning.misc.nn import MLPFunction
from softqlearning.misc import tf_utils


class NNVFunction(MLPFunction):
    def __init__(self,
                 env_spec,
                 hidden_layer_sizes=(100, 100),
                 name='value_function'):
        Serializable.quick_init(self, locals())

        self._Do = env_spec.observation_space.flat_dim
        self._observations_ph = tf.placeholder(
            tf.float32, shape=[None, self._Do], name='observations')

        super(NNVFunction, self).__init__(
            inputs=(self._observations_ph, ),
            name=name,
            hidden_layer_sizes=hidden_layer_sizes)

    def eval(self, observations):
        return super(NNVFunction, self)._eval((observations, ))

    def output_for(self, observations, reuse=False):
        return super(NNVFunction, self)._output_for(
            (observations, ), reuse=reuse)


class NNQFunction(MLPFunction):
    def __init__(self,
                 env_spec,
                 hidden_layer_sizes=(100, 100),
                 name='q_function'):
        Serializable.quick_init(self, locals())

        self._Da = env_spec.action_space.flat_dim
        self._Do = env_spec.observation_space.flat_dim

        self._observations_ph = tf.placeholder(
            tf.float32, shape=[None, self._Do], name='observations')
        self._actions_ph = tf.placeholder(
            tf.float32, shape=[None, self._Da], name='actions')

        super(NNQFunction, self).__init__(
            inputs=(self._observations_ph, self._actions_ph),
            name=name,
            hidden_layer_sizes=hidden_layer_sizes)

    def output_for(self, observations, actions, reuse=False):
        return super(NNQFunction, self)._output_for(
            (observations, actions), reuse=reuse)

    def eval(self, observations, actions):
        return super(NNQFunction, self)._eval((observations, actions))


class MeanQFunction(Serializable):
    def __init__(self, env_spec, q_functions):
        Serializable.quick_init(self, locals())

        self.q_functions = q_functions

        self._Da = env_spec.action_space.flat_dim
        self._Do = env_spec.observation_space.flat_dim

        self._observations_ph = tf.placeholder(
            tf.float32, shape=[None, self._Do], name='observations')
        self._actions_ph = tf.placeholder(
            tf.float32, shape=[None, self._Da], name='actions')

        self._output = self.output_for(
            self._observations_ph, self._actions_ph, reuse=True)

    def output_for(self, observations, actions, reuse=False):
        outputs = []
        for i, q_function in enumerate(self.q_functions):
            outputs.append(
                q_function.output_for(observations, actions, reuse=reuse))

        output = tf.add_n(outputs)
        return output

    def _eval(self, observations, actions):
        feeds = {
            self._observations_ph: observations,
            self._actions_ph: actions
        }

        return tf_utils.get_default_session().run(self._output, feeds)
