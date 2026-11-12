"""Regression checks against xmltest2 output; not an in-game simulation.

Run Validate-Cinis.ps1 first, then: python scripts/test_obsidian_balance.py
The arithmetic follows the read-only native investigation in research/STATUS.md.
Only the Python standard library is needed.
"""
import copy
import math
from pathlib import Path
import struct
import unittest
import xml.etree.ElementTree as ET

from build_obsidian_fix import apply_obsidian_ops

ROOT = Path(__file__).resolve().parents[1]
DISTANCES = (0, 384, 3328, 3500, math.hypot(3328, 3328), math.hypot(4096, 4096))


def f32(value):
    return struct.unpack('<f', struct.pack('<f', value))[0]


def native_amount(base, distance, maximum_distance, size_factor, phase_factor=1):
    # Initial and eruption paths skip the distance block entirely for <= 0.
    if maximum_distance > 0:
        scale = max(0, min(1, f32(1 - f32(f32(distance) / f32(maximum_distance)))))
        base = int(f32(f32(base) * scale))
    base = int(f32(f32(base) * f32(phase_factor)))
    return int(f32(f32(base) * f32(size_factor)))


def signature(node):
    return (node.tag, tuple(sorted(node.attrib.items())), (node.text or '').strip(),
            tuple(signature(child) for child in node))


class ObsidianBalance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = ET.parse(ROOT / 'research/patched-assets.xml').getroot()
        assets = {a.findtext('Values/Standard/GUID', '').strip(): a for a in root.iter('Asset')}
        config = assets['144830'].find('Values/VolcanoEruptionBalancing/ConfigPerRegion/Item')
        cls.initial = config.find('InitialLimitedLodeFertilities/Item')
        cls.eruption = assets['144837'].find('Values/VolcanoPhase/SpawnLimitedLodeFertilities/Item')
        cls.fertility = assets['145337'].find('Values/Fertility')
        cls.size_factor = float(config.findtext('LimitedLodeIslandSizeMultiplicator/Continental/Value'))
        cls.fragment = ET.parse(ROOT / 'config/obsidian-modops.xml').getroot()
        cls.packaged = ET.parse(ROOT / 'dist/cinis-four-directions/data/base/config/export/assets.xml').getroot()

    def refill(self, distance, overdrive=0, research=0, factor=1):
        base = int(self.eruption.findtext('LimitedLodeBaseAmount'))
        base += overdrive * int(self.eruption.findtext('AdditionalOverdriveAmountMin'))
        base += research * int(self.eruption.findtext('TechIncreaseAmountMin'))
        return native_amount(base, distance, float(self.eruption.findtext('ScaleAmountMaximumDistance')),
                             self.size_factor, factor)

    def test_distance_scaling_is_disabled_in_both_paths(self):
        self.assertEqual(float(self.initial.findtext('ScaleAmountMaximumDistance')), 0)
        self.assertEqual(float(self.eruption.findtext('ScaleAmountMaximumDistance')), 0)

    def test_all_cinis_start_with_120(self):
        amounts = [native_amount(int(self.initial.findtext('LimitedLodeBaseAmount')), distance,
                                 float(self.initial.findtext('ScaleAmountMaximumDistance')), self.size_factor)
                   for distance in DISTANCES]
        self.assertEqual(amounts, [120] * len(DISTANCES))

    def test_first_and_regular_eruption_have_equal_base_amounts(self):
        first = float(self.eruption.findtext('DefaultFactorLastPhaseStart'))
        self.assertEqual(first, 0.5)
        for distance in DISTANCES:
            with self.subTest(distance=distance):
                self.assertEqual(self.refill(distance, factor=first), 420)
                self.assertEqual(self.refill(distance), 840)

    def test_progression_does_not_reintroduce_distance_bias(self):
        for overdrive in range(5):
            for research in range(4):
                for factor in (0.5, 0.75, 1):
                    amounts = [self.refill(d, overdrive, research, factor) for d in DISTANCES]
                    with self.subTest(overdrive=overdrive, research=research, factor=factor):
                        self.assertEqual(len(set(amounts)), 1)

    def test_random_bonus_ranges_use_fixed_original_midpoints(self):
        for prefix, expected in (('AdditionalOverdriveAmount', 300), ('TechIncreaseAmount', 400)):
            self.assertEqual(int(self.eruption.findtext(prefix + 'Min')), expected)
            self.assertEqual(int(self.eruption.findtext(prefix + 'Max')), expected)
        self.assertEqual(self.refill(3328, overdrive=1), 1200)
        self.assertEqual(self.refill(3328, research=1), 1320)

    def test_original_capacity_and_research_limit_remain(self):
        cap = int(self.fertility.findtext('LimitedLodeMaximum/Continental/Value'))
        bonus = int(self.fertility.findtext('LimitedLodeIncreaseMaximumTech/IncreaseMaximumPerTech'))
        self.assertEqual((cap, bonus), (950, 250))
        self.assertEqual(min(cap, 900 + self.refill(5793)), 950)
        self.assertEqual(min(cap, 0 + self.refill(5793)), 840)
        self.assertEqual(min(cap + bonus, self.refill(5793, research=1)), 1200)

    def test_old_distance_settings_fail_the_equality_requirement(self):
        self.assertEqual(native_amount(700, 5000, 3500, 1.2, 0.5), 0)
        # 0.3.1's million-unit range still loses integer units at distant islands.
        old = [native_amount(700, d, 1000000, 1.2) for d in DISTANCES]
        self.assertGreater(len(set(old)), 1)

    def test_updating_030_and_031_keeps_maps_and_avoids_duplicates(self):
        maps = [op for op in self.packaged if op.get('GUID') in ('3377', '44421', '44422')]
        self.assertEqual(len(maps), 6)
        for previous_version in ('0.3.0', '0.3.1'):
            previous = ET.Element('ModOps')
            previous.extend(copy.deepcopy(maps))
            if previous_version == '0.3.1':
                for op in list(self.fragment)[:2]:
                    old = copy.deepcopy(op)
                    old[0].text = '1000000'
                    previous.append(old)
            result = apply_obsidian_ops(previous, self.fragment)
            with self.subTest(version=previous_version):
                self.assertEqual(len(result), 12)
                self.assertEqual([signature(op) for op in result[:6]], [signature(op) for op in maps])
                self.assertEqual(signature(result), signature(self.packaged))

    def test_reapplying_update_is_stable(self):
        result = apply_obsidian_ops(copy.deepcopy(self.packaged), self.fragment)
        self.assertEqual(signature(result), signature(self.packaged))


if __name__ == '__main__':
    unittest.main(verbosity=2)
