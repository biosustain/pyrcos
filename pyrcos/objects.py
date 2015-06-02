import re
import tempfile
import jinja2
import os

from pyrcos.cmd import circos
from IPython.core.display import display, Image, SVG
from pandas import DataFrame

_dir = os.path.dirname(__file__)

template_loader = jinja2.FileSystemLoader(searchpath=os.path.join(_dir, "templates"))
template_env = jinja2.Environment(loader=template_loader)

DEFAULT_INCLUDE = ["etc/housekeeping.conf", "etc/colors_fonts_patterns.conf"]


class CircosObject(object):
    __template__ = None

    def __str__(self):
        return self.configuration

    @property
    def configuration(self):
        template = template_env.get_template(self.__template__)
        vars = dict(self.__dict__)
        if "attributes" in vars:
            vars["attributes"] = {k: v for k, v in vars["attributes"].iteritems() if v is not None}
        return template.render(vars)


class CircosObjectWithinRadius(CircosObject):
    def __init__(self, r0, r1):
        self.r0 = r0
        self.r1 = r1


class CircosObjectWithFile(CircosObject):
    def __init__(self, file):
        if isinstance(file, str):
            file = open(file)
        elif isinstance(file, DataFrame):
            temp = tempfile.NamedTemporaryFile()
            file.to_csv(temp, sep="\t", index=False, header=False)
            temp.flush()
            file = temp

        self.file = file


class KaryotypeChromosome(object):
    _regex_ = re.compile("chr\s\-\s(.+)\s(.+)\s(.+)\s(.+)\s(.+)$")

    def __init__(self, id, label, start, stop, color):
        self.id = id
        self.label = label
        self.start = start
        self.stop = stop
        self.color = color

    def __str__(self):
        return "chr - %s %s %i %i %s" % (self.id, self.label, self.start, self.stop, self.color)

    @staticmethod
    def parse(line):
        group = KaryotypeChromosome._regex_.findall(line)[0]
        return KaryotypeChromosome(group[0], group[1], int(group[2]), int(group[3]), group[4])


class KaryotypeBand(object):
    _regex_ = re.compile("band\s(.+)\s(.+)\s(.+)\s(.+)\s(.+)\s(.+)$")

    def __init__(self, chromosome_id, id, label, start, stop, color):
        self.chromosome_id = chromosome_id
        self.id = id
        self.label = label
        self.start = start
        self.stop = stop
        self.color = color

    def __str__(self):
        return "band %s %s %s %i %i %s" % (self.chromosome_id, self.id, self.label, self.start, self.stop, self.color)

    @staticmethod
    def parse(line):
        group = KaryotypeBand._regex_.findall(line)[0]
        return KaryotypeBand(group[0], group[1], group[2], int(group[3]), int(group[4]), group[5])


class Karyotype(object):
    def __init__(self, rows):
        self.rows = rows

    def __str__(self):
        return "\n".join([str(r) for r in self.rows])

    @property
    def file(self):
        file = tempfile.NamedTemporaryFile("w+")
        file.write(str(self))
        file.flush()
        return file

    @property
    def filename(self):
        self._f = self.file
        return self._f.name

    def from_file(self, path):
        rows = []
        with open(path, 'r') as fr:
            for line in fr:
                if line.startswith("chr"):
                    rows.append(KaryotypeChromosome.parse(line))
                else:
                    rows.append(KaryotypeBand.parse(line))


