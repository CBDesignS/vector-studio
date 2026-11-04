import io
import unittest
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw
from app import app, trace_lock


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


if __name__ == '__main__':
    unittest.main()
