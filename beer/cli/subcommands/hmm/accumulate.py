
'Accumulate the ELBO from a list of utterances given from "stdin"'

import argparse
import pickle
import sys

import beer


def setup(parser):
    parser.add_argument('model', help='hmm based model')
    parser.add_argument('dataset', help='training data set')
    parser.add_argument('out', help='output accumulated ELBO')


def main(args, logger):
    logger.debug('load the model')
    with open(args.model, 'rb') as f:
        model = pickle.load(f)

    logger.debug('load the dataset')
    with open(args.dataset, 'rb') as f:
        dataset = pickle.load(f)


    elbo = beer.evidence_lower_bound(datasize=dataset.size)
    count = 0
    for line in sys.stdin:
        utt = dataset[line.strip().split()[0]]

        logger.debug(f'processing utterance: {utt.id}')
        elbo += beer.evidence_lower_bound(model, utt.features,
                                          datasize=dataset.size)
        count += 1

    logger.debug('saving the accumulated ELBO...')
    with open(args.out, 'wb') as f:
        pickle.dump((elbo, count), f)

    logger.info(f'accumulated ELBO over {count} utterances: {float(elbo) / (count * dataset.size) :.3f}.')

if __name__ == "__main__":
    main()