class Circos(CircosObject):
    __template__ = "circos.conf.template"

    def __init__(self, karyotypes, ideogram=None, plots=None, ticks=None, links=None, highlights=None, include=None,
                 circos_path=None, width=750, include_defaults=True, **kwargs):
        if isinstance(karyotypes, Karyotype):
            karyotypes = [karyotypes]

        if include is None:
            include = []
        elif isinstance(include, str):
            include = [include]

        if include_defaults:
            include = DEFAULT_INCLUDE + include

        assert all([isinstance(k, Karyotype) for k in karyotypes])
        self.karyotypes = karyotypes
        self.radius = width/2
        self.ideogram = ideogram if ideogram is not None else Ideogram()
        self.plots = Plots(plots)
        self.include = include
        self.ticks = Ticks(ticks)
        self.links = Links(links)
        self.highlights = Highlights(highlights)
        self.circos_path = circos_path
        self.attributes = kwargs

    @property
    def _repr_html_(self):
        self.temp = self.temp if self.temp is not None else tempfile.NamedTemporaryFile()
        self.save(self.temp.name)
        display(SVG(filename=self.temp.name + ".svg"))

        return ""

    def save(self, file_path, format="svg"):
        circos(self, output_file=file_path, format=format, circos_path=self.circos_path)


class Ideogram(CircosObject):
    __template__ = "ideogram.config.template"

    def __init__(self, default_spacing=0, break_spacing=0, thickness=1, stroke_thickness=2, stroke_color="black",
                 fill=True, fill_color="black", radius=0.85, show_label=False, label_font="default", label_radius=0.05,
                 label_size=60, label_parallel=True, label_case="upper", band_stroke_thickness=1, show_bands=True,
                 fill_bands=True):
        self.default_spacing = default_spacing
        self.break_spacing = break_spacing
        self.thickness = thickness
        self.stroke_thickness = stroke_thickness
        self.stroke_color = stroke_color
        self.fill = fill
        self.fill_color = fill_color
        self.radius = radius
        self.show_label = show_label
        self.label_font = label_font
        self.label_radius = label_radius
        self.label_size = label_size
        self.label_parallel = label_parallel
        self.label_case = label_case
        self.band_stroke_thickness = band_stroke_thickness
        self.show_bands = show_bands
        self.fill_bands = fill_bands


class Links(object):

    def __init__(self, links=[]):
        if links is None:
            links = []
        elif isinstance(links, Links):
            links = links.links
        elif isinstance(links, Link):
            links = [links]
        self.links = links

    def __len__(self):
        return len(self.links)

    def __getitem__(self, item):
        return self.links[item]


class Link(CircosObjectWithFile):
    __template__ = "link.config.template"

    def __init__(self, file=None, color=None, radius=None, bezier_radius=0.1, bezier_radius_purity=0.75,
                 crest=0.5, ribbon=False, thickness=1):
        CircosObjectWithFile.__init__(self, file)
        self.color = color
        self.radius = radius
        self.bezier_radius = bezier_radius
        self.bezier_radius_purity = bezier_radius_purity
        self.crest = crest
        self.ribbon = ribbon
        self.thickness = thickness


class Rules(object):
    def __init__(self, rules=None):
        if isinstance(rules, Rules):
            rules = rules.rules
        self.rules = [] if rules is None else rules

    def __len__(self):
        return len(self.rules)


class Rule(CircosObject):
    __template__ = "rule.config.template"

    def __init__(self, condition=None, color=None, show=True, flow=None, radius1=None, radius2=None):
        super(Rule, self).__init__()
        self.condition = condition
        self.color = color
        self.show = show
        self.flow = flow
        self.radius1 = radius1
        self.radius2 = radius2


class Plots(object):
    def __init__(self, plots=[]):
        if plots is None:
            plots = []
        elif isinstance(plots, Plots):
            plots = plots.plots
        elif isinstance(plots, Plot):
            plots = [plots]
        self.plots = plots

    def __len__(self):
        return len(self.plots)

    def __getitem__(self, item):
        return self.plots[item]


class Backgrounds(object):

    def __init__(self, backgrounds=[]):
        if backgrounds is None:
            backgrounds = []
        elif isinstance(backgrounds, Backgrounds):
            backgrounds = backgrounds.backgrounds
        elif isinstance(backgrounds, Background):
            backgrounds = [backgrounds]
        self.backgrounds = backgrounds

    def __len__(self):
        return len(self.backgrounds)

    def __getitem__(self, item):
        return self.backgrounds[item]


