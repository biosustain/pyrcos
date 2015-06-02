from pandas import DataFrame


def parse_essentials(essentials_file, samples, normalization=None, cutoff=100):
    data = DataFrame.from_csv(essentials_file, sep="\t", index_col=False)
    data = data[["Position"] + samples]
    data["sum"] = data[samples].apply(sum, axis=1)
    data = data[data["sum"] < cutoff]
    data = data.groupby("Position").sum()
    for sample in samples:
        sample_data = DataFrame(None, index=data.index)
        if normalization is not None:
            sample_data["insertions"] = data[sample].apply(normalization)
        else:
            sample_data["insertions"] = data[sample]

        sample_data.dropna(inplace=True)
        yield sample_data


def convert_sample_to_table(sample_data, chromosome_name):
    return DataFrame(dict(chr=chromosome_name,
                          start=sample_data.index,
                          end=sample_data.index+1,
                          value=sample_data["insertions"]))