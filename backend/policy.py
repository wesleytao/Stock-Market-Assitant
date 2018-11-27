from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import copy
import json
import logging
import os
import tensorflow as tf
import warnings
from typing import Any, List, Dict, Text, Optional, Tuple

from rasa_core import utils
from rasa_core.domain import Domain
from rasa_core.featurizers import (
    MaxHistoryTrackerFeaturizer, BinarySingleStateFeaturizer)
from rasa_core.featurizers import TrackerFeaturizer
from rasa_core.policies.policy import Policy
from rasa_core.trackers import DialogueStateTracker

import logging

from rasa_core.policies.keras_policy import KerasPolicy

logger = logging.getLogger(__name__)


class CustomPolicy(KerasPolicy):
    def model_architecture(self, input_shape, output_shape):
        """Build a Keras model and return a compiled model."""
        from keras.layers import LSTM, Activation, Masking, Dense
        from keras.models import Sequential

        from keras.models import Sequential
        from keras.layers import \
            Masking, LSTM, Dense, TimeDistributed, Activation

        # Build Model
        model = Sequential()

        # the shape of the y vector of the labels,
        # determines which output from rnn will be used
        # to calculate the loss
        if len(output_shape) == 1:
            # y is (num examples, num features) so
            # only the last output from the rnn is used to
            # calculate the loss
            model.add(Masking(mask_value=-1, input_shape=input_shape))
            model.add(LSTM(self.rnn_size))
            model.add(Dense(input_dim=self.rnn_size, units=output_shape[-1]))
        elif len(output_shape) == 2:
            # y is (num examples, max_dialogue_len, num features) so
            # all the outputs from the rnn are used to
            # calculate the loss, therefore a sequence is returned and
            # time distributed layer is used

            # the first value in input_shape is max dialogue_len,
            # it is set to None, to allow dynamic_rnn creation
            # during prediction
            model.add(Masking(mask_value=-1,
                              input_shape=(None, input_shape[1])))
            model.add(LSTM(self.rnn_size, return_sequences=True))
            model.add(TimeDistributed(Dense(units=output_shape[-1])))
        else:
            raise ValueError("Cannot construct the model because"
                             "length of output_shape = {} "
                             "should be 1 or 2."
                             "".format(len(output_shape)))

        model.add(Activation('softmax'))

        model.compile(loss='categorical_crossentropy',
                      optimizer='adam',
                      metrics=['accuracy'])

        logger.debug(model.summary())
        return model

    def train(self,
              training_trackers: List[DialogueStateTracker],
              domain: Domain,
              **kwargs: Any
              ) -> None:

        training_data = self.featurize_for_training(training_trackers,
                                                    domain,
                                                    **kwargs)

        # noinspection PyPep8Naming
        shuffled_X, shuffled_y = training_data.shuffled_X_y()

        self.graph = tf.Graph()
        with self.graph.as_default():
            self.session = tf.Session()
            with self.session.as_default():
                if self.model is None:
                    self.model = self.model_architecture(shuffled_X.shape[1:],
                                                         shuffled_y.shape[1:])

                logger.info("Fitting model with {} total samples and a "
                            "validation split of {}"
                            "".format(training_data.num_examples(),
                                      self.validation_split))
                # filter out kwargs that cannot be passed to fit
                params = self._get_valid_params(self.model.fit, **kwargs)

                self.model.fit(shuffled_X, shuffled_y, **params)
                # the default parameter for epochs in keras fit is 1
                self.current_epoch = self.defaults.get("epochs", 1)
                logger.info("Done fitting keras policy model")
