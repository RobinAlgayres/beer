
from .parameters import *
from .bayesmodel import *
from .normal import *
from .normalset import *
from .mixture import *
from .mixtureset import *
from .hmm import *
from .ppca import *
from .pldaset import *
from .vae import *
from .. import nnet


_model_types = {
    'Normal': normal.create,
    'NormalSet': normalset.create,
    'Mixture': mixture.create,
    'MixtureSet': mixtureset.create,
    'HMM': None,
    'PPCA': ppca.create,
    'PLDASet': pldaset.PLDASet.create,
    'MarginalPLDASet': pldaset.MarginalPLDASet.create,
    'VAE': vae.create_vae,
    'NonLinearSubspaceModel': vae.create_non_linear_subspace_model,
    'NeuralNetwork': nnet.neuralnetwork.create
}


def create_model(conf, mean, variance, create_model_handle=None):
    '''Create one or several models from a YAML configuration string.

    Args:
        conf (dict): Dictionary containing the configuration of the
            model.
        mean (``torch.Tensor``): Mean of the data to initialize the
            model.
        variance (``torch.Tensor``): Variance of the data to initialize
            the model.

    Returns:
        :any:`BayesianModel` or a list of :any:`BayesianModel`

    '''
    requested_type = conf['type']
    if requested_type not in _model_types:
        raise ValueError('Unknown model type: {}'.format(requested_type))
    if requested_type == 'NeuralNetwork':
        return _model_types[requested_type](conf, mean.dtype, mean.device)
    else:
        return _model_types[requested_type](conf, mean, variance, create_model)
