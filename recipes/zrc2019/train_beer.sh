#!/usr/bin/env bash

#######################################################################
## SETUP

python ../../setup.py install

if [ $# -ne 2 ]; then
    echo "usage: $0 <wav_dir_tarbz2> <clean>"
    exit 1
fi

# Directory structure
datadir=data
feadir=features
expdir=exp

# Data
db=zrc2019
dataset=train
wav=$1
transcription=trans.txt
# Features
feaname=mfcc

# AUD training
# The number of epochs probably needs to be tuned to the final data.
epochs=8

# These parameter will be ignore if you do parallel training. More
# precisely, the learning rate will be set to 1 and the batch
# size to the number of utterances in the training data.
lrate=0.1
batch_size=400

#######################################################################

if [ $2 = 'clean' ]; then
	rm -r $datadir $feadir 
	rm $expdir/$db/aud/$transcription
	rm $expdir/$db/datasets/$dataset.pkl

fi

source activate beer

mkdir -p $datadir $expdir $feadir


echo "--> Preparing data for the $db database"
local/$db/prepare_data.sh $datadir/$db $wav $dataset || exit 1


echo "--> Extracting features for the $db database"
steps/extract_features.sh conf/${feaname}.yml $datadir/$db/$dataset \
     $feadir/$db/$dataset || exit 1


# Create a "dataset". This "dataset" is just an object
# associating the features with their utterance id and some
# other meta-data (e.g. global mean, variance, ...).
echo "--> Creating dataset(s) for $db database"
steps/create_dataset.sh $datadir/$db/$dataset \
    $feadir/$db/$dataset/${feaname}.npz \
    $expdir/$db/datasets/${dataset}.pkl


echo "--> Acoustic Unit Discovery on $db database"
steps/aud.sh conf/hmm.yml $expdir/$db/datasets/${dataset}.pkl \
    $epochs $lrate $batch_size $expdir/$db/aud $transcription

# Parallel training. Much faster (and more accurate). This is the
# recommended training way. However, you need to have Sun Grid Engine
# like (i.e. qsub command) to run it. If you have a different
# enviroment please see utils/parallel/sge/* to see how to adapt
# this recipe to you system.
#steps/aud_parallel.sh conf/hmm.yml \
#    data/$db/train/uttids \
#    $expdir/$db/datasets/${dataset}.pkl \
#    $epochs $expdir/$db/aud

