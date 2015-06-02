import logging
import tempfile

logger = logging.getLogger(__file__)


class TranscriptionFactor:
    pass


class Gene:
    pass


def _parse_regulondb_genes_file(genes_file):
    genes = {}
    name2loci = {}

    with open(genes_file, "rU") as genes_data:
        for line in genes_data:
            if line.startswith("#"):
                continue

            row = line.split("\t")
            gene = Gene()
            gene.name = row[1]
            gene.locus = row[2]
            gene.start = int(row[3])
            gene.end = int(row[4])

            if len(gene.locus) > 0:
                if gene.name.upper() in name2loci:
                    raise RuntimeError("Name already found: %s" % gene.name)
                else:
                    name2loci[gene.name.upper()] = gene.locus
                    genes[gene.locus] = gene

    return genes, name2loci


def _parse_transcription_factors_file(transcription_factors_file):
    transcription_factors = {}

    with open(transcription_factors_file, "rU") as tf_data:
        for line in tf_data:
            if line.startswith("#"):
                continue
            row = line.split("\t")
            tf = transcription_factors[row[1].upper()] = TranscriptionFactor()
            tf.id = row[0]
            tf.genes = row[2].split(", ")

    return transcription_factors


def _parse_interactions_file(interactions_file, genes, name2loci, transcription_factors):
    interactions = []
    with open(interactions_file, "rU") as inter_file:
        for line in inter_file:
            if line.startswith("#"):
                continue
            try:
                row = line.split("\t")
                tf_name = row[0]
                regulation_type = row[2]
                target_name = row[1]
                target_locus = name2loci[target_name.upper()]
                target_gene = genes[target_locus]
                tf = transcription_factors[tf_name.upper()]
                for tf_gene_name in tf.genes:
                    try:
                        tf_locus = name2loci[tf_gene_name.upper()]
                        tf_gene = genes[tf_locus]
                        logger.info("TF_GENE: %s" % target_gene)
                        interactions.append((tf_gene, target_gene, regulation_type))
                        logger.info("DONE")
                    except KeyError as e:
                        logger.error(e)
            except KeyError as e:
                logger.error(e)

        return interactions


def parse_regulondb(genes_file, transcription_factors_file, interactions_file):
    genes, name2loci = _parse_regulondb_genes_file(genes_file)
    transcription_factors = _parse_transcription_factors_file(transcription_factors_file)
    interactions = _parse_interactions_file(interactions_file, genes, name2loci, transcription_factors)
    return interactions


def convert_interactions_to_links(interactions, posistions):
    temp = tempfile.NamedTemporaryFile("w+")
    for interaction in interactions:
        tf = interaction[0]
        gene = interaction[1]

        if tf.locus not in posistions or gene.locus not in posistions:
            continue

        (tf_start, tf_stop, tf_chromosome) = posistions[tf.locus]
        (g_start, g_stop, g_chromosome) = posistions[gene.locus]
        reg = interaction[2]
        if reg == "+": color = "green"
        elif reg == "-": color = "red"
        elif reg == "+-": color = "blue"
        else: color = "grey"

        temp.write("%s %i %i %s %i %i color=%s\n" % (tf_chromosome, tf_start, tf_stop,
                                                     g_chromosome, g_start, g_stop,
                                                     color))

    temp.flush()
    return temp