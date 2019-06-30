"""GazeNet architecture."""
import time
from typing import Dict

import tensorflow as tf

import util.gaze
from core import BaseDataSource, BaseModel
data_format = "channels_last"  # Change this to "channels_first" to run on GPU


class DenseNetFixed(BaseModel):
    """An implementation of the DenseNet architecture."""

    # The model files will be saved in a folder with this name
    model_identifier = "DenseNetFixed_{}".format(int(time.time()))

    def get_identifier(self):
        # e.g. DenseNetFixed_RS1
        return self.model_identifier

    def build_model(self, data_sources: Dict[str, BaseDataSource], mode: str):
        """Build model."""
        # depth of network. This parameter will define how many layers will be in a dense block
        depth = 40
        # Number of layers per dense block
        self.N = int((depth - 4) / 3)
        # Number of feature maps added by a single convolutional layer
        self.growth_rate = 12

        # Test predictions only work if this is always true.
        # It is ok to set this to True. See https://piazza.com/class/jdbpmonr7fa26b?cid=105
        is_training = True

        data_source = next(iter(data_sources.values()))
        input_tensors = data_source.output_tensors

        # We only use the picture data as input
        x = input_tensors['eye']
        y = input_tensors['gaze']

        def conv(name, l, channel, stride):
            return tf.layers.conv2d(l, filters=channel, kernel_size=3, strides=stride,
                                    padding='same', name=name, data_format=data_format)

        def add_layer(name, l):
            """
            Adds BN, ReLU and Conv layer
            :param name: will be used as variable scope
            :param l: input tensor
            :return:
            """
            with tf.variable_scope(name):
                c = tf.layers.batch_normalization(l, name='bn1', training=is_training)
                c = tf.nn.relu(c)
                c = conv('conv1', c, self.growth_rate, 1)
                l = tf.concat([c, l], 3)
            return l

        def add_transition(name, l):
            """
            Adds a transition layer. Consists of BN, ReLU, Conv, ReLU, AvgPooling
            :param name: variable scope
            :param l: input tensor
            :return:
            """
            shape = l.get_shape().as_list()
            in_channel = shape[3]
            with tf.variable_scope(name):
                l = tf.layers.batch_normalization(l, name='bn1', training=is_training)
                l = tf.nn.relu(l)
                l = tf.layers.conv2d(l, filters=in_channel, strides=1, kernel_size=1, padding='same',
                                     data_format=data_format, name='conv1')
                l = tf.nn.relu(l)
                layer = tf.layers.AveragePooling2D(name='pool', padding='same', strides=2,
                                                   pool_size=2, data_format=data_format)
                l = layer.apply(l, scope=tf.get_variable_scope())
            return l

        def global_average_pooling(x, data_format='channels_last', name=None):
            """
            Global average pooling as in the paper `Network In Network
            <http://arxiv.org/abs/1312.4400>`_.
            Args:
                x (tf.Tensor): a 4D tensor.
            Returns:
                tf.Tensor: a NC tensor named ``output``.
            """
            assert x.shape.ndims == 4
            axis = [1, 2] if data_format == 'channels_last' else [2, 3]
            return tf.reduce_mean(x, axis, name=name)

        def dense_net():
            """
            Returns the GAZENet with three dense blocks
            :return:
            """
            # Initial convolution
            with tf.variable_scope('block_initial'):
                l = conv('conv0', x, 16, 1)

            # Three dense blocks
            with tf.variable_scope('block1'):
                for i in range(self.N):
                    l = add_layer('dense_layer.{}'.format(i), l)
                l = add_transition('transition1', l)

            with tf.variable_scope('block2'):

                for i in range(self.N):
                    l = add_layer('dense_layer.{}'.format(i), l)
                l = add_transition('transition2', l)

            with tf.variable_scope('block3'):

                for i in range(self.N):
                    l = add_layer('dense_layer.{}'.format(i), l)

            # Difference to original DenseNet: we output a numerical value
            with tf.variable_scope('regression'):
                l = tf.layers.batch_normalization(l, name='bnlast', training=is_training)
                l = tf.nn.relu(l)
                l = global_average_pooling(name='gap', x=l, data_format=data_format)
                regressed_output = tf.layers.dense(l, units=2, name='fc4', activation=None)

            return regressed_output

        output = dense_net()

        with tf.variable_scope('mse'):  # To optimize
            loss_terms = {
                'gaze_mse': tf.reduce_mean(tf.squared_difference(output, y)),
            }
        with tf.variable_scope('ang'):  # To evaluate in addition to loss terms
            metrics = {
                'gaze_angular': util.gaze.tensorflow_angular_error_from_pitchyaw(output, y),
            }
        return {'gaze': output}, loss_terms, metrics

