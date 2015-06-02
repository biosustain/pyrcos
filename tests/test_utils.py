from unittest import TestCase
from Bio import SeqIO
from pyrcos.objects import KaryotypeChromosome, KaryotypeBand
from pyrcos.utils import seq_records_to_karyotype
import os

CUR_DIR = os.path.dirname(__file__)


class UtilsTestCase(TestCase):

    def setUp(self):
        cerevisiae = os.path.join(CUR_DIR, "fixtures", "S.cerevisiae.gbff")
        self.genbanks = list(SeqIO.parse(cerevisiae, "gb"))

    def test_convert_seq_records_to_karyotype(self):
        karyotype = seq_records_to_karyotype(self.genbanks)
        self.assertTrue(all([isinstance(r, KaryotypeChromosome) for r in karyotype.rows[0:len(self.genbanks)]]))
        self.assertTrue(all([isinstance(r, KaryotypeBand) for r in karyotype.rows[len(self.genbanks):]]))
