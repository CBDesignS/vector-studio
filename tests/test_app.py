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

    def test_desktop_launcher_uses_free_local_port_and_closes(self):
        server = Mock(server_port=54321)
        server.serve_forever.side_effect = KeyboardInterrupt
        with patch.object(launcher, 'make_server', return_value=server) as make_server, \
                patch.object(launcher.threading, 'Timer') as timer:
            launcher.main()
        make_server.assert_called_once_with('127.0.0.1', launcher.PREFERRED_PORT, app, threaded=True)
        self.assertEqual(timer.call_args.kwargs['args'], ('http://127.0.0.1:54321',))
        timer.return_value.start.assert_called_once()
        timer.return_value.cancel.assert_called_once()
        server.server_close.assert_called_once()

    def test_launcher_falls_back_if_preferred_port_is_busy(self):
        server = Mock(server_port=54322)
        server.serve_forever.side_effect = KeyboardInterrupt
        with patch.object(launcher, 'make_server', side_effect=[SystemExit(1), server]) as make_server, \
                patch.object(launcher.threading, 'Timer'):
            launcher.main()
        self.assertEqual(make_server.call_count, 2)
        self.assertEqual(make_server.call_args.args[:2], ('127.0.0.1', 0))
        server.server_close.assert_called_once()


if __name__ == '__main__':
    unittest.main()
