import os
import tempfile


def circos(circos_object, output_file=None, circos_path=None, format="png"):
    cmd = os.path.join(circos_path, "bin", "circos")
    config = tempfile.NamedTemporaryFile()
    conf = str(circos_object)
    config.write(conf)
    config.flush()
    split = output_file.split(os.sep)
    output_file = split[-1]
    output_dir = os.sep.join(split[0:-1])
    if len(output_dir) == 0:
        output_dir = "."

    cmd += " -config %s -%s -dir %s -file %s" % (config.name, format, output_dir, output_file)
    if os.system(cmd) != 0:
        raise RuntimeError