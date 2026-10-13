import unittest
from .common import KodiHarness, ADDON


class ProfileTests(unittest.TestCase):
    def test_explicit_activation_then_switch_is_isolated(self):
        with KodiHarness() as k:
            neutral = [i.label for _, i, _ in k.call('?row=context-a')]
            self.assertTrue(k.profile.activate(str(ADDON), 'andy'))
            andy = [i.label for _, i, _ in k.call('?row=context-a')]
            self.assertNotEqual(neutral, andy)
            k.active = 'Dad'
            self.assertEqual([i.label for _, i, _ in k.call('?row=context-a')], neutral)
            self.assertTrue(k.profile.activate(str(ADDON), 'dad'))
            dad = [i.label for _, i, _ in k.call('?row=context-a')]
            self.assertNotEqual(dad, andy)
            k.active = 'Andy'
            self.assertEqual([i.label for _, i, _ in k.call('?row=context-a')], andy)

    def test_query_string_cannot_impersonate_profile(self):
        with KodiHarness() as k:
            k.profile.activate(str(ADDON), 'andy')
            a = [i.label for _, i, _ in k.call('?row=context-a')]
            b = [i.label for _, i, _ in k.call('?row=context-a&profile=Dad')]
            self.assertEqual(a, b)

    def test_shared_scope_does_not_show_previous_profile(self):
        with KodiHarness() as k:
            k.shared = True
            self.assertTrue(k.profile.activate(str(ADDON), 'andy'))
            k.active = 'Dad'
            self.assertIsNone(k.profile.read_snapshot())
            self.assertEqual(k.rows.listed_items(str(ADDON), 'context-a'),
                             k.fixtures.load_rows(str(ADDON), 'neutral')['context-a'])
            self.assertTrue(k.profile.activate(str(ADDON), 'dad'))
            k.active = 'Andy'
            self.assertIsNone(k.profile.read_snapshot())

    def test_duplicate_labels_or_unresolved_scope_fail_closed(self):
        with KodiHarness() as k:
            k.duplicate_labels = True
            self.assertFalse(k.profile.activate(str(ADDON), 'andy'))
            self.assertIsNone(k.profile.read_snapshot())
            k.duplicate_labels = False
            k.ambiguous_path = True
            self.assertFalse(k.profile.activate(str(ADDON), 'andy'))
            self.assertIsNone(k.profile.current_scope())
