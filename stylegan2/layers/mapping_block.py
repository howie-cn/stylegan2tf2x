import tensorflow as tf

from stylegan2.layers.embedding import LabelEmbedding
from stylegan2.layers.dense import Dense
from stylegan2.layers.bias import Bias
from stylegan2.layers.leaky_relu import LeakyReLU


class Mapping(tf.keras.layers.Layer):
    def __init__(self, w_dim, labels_dim, n_mapping, **kwargs):
        super(Mapping, self).__init__(**kwargs)
        self.w_dim = w_dim
        self.labels_dim = labels_dim
        self.n_mapping = n_mapping
        self.gain = 1.0
        self.lrmul = 0.01

        if self.labels_dim > 0:
            self.labels_embedding = LabelEmbedding(embed_dim=self.w_dim, name='labels_embedding')

        self.normalize = tf.keras.layers.Lambda(lambda x: x * tf.math.rsqrt(tf.reduce_mean(tf.square(x), axis=1, keepdims=True) + 1e-8))

        self.dense_layers = list()
        self.bias_layers = list()
        self.act_layers = list()
        for ii in range(self.n_mapping):
            self.dense_layers.append(Dense(w_dim, gain=self.gain, lrmul=self.lrmul, name='dense_{:d}'.format(ii)))
            self.bias_layers.append(Bias(lrmul=self.lrmul, n_dims=2, name='bias_{:d}'.format(ii)))
            self.act_layers.append(LeakyReLU(name='lrelu_{:d}'.format(ii)))

    def call(self, inputs, training=None, mask=None):
        latents, labels = inputs
        x = latents

        # embed label if any
        if self.labels_dim > 0:
            y = self.labels_embedding(labels)
            x = tf.concat([x, y], axis=1)

        # normalize inputs
        x = self.normalize(x)

        # apply mapping blocks
        for dense, apply_bias, leaky_relu in zip(self.dense_layers, self.bias_layers, self.act_layers):
            x = dense(x)
            x = apply_bias(x)
            x = leaky_relu(x)

        return x

    def get_config(self):
        config = super(Mapping, self).get_config()
        config.update({
            'w_dim': self.w_dim,
            'labels_dim': self.labels_dim,
            'n_mapping': self.n_mapping,
            'gain': self.gain,
            'lrmul': self.lrmul,
        })
        return config