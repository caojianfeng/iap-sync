#! /usr/bin/env python3

import argparse
from ..model.product import AppStoreProduct, XML_NAMESPACE, Product
from .actions import actions
from ..utils.args import extract_params


def main():
    parser = argparse.ArgumentParser(
        description='''
        -m | --mode sync: fetch from api defined by --config-file, generate itmsp package, for uploading to itunesconnect
        -m | --mode verify: verify generated itmsp package by sync mode
        -m | --mode upload: upload generated itmsp package to itunes connect by sync mode
        '''
    )
    parser.add_argument('-c', '--config-file')
    parser.add_argument('-m', '--mode')
    parser.add_argument('--skip-appstore', default=False, type=bool)
    parser.add_argument('--price-only', default=False, type=bool)
    parser.add_argument('--fix-screenshots', default=False, type=bool)
    parser.add_argument('--force-update', default=False, type=bool)
    parser.add_argument('--ceil-price', default=False, type=bool)
    parser.add_argument('--dry-run', default=False, type=bool)
    parser = parser.parse_args()
    params = extract_params(parser)
    actions[parser.mode](params, {'namespaces': {'x': XML_NAMESPACE}})

