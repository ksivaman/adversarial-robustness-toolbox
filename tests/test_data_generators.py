# MIT License
#
# Copyright (C) IBM Corporation 2018
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
# Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
from __future__ import absolute_import, division, print_function, unicode_literals

import logging
import unittest

import numpy as np
from keras.preprocessing.image import ImageDataGenerator

from art.data_generators import KerasDataGenerator, PyTorchDataGenerator, MXDataGenerator, TFDataGenerator
from art.utils import master_seed

logger = logging.getLogger('testLogger')


class TestKerasDataGenerator(unittest.TestCase):
    def setUp(self):
        import keras

        # Set master seed
        master_seed(42)

        class DummySequence(keras.utils.Sequence):
            def __init__(self):
                self._size = 5
                self._x = np.random.rand(self._size, 28, 28, 1)
                self._y = np.random.randint(0, high=10, size=(self._size, 10))

            def __len__(self):
                return self._size

            def __getitem__(self, idx):
                return self._x[idx], self._y[idx]

        sequence = DummySequence()
        self.data_gen = KerasDataGenerator(sequence, size=5, batch_size=1)

    def tearDown(self):
        import keras.backend as k

        k.clear_session()

    def test_gen_interface(self):
        gen = self._dummy_gen()
        data_gen = KerasDataGenerator(gen, size=None, batch_size=5)

        x, y = data_gen.get_batch()

        # Check return types
        self.assertTrue(isinstance(x, np.ndarray))
        self.assertTrue(isinstance(y, np.ndarray))

        # Check shapes
        self.assertEqual(x.shape, (5, 28, 28, 1))
        self.assertEqual(y.shape, (5, 10))

    def test_gen_keras_specific(self):
        gen = self._dummy_gen()
        data_gen = KerasDataGenerator(gen, size=None, batch_size=5)

        iter_ = iter(data_gen.generator)
        x, y = next(iter_)

        # Check return types
        self.assertTrue(isinstance(x, np.ndarray))
        self.assertTrue(isinstance(y, np.ndarray))

        # Check shapes
        self.assertEqual(x.shape, (5, 28, 28, 1))
        self.assertEqual(y.shape, (5, 10))

    def test_sequence_keras_specific(self):
        iter_ = iter(self.data_gen.generator)
        x, y = next(iter_)

        # Check return types
        self.assertTrue(isinstance(x, np.ndarray))
        self.assertTrue(isinstance(y, np.ndarray))

        # Check shapes
        self.assertEqual(x.shape, (28, 28, 1))
        self.assertEqual(y.shape, (10,))

    def test_sequence_interface(self):
        x, y = self.data_gen.get_batch()

        # Check return types
        self.assertTrue(isinstance(x, np.ndarray))
        self.assertTrue(isinstance(y, np.ndarray))

        # Check shapes
        self.assertEqual(x.shape, (28, 28, 1))
        self.assertEqual(y.shape, (10,))

    def test_imagedatagen_interface(self):
        train_size, batch_size = 20, 5
        x_train, y_train = np.random.rand(train_size, 28, 28, 1), np.random.randint(0, 2, size=(train_size, 10))

        datagen = ImageDataGenerator(width_shift_range=0.075, height_shift_range=0.075, rotation_range=12,
                                     shear_range=0.075, zoom_range=0.05, fill_mode='constant', cval=0)
        datagen.fit(x_train)

        # Create wrapper and get batch
        data_gen = KerasDataGenerator(datagen.flow(x_train, y_train, batch_size=batch_size), size=None,
                                      batch_size=batch_size)
        x, y = data_gen.get_batch()

        # Check return types
        self.assertTrue(isinstance(x, np.ndarray))
        self.assertTrue(isinstance(y, np.ndarray))

        # Check shapes
        self.assertEqual(x.shape, (batch_size, 28, 28, 1))
        self.assertEqual(y.shape, (batch_size, 10))

    def test_imagedatagen_keras_specific(self):
        train_size, batch_size = 20, 5
        x_train, y_train = np.random.rand(train_size, 28, 28, 1), np.random.randint(0, 2, size=(train_size, 10))

        datagen = ImageDataGenerator(width_shift_range=0.075, height_shift_range=0.075, rotation_range=12,
                                     shear_range=0.075, zoom_range=0.05, fill_mode='constant', cval=0)
        datagen.fit(x_train)

        # Create wrapper and get batch
        data_gen = KerasDataGenerator(datagen.flow(x_train, y_train, batch_size=batch_size), size=None,
                                      batch_size=batch_size)
        x, y = next(data_gen.generator)

        # Check return types
        self.assertTrue(isinstance(x, np.ndarray))
        self.assertTrue(isinstance(y, np.ndarray))

        # Check shapes
        self.assertEqual(x.shape, (batch_size, 28, 28, 1))
        self.assertEqual(y.shape, (batch_size, 10))

    @staticmethod
    def _dummy_gen(size=5):
        yield np.random.rand(size, 28, 28, 1), np.random.randint(low=0, high=10, size=(size, 10))


