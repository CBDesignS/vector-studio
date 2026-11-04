import io
import unittest
import xml.etree.ElementTree as ET
from unittest.mock import Mock, patch
from PIL import Image, ImageDraw
from app import app, trace_lock
import launcher


class VectorStudioTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def image(self):
        image = Image.new('RGBA', (64, 64), 'white')
        ImageDraw.Draw(image).ellipse((10, 10, 54, 54), fill='red')
        ImageDraw.Draw(image).rectangle((20, 20, 40, 40), fill='black')
        output = io.BytesIO()
        image.save(output, format='PNG')
        output.seek(0)
        return output

    def test_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Vector Studio', response.data)

    def test_real_tracing_both_modes(self):
        for mode in ('color', 'binary'):
            with self.subTest(mode=mode):
                response = self.client.post('/api/vectorize', data={
                    'image': (self.image(), 'sample.png'), 'mode': mode})
                self.assertEqual(response.status_code, 200, response.data)
                root = ET.fromstring(response.json['svg'])
                self.assertEqual(root.tag, '{http://www.w3.org/2000/svg}svg')
                self.assertTrue(root.findall('.//{http://www.w3.org/2000/svg}path'))

    def test_invalid_inputs(self):
        self.assertEqual(self.client.post('/api/vectorize').status_code, 400)
        response = self.client.post('/api/vectorize', data={
            'image': (io.BytesIO(b'not an image'), 'bad.png')})
        self.assertEqual(response.status_code, 400)
        for value in ('9', 'NaN', '-1', 'oops'):
            response = self.client.post('/api/vectorize', data={
                'image': (self.image(), 'sample.png'), 'colors': value})
            self.assertEqual(response.status_code, 400)

    def test_busy(self):
        trace_lock.acquire()
        try:
            response = self.client.post('/api/vectorize', data={
                'image': (self.image(), 'sample.png')})
            self.assertEqual(response.status_code, 429)
        finally:
            trace_lock.release()

    def test_size_limit(self):
        response = self.client.post('/api/vectorize', data={
            'image': (io.BytesIO(b'x' * (12 * 1024 * 1024)), 'large.png')})
        self.assertEqual(response.status_code, 413)

    def ring(self, color='black', transparent=False):
        image = Image.new('RGBA', (80, 80), (255, 255, 255, 0 if transparent else 255))
        draw = ImageDraw.Draw(image)
        draw.rectangle((10, 10, 69, 69), fill=color)
        draw.rectangle((25, 25, 54, 54), fill=(255, 255, 255, 0 if transparent else 255))
        output = io.BytesIO()
        image.save(output, format='PNG')
        output.seek(0)
        return output

    def test_real_holes_and_no_white_backing(self):
        for mode, color in [('binary', 'black'), ('color', 'red')]:
            for alpha in (False, True):
                with self.subTest(mode=mode, alpha=alpha):
                    response = self.client.post('/api/vectorize', data={
                        'image': (self.ring(color, alpha), 'ring.png'), 'mode':mode,
                        'transparent':'1', 'width_mm':'75', 'trim':'1'})
                    self.assertEqual(response.status_code, 200, response.data)
                    root = ET.fromstring(response.json['svg'])
                    paths = root.findall('{http://www.w3.org/2000/svg}path')
                    self.assertEqual(len(paths), 1)
                    self.assertGreaterEqual(paths[0].get('d').upper().count('M'), 2)
                    self.assertEqual(paths[0].get('fill-rule'), 'evenodd')
                    self.assertNotIn(paths[0].get('fill').lower(), ('#ffffff', '#fefefe'))
                    self.assertEqual(root.get('width'), '75mm')
                    self.assertEqual(root.get('viewBox'), '0 0 60 60')
                    self.assertFalse(root.findall('{http://www.w3.org/2000/svg}rect'))

    def test_backing_is_explicit_and_preview_is_separate(self):
        response = self.client.post('/api/vectorize', data={
            'image': (self.ring(), 'ring.png'), 'transparent':'0'})
        self.assertEqual(response.status_code, 200, response.data)
        root = ET.fromstring(response.json['svg'])
        self.assertEqual(len(root.findall('{http://www.w3.org/2000/svg}rect')), 1)
        self.assertNotIn('stroke=', response.json['svg'])
        self.assertIn('stroke=', response.json['outline'])
        self.assertTrue(response.json['guide'].startswith('data:image/png;base64,'))

    def test_new_setting_bounds_and_empty_art(self):
        for key, value in [('width_mm','0'), ('threshold','NaN'), ('quality','9999'),
                           ('upscale','99'), ('transparent','yes'), ('background','red')]:
            with self.subTest(key=key):
                response = self.client.post('/api/vectorize', data={
                    'image': (self.image(), 'sample.png'), key:value})
                self.assertEqual(response.status_code, 400)
        blank = Image.new('RGB', (20,20), 'white')
        output = io.BytesIO()
        blank.save(output, format='PNG')
        output.seek(0)
        response = self.client.post('/api/vectorize', data={'image':(output,'blank.png')})
        self.assertEqual(response.status_code, 400)

    def test_inverted_alpha_and_detail_controls(self):
        response = self.client.post('/api/vectorize', data={
            'image': (self.ring('white', True), 'white-ring.png'), 'invert':'1',
            'upscale':'4', 'fitting':'polygon', 'width_mm':'80', 'quality':'3200'})
        self.assertEqual(response.status_code, 200, response.data)
        root = ET.fromstring(response.json['svg'])
        paths = root.findall('{http://www.w3.org/2000/svg}path')
        self.assertEqual(len(paths), 1)
        self.assertGreaterEqual(paths[0].get('d').upper().count('M'), 2)
        self.assertEqual(root.get('viewBox'), '0 0 240 240')
        self.assertEqual(root.get('width'), '80mm')

    def test_desktop_launcher_uses_free_local_port_and_closes(self):
        server = Mock(server_port=54321)
        server.serve_forever.side_effect = KeyboardInterrupt
        with patch.object(launcher, 'make_server', return_value=server) as make_server, \
                patch.object(launcher.threading, 'Timer') as timer:
            launcher.main()
        make_server.assert_called_once_with('127.0.0.1', 0, app, threaded=True)
        self.assertEqual(timer.call_args.kwargs['args'], ('http://127.0.0.1:54321',))
        timer.return_value.start.assert_called_once()
        timer.return_value.cancel.assert_called_once()
        server.server_close.assert_called_once()


if __name__ == '__main__':
    unittest.main()