class Background(CircosObject):
    __template__ = "background.config.template"

    def __init__(self, y0=0, y1=1, color=None):
        self.y0 = y0
        self.y1 = y1
        self.color = color


class Axes(CircosObject):
    __template__ = "axes.config.template"

    def __init__(self, axes=[]):
        super(Axes, self).__init__()
        if axes is None:
            axes = []
        elif isinstance(axes, Axes):
            axes = axes.axes
        elif isinstance(axes, Axis):
            axes = [axes]
        self.axes = axes

    def __len__(self):
        return len(self.axes)

    def __getitem__(self, item):
        return self.axes[item]


class Axis(CircosObject):
    """
    Arguments
    =========
    spacing :
        absolute or relative spacing of the axis
    position :
        fixed position (or positions) for axes
    position_skip :
        fixed position (or positions) to skip when drawing axis lines
    y0 :
        absolute or relative start of axis lines
    y1 :
        absolute or relative start of axis lines
    color :
        color of axis lines
    thickness :
        thickness of axis lines
    """
    __template__ = "axis.config.template"

    def __init__(self, y0, y1, spacing=None, position=None, position_skip=None, color=None, thickness=None):
        self.y0 = y0
        self.y1 = y1
        self.spacing = spacing
        self.position = position
        self.position_skip = position_skip
        self.color = color
        self.thickness = thickness


class Plot(CircosObjectWithFile, CircosObjectWithinRadius):
    __template__ = "plot.config.template"

    def __init__(self, type, file, r0, r1, backgrounds=None, axes=None, rules=None, **kwargs):
        CircosObjectWithFile.__init__(self, file)
        CircosObjectWithinRadius.__init__(self, r0, r1)
        self.type = type
        self.rules = Rules(rules)
        self.backgrounds = Backgrounds(backgrounds)
        self.axes = Axes(axes)
        self.attributes = kwargs

    @property
    def color(self):
        return self.attributes.get("color", "black")

    @color.setter
    def color(self, color):
        self.attributes["color"] = color


class Heatmap(Plot):
    def __init__(self, file, r0, r1, backgrounds=None, axes=None, rules=None, orientation=None,
                 color=None, color_alt=None, stroke_thickness=None, color_mapping=None, scale_log_base=None):
        super(Heatmap, self).__init__("heatmap", file, r0, r1,
                                      backgrounds=backgrounds,
                                      axes=axes,
                                      rules=rules,
                                      color=color,
                                      color_alt=color_alt,
                                      color_mapping=color_mapping,
                                      scale_log_base=scale_log_base,
                                      orientation=orientation,
                                      stroke_thickness=stroke_thickness)

    @property
    def orientation(self):
        return self.attributes.get("orientation", "out")

    @orientation.setter
    def orientation(self, orientation):
        self.attributes["orientation"] = orientation

    @property
    def color_alt(self):
        return self.attributes.get("color_alt", None)

    @color_alt.setter
    def color_alt(self, color_alt):
        self.attributes['color_atl'] = color_alt

    @property
    def color_mapping(self):
        return self.attributes.get("color_mapping", 0)

    @color_mapping.setter
    def color_mapping(self, color_mapping):
        self.attributes["color_mapping"] = color_mapping

    @property
    def scale_log_base(self):
        return self.attributes.get("scale_log_base", 1)

    @scale_log_base.setter
    def scale_log_base(self, scale_log_base):
        self.attributes["scale_log_base"] = scale_log_base

    @property
    def stroke_thickness(self):
        return self.attributes.get("stroke_thickness", 1)

    @stroke_thickness.setter
    def stroke_thickness(self, stroke_thickness):
        self.attributes["stroke_thickness"] = stroke_thickness


