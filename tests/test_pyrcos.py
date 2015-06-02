from unittest import TestCase
from pyrcos.objects import KaryotypeChromosome, KaryotypeBand, Ideogram

expected_default_ideogram = \
"""<ideogram>

<spacing>
default = 0u
break   = 0u
</spacing>

# thickness (px) of chromosome ideogram
thickness        = 1p
stroke_thickness = 2
# ideogram border color
stroke_color     = black
fill             = yes
# the default chromosome color is set here and any value
# defined in the karyotype file overrides it
fill_color       = black

# fractional radius position of chromosome ideogram within image
radius         = 0.85r
show_label     = no
label_font     = default
label_radius   = 0.05
label_size     = 60
label_parallel = yes
label_case     = upper

# cytogenetic bands
band_stroke_thickness = 1

# show_bands determines whether the outline of cytogenetic bands
# will be seen
show_bands            = True
# in order to fill the bands with the color defined in the karyotype
# file you must set fill_bands
fill_bands            = True

</ideogram>"""


class PyrcosTestCase(TestCase):

    def setUp(self):
        pass

    def test_karyotype_chromossome(self):
        chromosome = KaryotypeChromosome("id", "label", 1, 10, "blue")
        self.assertEqual(str(chromosome), "chr - id label 1 10 blue")

    def test_karyotype_band(self):
        band = KaryotypeBand("id", "band.id", "band.label", 1, 10, "blue")
        self.assertEqual(str(band), "band id band.id band.label 1 10 blue")

    def test_ideogram(self):
        default_ideogram = Ideogram()
        default_attrs = dict(default_spacing=0, break_spacing=0, thickness=1, stroke_thickness=2, stroke_color="black",
                             fill=True, fill_color="black", radius=0.85, show_label=False, label_font="default",
                             label_radius=0.05, label_size=60, label_parallel=True, label_case="upper",
                             band_stroke_thickness=1, show_bands=True, fill_bands=True)

        for attr in default_attrs:
            self.assertEqual(getattr(default_ideogram, attr), default_attrs[attr])

        self.assertEqual(str(default_ideogram), expected_default_ideogram)