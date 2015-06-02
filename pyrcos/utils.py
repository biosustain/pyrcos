from Bio.SeqRecord import SeqRecord
from pandas import DataFrame
from pyrcos.objects import KaryotypeChromosome, Karyotype
from pyrcos.constants import DEFAUT_CHR_COLOR
import numpy as np


def seq_records_to_karyotype(records, color_map={}):
    assert all([isinstance(r, SeqRecord) for r in records])
    chrs = []
    for i, record in enumerate(records):
        chr = KaryotypeChromosome(record.id, record.name, 1, len(record), color_map.get(record.id, DEFAUT_CHR_COLOR))
        chrs.append(chr)

    return Karyotype(chrs)


def seq_record_to_tiles(records, feature_types=["gene"]):
    for record in records:
        track = DataFrame(columns=["chromosome", "start", "end", "value", "options"])
        i = 0
        for feature in record.features:
            if feature.type in feature_types:
                track.loc[i] = (record.id, int(feature.location.start+1),
                                           int(feature.location.end),
                                           1, "")
                i += 1

        track["start"] = np.array(track["start"], dtype=int)
        track["end"] = np.array(track["end"], dtype=int)

        yield track