class Histogram(Plot):
    def __init__(self, file, r0, r1, backgrounds=None, axes=None, rules=None, orientation="on", color=None,
                 stroke_thickness=None):
        super(Histogram, self).__init__("histogram", file, r0, r1,
                                        backgrounds=backgrounds,
                                        axes=axes,
                                        rules=rules,
                                        color=color,
                                        orientation=orientation,
                                        stroke_thickness=stroke_thickness)

    @property
    def orientation(self):
        return self.attributes.get("orientation", "out")

    @orientation.setter
    def orientation(self, orientation):
        self.attributes["orientation"] = orientation

    @property
    def stroke_thickness(self):
        return self.attributes.get("stroke_thickness", 1)

    @stroke_thickness.setter
    def stroke_thickness(self, stroke_thickness):
        self.attributes["stroke_thickness"] = stroke_thickness


class Line(Plot):
    def __init__(self, file, r0, r1, backgrounds=None, axes=None, rules=None,
                 color=None, thickness=None, orientation=None):
        super(Line, self).__init__("line", file, r0, r1,
                                   backgrounds=backgrounds,
                                   axes=axes,
                                   rules=rules,
                                   color=color,
                                   thickness=thickness,
                                   orientation=orientation)

    @property
    def orientation(self):
        return self.attributes.get("orientation", "out")

    @orientation.setter
    def orientation(self, orientation):
        self.attributes["orientation"] = orientation

    @property
    def thickness(self):
        return self.attributes.get("thickness", 1)

    @thickness.setter
    def thickness(self, thickness):
        self.attributes["thickness"] = thickness


class Scatter(Plot):
    def __init__(self, file, r0, r1, backgrounds=None, axes=None, rules=None, color=None,
                 glyph=None, glyph_size=None, stroke_color=None, stroke_thickness=None, orientation=None):
        super(Scatter, self).__init__("scatter", file, r0, r1,
                                      backgrounds=backgrounds,
                                      axes=axes,
                                      rules=rules,
                                      color=color,
                                      glyph=glyph,
                                      glyph_size=glyph_size,
                                      stroke_color=stroke_color,
                                      stroke_thickness=stroke_thickness,
                                      orientation=orientation)

    @property
    def glyph(self):
        return self.attributes.get("glyph", "circle")

    @glyph.setter
    def glyph(self, glyph):
        self.attributes["glyph"] = glyph

    @property
    def glyph_size(self):
        return self.attributes.get("glyph_size", 10)

    @glyph_size.setter
    def glyph_size(self, glyph_size):
        self.attributes["glyph_size"] = glyph_size

    @property
    def stroke_color(self):
        return self.attributes.get("stroke_color", "black")

    @stroke_color.setter
    def stroke_color(self, stroke_color):
        self.attributes["stroke_color"] = stroke_color

    @property
    def stroke_thickness(self):
        return self.attributes.get("stroke_thickness", 0)

    @stroke_thickness.setter
    def stroke_thickness(self, stroke_thickness):
        self.attributes["stroke_thickness"] = stroke_thickness

    @property
    def orientation(self):
        return self.attributes.get("orientation", "out")

    @orientation.setter
    def orientation(self, orientation):
        self.attributes["orientation"] = orientation


class Text(Plot):
    def __init__(self, file,  r0, r1, **kwargs):
        super(Text, self).__init__("text", file, r0, r1, **kwargs)


