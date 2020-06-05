import tensorflow as tf

from stylegan2.layers.conv import Conv2D
from stylegan2.layers.bias_act import BiasAct


class FromRGB(tf.keras.layers.Layer):
    def __init__(self, fmaps, **kwargs):
        super(FromRGB, self).__init__(**kwargs)
        self.fmaps = fmaps

        self.conv = Conv2D(fmaps=self.fmaps, kernel=1, up=False, down=False,
                           resample_kernel=None, gain=1.0, lrmul=1.0, name='conv')
        self.apply_bias_act = BiasAct(lrmul=1.0, act='lrelu', name='bias')

    def call(self, inputs, training=None, mask=None):
        y = self.conv(inputs)
        y = self.apply_bias_act(y)
        return y
