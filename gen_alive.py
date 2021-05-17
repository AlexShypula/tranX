# coding=utf-8
from __future__ import print_function

import time

import astor
import six.moves.cPickle as pickle
from six.moves import input
from six.moves import xrange as range
from torch.autograd import Variable
import torch
import numpy as np
import sys

import evaluation
from asdl.asdl import ASDLGrammar
from asdl.transition_system import TransitionSystem
from common.utils import update_args, init_arg_parser
from common.registerable import Registrable
from components.dataset import Dataset
# from components.reranker import *
from components.standalone_parser import StandaloneParser
from components.vocab import Vocab, VocabEntry
from model import nn_utils
from model.paraphrase import ParaphraseIdentificationModel
from model.parser import Parser
from model.reconstruction_model import Reconstructor
from model.utils import GloveHelper
from asdl.lang.alive_lang.alive_form import check_ast_tree_opt
from asdl.lang.alive_lang.alive.common import ParseError
import random

assert astor.__version__ == "0.7.1"
# if six.PY3:
#     # import additional packages for wikisql dataset (works only under Python 3)
#     pass


vocab_src = [str(i) for i in range(10)]
vocab_primitive_code = vocab_src + [char + str(i) for char in ["r", "C"] for i in range(10)]
src_vocab = VocabEntry.from_corpus(vocab_src, size=len(vocab_src)*2)
tgt_primitive = tgt_code = VocabEntry.from_corpus(vocab_primitive_code, size=len(vocab_primitive_code)*2)

vocab = Vocab(source=src_vocab, primitive=tgt_primitive, code=tgt_code)

def init_config():
    args = arg_parser.parse_args()

    # seed the RNG
    torch.manual_seed(args.seed)
    if args.cuda:
        torch.cuda.manual_seed(args.seed)
    np.random.seed(int(args.seed * 13 / 7))

    return args


def gen(args):

    # vocab = pickle.load(open(args.vocab, 'rb'))
    grammar = ASDLGrammar.from_text(open(args.asdl_file).read())
    transition_system = Registrable.by_name(args.transition_system)(grammar)

    parser_cls = Registrable.by_name(args.parser)  # TODO: add arg

    model = parser_cls(args, vocab, transition_system)

    model.eval()
    n_verified = 0
    n_didnt_verify = 0
    n_error = 0
    # for i in range(100):
    i=0
    while(n_verified + n_error + n_didnt_verify) < 1000:
        i+=1
        inp = [" ".join([c for c in str(random.randint(0,100000))])]
        hypotheses = model.parse(inp, debug=True)

        for hyp_id, hyp in enumerate(hypotheses):
            print('------------------ Iter {} Hypothesis {} ------------------'.format(i, hyp_id))
            print(hyp.code)
            try:
                verified = check_ast_tree_opt(hyp.tree)
                n_verified += verified
                n_didnt_verify += (1-verified)
            except (AssertionError, TypeError, ValueError, ParseError, NameError, AttributeError) as e:
                try:
                    print("error!")
                    print("*"*40)
                    print(repr(e))
                    n_error+=1
                except NameError as e:
                    print("error!")
                    print("*" * 40)
                    print(repr(e))
                    n_error += 1
    print("verified", n_verified)
    print("didnt' verify", n_didnt_verify)
    print("error", n_error)


#
#
# def test(args):
#     test_set = Dataset.from_bin_file(args.test_file)
#     assert args.load_model
#
#     print('load model from [%s]' % args.load_model, file=sys.stderr)
#     params = torch.load(args.load_model, map_location=lambda storage, loc: storage)
#     transition_system = params['transition_system']
#     saved_args = params['args']
#     saved_args.cuda = args.cuda
#     # set the correct domain from saved arg
#     args.lang = saved_args.lang
#
#     parser_cls = Registrable.by_name(args.parser)
#     parser = parser_cls.load(model_path=args.load_model, cuda=args.cuda)
#     parser.eval()
#     evaluator = Registrable.by_name(args.evaluator)(transition_system, args=args)
#     eval_results, decode_results = evaluation.evaluate(test_set.examples, parser, evaluator, args,
#                                                        verbose=args.verbose, return_decode_result=True)
#     print(eval_results, file=sys.stderr)
#     if args.save_decode_to:
#         pickle.dump(decode_results, open(args.save_decode_to, 'wb'))

#
# def interactive_mode(args):
#     """Interactive mode"""
#     print('Start interactive mode', file=sys.stderr)
#
#     parser = StandaloneParser(args.parser,
#                               args.load_model,
#                               args.example_preprocessor,
#                               beam_size=args.beam_size,
#                               cuda=args.cuda)
#
#     while True:
#         utterance = input('Query:').strip()
#         hypotheses = parser.parse(utterance, debug=True)
#
#         for hyp_id, hyp in enumerate(hypotheses):
#             print('------------------ Hypothesis %d ------------------' % hyp_id)
#             print(hyp.code)
#             # print(hyp.tree.to_string())
#             # print('Actions:')
#             # for action_t in hyp.action_infos:
#             #     print(action_t.__repr__(True))
#
#


if __name__ == '__main__':
    arg_parser = init_arg_parser()
    args = init_config()
    print(args, file=sys.stderr)
    gen(args)
    # if args.mode == 'train':
    #     train(args)
    # elif args.mode in ('train_reconstructor', 'train_paraphrase_identifier'):
    #     train_rerank_feature(args)
    # elif args.mode == 'rerank':
    #     train_reranker_and_test(args)
    # elif args.mode == 'test':



    #     test(args)
    # elif args.mode == 'interactive':
    #     interactive_mode(args)
    # else:
    #     raise RuntimeError('unknown mode')