class Tile(Plot):
    def __init__(self, file, r0, r1, backgrounds=None, axes=None, rules=None, layers=None, color=None,
                 stroke_color=None, stroke_thickness=None, margin=None, orientation=None, layers_overflow=None,
                 padding=None, thickness=None):
        super(Tile, self).__init__("tile", file, r0, r1,
                                   backgrounds=backgrounds,
                                   axes=axes,
                                   rules=rules,
                                   color=color,
                                   stroke_color=stroke_color,
                                   stroke_thickness=stroke_thickness,
                                   orientation=orientation,
                                   layers=layers,
                                   layers_overflow=layers_overflow,
                                   margin=margin,
                                   padding=padding,
                                   thickness=thickness
                                   )
    @property
    def color(self):
        return self.attributes.get("color", "grey")

    @color.setter
    def color(self, color):
        self.attributes["color"] = color

    @property
    def stroke_color(self):
        return self.attributes.get("stroke_color", "vgrey")

    @stroke_color.setter
    def stroke_color(self, stroke_color):
        self.attributes["stroke_color"] = stroke_color

    @property
    def stroke_thickness(self):
        return self.attributes.get("stroke_thickness", 1)

    @stroke_thickness.setter
    def stroke_thickness(self, stroke_thickness):
        self.attributes["stroke_thickness"] = stroke_thickness

    @property
    def orientation(self):
        return self.attributes.get("orientation", "out")

    @orientation.setter
    def orientation(self, orientation):
        self.attributes["orientation"] = orientation

    @property
    def layers(self):
        return self.attributes.get("layers", 10)

    @layers.setter
    def layers(self, layers):
        self.attributes["layers"] = layers

    @property
    def layers_overflow(self):
        return self.attributes.get("layers_overflow", "hide")

    @layers_overflow.setter
    def layers_overflow(self, layers_overflow):
        self.attributes["layers_overflow"] = layers_overflow

    @property
    def margin(self):
        return self.attributes.get("margin", "1u")

    @margin.setter
    def margin(self, margin):
        self.attributes["margin"] = margin

    @property
    def padding(self):
        return self.attributes.get("padding", 3)

    @padding.setter
    def padding(self, padding):
        self.attributes["padding"] = padding

    @property
    def thickness(self):
        return self.attributes.get("thickness", 10)

    @thickness.setter
    def thickness(self, thickness):
        self.attributes["thickness"] = thickness


class Ticks(CircosObject):
    __template__ = "ticks.config.template"

    def __init__(self, ticks, show_label=True):
        super(Ticks, self).__init__()
        if ticks is None:
            ticks = []
        elif isinstance(ticks, Ticks):
            ticks = ticks.ticks
        elif isinstance(ticks, Tick):
            ticks = [ticks]
        self.ticks = ticks
        self.show_label = show_label

    def __len__(self):
        return len(self.ticks)

    def __getitem__(self, item):
        return self.ticks[item]


class Tick(CircosObject):
    __template__ = "tick.config.template"

    def __init__(self, size=None, spacing=None, color=None, show_label=True, label_size=None,
                 format=None, grid=False, grid_color=None, grid_thickness=None, radii=None, radius=None):
        super(Tick, self).__init__()

        self.size = size
        self.spacing = spacing
        self.color = color
        self.show_label = show_label
        self.label_size = label_size
        self.format = format
        self.grid = grid
        self.grid_color = grid_color
        self.grid_thickness = grid_thickness
        self.radii = radii if radii is not None else []
        if radii is None and radius is not None:
            self.radii.append(radius)


class Highlights(object):
    def __init__(self, highlights=None):
        if highlights is None:
            highlights = []
        elif isinstance(highlights, Highlights):
            highlights = highlights.highlights
        elif isinstance(highlights, Highlights):
            highlights = [highlights]
        self.highlights = highlights

    def __len__(self):
        return len(self.highlights)

    def __getitem__(self, item):
        return self.highlights[item]


class Highlight(CircosObjectWithFile, CircosObjectWithinRadius):
    __template__ = "highlight.config.template"

    def __init__(self, file, r0, r1, color=None, init_counter=None, **kwargs):
        CircosObjectWithFile.__init__(self, file)
        CircosObjectWithinRadius.__init__(self, r0, r1)
        self.attributes = kwargs
        self.attributes['fill_color'] = color
        self.attributes['init_counter'] = init_counter