class TestPyTorchGenerator(unittest.TestCase):
    def setUp(self):
        import torch
        from torch.utils.data import DataLoader

        # Set master seed
        master_seed(42)

        class DummyDataset(torch.utils.data.Dataset):
            def __init__(self):
                self._size = 10
                self._x = np.random.rand(self._size, 1, 5, 5)
                self._y = np.random.randint(0, high=10, size=self._size)

            def __len__(self):
                return self._size

            def __getitem__(self, idx):
                return self._x[idx], self._y[idx]

        dataset = DummyDataset()
        data_loader = DataLoader(dataset=dataset, batch_size=5, shuffle=True)
        self.data_gen = PyTorchDataGenerator(data_loader, size=10, batch_size=5)

    def test_gen_interface(self):
        x, y = self.data_gen.get_batch()

        # Check return types
        self.assertTrue(isinstance(x, np.ndarray))
        self.assertTrue(isinstance(y, np.ndarray))

        # Check shapes
        self.assertEqual(x.shape, (5, 1, 5, 5))
        self.assertEqual(y.shape, (5,))

    def test_pytorch_specific(self):
        import torch

        iter_ = iter(self.data_gen.data_loader)
        x, y = next(iter_)

        # Check return types
        self.assertTrue(isinstance(x, torch.Tensor))
        self.assertTrue(isinstance(y, torch.Tensor))

        # Check shapes
        self.assertEqual(x.shape, (5, 1, 5, 5))
        self.assertEqual(y.shape, (5,))


class TestMXGenerator(unittest.TestCase):
    def setUp(self):
        import mxnet as mx

        # Set master seed
        master_seed(42)

        x = mx.random.uniform(shape=(10, 1, 5, 5))
        y = mx.random.uniform(shape=10)
        dataset = mx.gluon.data.dataset.ArrayDataset(x, y)

        data_loader = mx.gluon.data.DataLoader(dataset, batch_size=5, shuffle=True)
        self.data_gen = MXDataGenerator(data_loader, size=10, batch_size=5)

    def test_gen_interface(self):
        x, y = self.data_gen.get_batch()

        # Check return types
        self.assertTrue(isinstance(x, np.ndarray))
        self.assertTrue(isinstance(y, np.ndarray))

        # Check shapes
        self.assertEqual(x.shape, (5, 1, 5, 5))
        self.assertEqual(y.shape, (5,))

    def test_mxnet_specific(self):
        import mxnet as mx

        iter_ = iter(self.data_gen.data_loader)
        x, y = next(iter_)

        # Check return types
        self.assertTrue(isinstance(x, mx.ndarray.NDArray))
        self.assertTrue(isinstance(y, mx.ndarray.NDArray))

        # Check shapes
        self.assertEqual(x.shape, (5, 1, 5, 5))
        self.assertEqual(y.shape, (5,))


class TestTFDataGenerator(unittest.TestCase):
    def setUp(self):
        import tensorflow as tf

        # Set master seed
        master_seed(42)

        def generator(batch_size=5):
            while True:
                yield np.random.rand(batch_size, 5, 5, 1), np.random.randint(0, 10, size=10 * batch_size). \
                    reshape(batch_size, -1)

        self.sess = tf.Session()
        self.dataset = tf.data.Dataset.from_generator(generator, (tf.float32, tf.int32))

    def tearDown(self):
        import tensorflow as tf

        self.sess.close()
        tf.reset_default_graph()

    def test_init(self):
        iter_ = self.dataset.make_initializable_iterator()
        data_gen = TFDataGenerator(sess=self.sess, iterator=iter_, iterator_type='initializable',
                                   iterator_arg={}, size=10, batch_size=5)
        x, y = data_gen.get_batch()

        # Check return types
        self.assertTrue(isinstance(x, np.ndarray))
        self.assertTrue(isinstance(y, np.ndarray))

        # Check shapes
        self.assertEqual(x.shape, (5, 5, 5, 1))
        self.assertEqual(y.shape, (5, 10))

    def test_reinit(self):
        import tensorflow as tf

        iter_ = tf.data.Iterator.from_structure(self.dataset.output_types, self.dataset.output_shapes)
        init_op = iter_.make_initializer(self.dataset)
        data_gen = TFDataGenerator(sess=self.sess, iterator=iter_, iterator_type='reinitializable',
                                   iterator_arg=init_op, size=10, batch_size=5)
        x, y = data_gen.get_batch()

        # Check return types
        self.assertTrue(isinstance(x, np.ndarray))
        self.assertTrue(isinstance(y, np.ndarray))

        # Check shapes
        self.assertEqual(x.shape, (5, 5, 5, 1))
        self.assertEqual(y.shape, (5, 10))

    def test_feedable(self):
        import tensorflow as tf

        handle = tf.placeholder(tf.string, shape=[])
        iter_ = tf.data.Iterator.from_string_handle(handle, self.dataset.output_types, self.dataset.output_shapes)
        feed_iterator = self.dataset.make_initializable_iterator()
        feed_handle = self.sess.run(feed_iterator.string_handle())
        data_gen = TFDataGenerator(sess=self.sess, iterator=iter_, iterator_type='feedable',
                                   iterator_arg=(feed_iterator, {handle: feed_handle}), size=10, batch_size=5)
        x, y = data_gen.get_batch()

        # Check return types
        self.assertTrue(isinstance(x, np.ndarray))
        self.assertTrue(isinstance(y, np.ndarray))

        # Check shapes
        self.assertEqual(x.shape, (5, 5, 5, 1))
        self.assertEqual(y.shape, (5, 10))


if __name__ == '__main__':
    unittest.main()
