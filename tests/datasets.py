from unittest import TestCase
from pyrcos.datasets.regulatory_network import parse_regulondb
import os

CURDIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(CURDIR, "..", "data")

class RegulatoryNetworkTestCase(TestCase):
    def test_parse_regulondb(self):
        genes_file = os.path.join(DATA_DIR, "GeneProductSet.txt")
        transcription_factors_file = os.path.join(DATA_DIR, "TFSet.txt")
        interactions_file = os.path.join(DATA_DIR, "network_tf_gene.txt")
        list = parse_regulondb(genes_file, transcription_factors_file, interactions_file)
        print(list)