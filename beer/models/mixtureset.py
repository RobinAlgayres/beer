
from collections import namedtuple
import torch
from .bayesmodel import BayesianParameterSet, BayesianParameter
from .bayesmodel import BayesianModelSet
from ..priors import DirichletPrior
from ..utils import logsumexp


MixtureSetElement = namedtuple('MixtureSetElement', ['weights', 'modelset'])

class MixtureSet(BayesianModelSet):

    @classmethod
    def create(cls, size, modelset, weights=None, prior_strength=1.):
        tensor = modelset.mean_field_groups[0][0].prior.natural_parameters
        dtype, device = tensor.dtype, tensor.device
        n_comp_per_mixture = len(modelset) // size
        if weights is None:
            weights = torch.ones(size, n_comp_per_mixture, dtype=dtype,
                                 device=device)
            weights *= 1. / n_comp_per_mixture
        prior_weights = [DirichletPrior(prior_strength * w) for w in weights]
        posterior_weights = [DirichletPrior(prior_strength * w) for w in weights]
        return cls(prior_weights, posterior_weights, modelset)

    def __init__(self, prior_weights, posterior_weights, modelset):
        '''
        Args:
            prior_weights (:any:`DirichletPrior`): Prior distribution
                over the weights of the mixture.
            posterior_weights (any:`DirichletPrior`): Posterior
                distribution over the weights of the mixture.
            modelset (:any:`BayesianModelSet`): Set of models for all
                mixtures.

        '''
        super().__init__()
        self.weights = BayesianParameterSet([
            BayesianParameter(prior, posterior)
            for prior, posterior in zip(prior_weights, posterior_weights)])
        self.modelset = modelset

    def __getitem__(self, key):
        weights = self.weights[key]
        mdlset = [self.modelset[i] for i in range(key * self.n_comp_per_mixture,
                  (key+1) * self.n_comp_per_mixture)]
        return MixtureSetElement(weights=weights, modelset=mdlset)

    def __len__(self):
        return len(self.weights)

    @property
    def n_comp_per_mixture(self):
        return len(self.modelset) // len(self)

    def _local_kl_divergence(self, log_weights, log_resps):
        retval = torch.sum(log_resps.exp() * (log_resps - log_weights), dim=-1)
        return retval

    ####################################################################
    # BayesianModel interface.
    ####################################################################

    def mean_field_factorization(self):
        return [self.modelset.mean_field_factorization()[0] + [*self.weights]]

    def sufficient_statistics(self, data):
        return self.modelset.sufficient_statistics(data)

    def expected_log_likelihood(self, stats):
        log_weights = self.weights.expected_natural_parameters()
        pc_exp_llhs = self.modelset.expected_log_likelihood(stats)
        pc_exp_llhs = pc_exp_llhs.reshape(-1, len(self), self.n_comp_per_mixture)
        w_pc_exp_llhs = pc_exp_llhs + log_weights[None]

        # Responsibilities.
        log_norm = logsumexp(w_pc_exp_llhs.detach(), dim=-1)
        log_resps = w_pc_exp_llhs.detach() - log_norm[:, :, None]
        resps = log_resps.exp()
        self.cache['resps'] = resps

        # expected llh.
        local_kl_div = self._local_kl_divergence(log_weights, log_resps)
        exp_llh = (pc_exp_llhs * resps).sum(dim=-1)

        return exp_llh - local_kl_div

    def accumulate(self, stats, resps):
        ret_val = {}
        joint_resps = self.cache['resps'] * resps[:,:, None]
        sum_joint_resps = joint_resps.sum(dim=0)
        ret_val = dict(zip(self.weights, sum_joint_resps))
        acc_stats = self.modelset.accumulate(stats,
            joint_resps.reshape(-1, len(self) * self.n_comp_per_mixture))
        ret_val = {**ret_val, **acc_stats}
        return ret_val


__all__ = ['MixtureSet']
