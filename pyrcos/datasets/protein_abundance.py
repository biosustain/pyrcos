import tempfile
from math import log


def read_paxdb(dataset, normalization=log, normalization_kwargs={}):
    res = {}
    with open(dataset, "r") as data:
        for line in data:
            if line.startswith("#"):
                continue

            (internal_id, string_external_id, abundance) = line.split("\t")
            (string_id, locus) = string_external_id.split(".")
            res[locus] = normalization(float(abundance), **normalization_kwargs)

    return res


def convert_abundance_to_file(abundance, positions):
    file = tempfile.NamedTemporaryFile()
    for locus in abundance.keys():
        (start, end, chromosome) = positions[locus]
        file.write("%s %i %i %f\n" % (chromosome, start, end, abundance[locus]))

    file.flush()
    return file