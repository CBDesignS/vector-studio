"""Filesystem fixtures never touch the user's real app or Desktop."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('mac_manage', ROOT / 'macos/manage.py')
mac = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mac)


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name).absolute()
        self.target = self.home / 'Library/Application Support/VectorStudioCuttingLab'
        self.target.mkdir(parents=True)
        (self.target / '.vector-studio-macos').write_text(mac.MARKER)
        (self.home / 'Desktop').mkdir()

    def test_target_and_identity_guards(self):
        mac.validate_target(self.target, self.home)
        for path in (self.home, self.target.parent, self.target / 'nested'):
            with self.assertRaises(ValueError):
                mac.validate_target(path, self.home)
        (self.target / '.vector-studio-macos').write_text('other-app')
        with self.assertRaises(ValueError):
            mac.validate_target(self.target, self.home)

    def test_copy_allowlist_and_rerun_from_installed_folder(self):
        mac.copy_sources(ROOT, self.target)
        mac.copy_sources(self.target, self.target)
        self.assertTrue((self.target / 'macos/Uninstall.command').is_file())
        self.assertFalse((self.target / 'windows').exists())
        self.assertFalse((self.target / 'Install.cmd').exists())

    def test_missing_sources_do_not_partially_update(self):
        source = self.home / 'incomplete'
        source.mkdir()
        (source / 'app.py').write_text('incomplete')
        with self.assertRaises(ValueError):
            mac.copy_sources(source, self.target)
        self.assertFalse((self.target / 'app.py').exists())

    def test_shortcuts_use_installed_folder_and_keep_other_files(self):
        other = self.home / 'Desktop/photo.txt'
        other.write_text('keep')
        mac.create_shortcuts(self.home)
        mac.create_shortcuts(self.home)
        launcher = self.home / 'Desktop/Vector Studio Cutting Lab.command'
        self.assertIn('Application Support/VectorStudioCuttingLab/macos/Setup.sh', launcher.read_text())
        self.assertTrue(launcher.read_text().endswith('run\n'))
        self.assertEqual(other.read_text(), 'keep')

    def test_unrelated_shortcut_name_is_not_overwritten(self):
        path = self.home / 'Desktop/Vector Studio Cutting Lab.command'
        path.write_text('someone else owns this')
        with self.assertRaises(ValueError):
            mac.create_shortcuts(self.home)
        self.assertEqual(path.read_text(), 'someone else owns this')

    def test_symlink_destination_is_refused(self):
        outside = self.home / 'keep.txt'
        outside.write_text('keep')
        link = self.target / 'app.py'
        try:
            link.symlink_to(outside)
        except OSError:
            self.skipTest('Symlink creation is unavailable on this test host.')
        with self.assertRaises(ValueError):
            mac.copy_sources(ROOT, self.target)
        self.assertEqual(outside.read_text(), 'keep')

    def test_windows_entry_points_and_relocation(self):
        for name in ('Install', 'Run', 'Uninstall'):
            self.assertTrue((ROOT / 'windows' / f'{name}.cmd').exists())
            self.assertFalse((ROOT / f'{name}.cmd').exists())
        setup = (ROOT / 'windows/Install.ps1').read_text()
        self.assertIn("Join-Path $destination 'windows\\Run.cmd'", setup)
        self.assertIn("Join-Path $destination 'windows\\Uninstall.cmd'", setup)


if __name__ == '__main__':
    unittest.main()
