"""
algorithms

Created by: Martin Sicho
On: 1/26/20, 5:43 PM
"""
import torch

from drugex.api.corpus import Corpus
from drugex.api.pretrain.generators import BasicGenerator
from drugex.api.pretrain.serialization import GeneratorSerializer
from modelling.core import bases
from modelling.models import ModelParameter, ModelFileFormat


class StateSerializer(GeneratorSerializer):

    def __init__(self, path):
        self.path = path

    def saveGenerator(self, generator):
        state = generator.getState()
        torch.save(state, self.path)

class DrugExNetwork(bases.Algorithm):
    name = "DrugExNetwork"
    GENERATOR = 'generator'


    def initSelf(self, X):
        if not self.callback.getState():
            self._model = BasicGenerator(
                monitor=self.callback
                , corpus=X
                , train_params={
                    "epochs" : self.params['nEpochs']
                    , "monitor_freq" : self.params['monitorFrequency']
                }
            )
        else:
            self._model = BasicGenerator(
                monitor=self.callback
                , initial_state=self.callback
                , corpus=X
                , train_params={
                    "epochs" : self.params['nEpochs']
                    , "monitor_freq" : self.params['monitorFrequency']
                }
            )

    @classmethod
    def getModes(cls):
        return [cls.GENERATOR]

    @classmethod
    def getFileFormats(cls, attach_to=None):
        formats = [ModelFileFormat.objects.get_or_create(
            fileExtension=".torch.pkg",
            description="State of a neural network built with pytorch."
        )[0]]
        if attach_to:
            cls.attachToInstance(attach_to, formats, attach_to.fileFormats)

    @staticmethod
    def getParams():
        names = ['nEpochs', 'monitorFrequency'] # TODO: add batch size
        types = [ModelParameter.INTEGER, ModelParameter.INTEGER]
        assert len(names) == len(types)
        return [
            ModelParameter.objects.get_or_create(name=name, contentType=type_, algorithm=DrugExNetwork.getDjangoModel())[0] for name, type_ in zip(names, types)
        ]

    @property
    def model(self):
        return self._model

    def fit(self, X: Corpus, y=None):
        self.initSelf(X)
        valid_set_size = self.validationInfo.validSetSize
        if valid_set_size:
            self.model.pretrain(validation_size=valid_set_size)
        else:
            self.model.pretrain()

    def predict(self, X: Corpus):
        # TODO: implement generation of compounds
        pass

    def getSerializer(self):
        return lambda filename : self.model.save(StateSerializer(filename))