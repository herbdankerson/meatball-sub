import { createServer } from 'http';
import { stat } from 'fs/promises';
import { createReadStream } from 'fs';
import { extname, join } from 'path';

const PORT = process.env.PORT || 3000;
const PUBLIC_DIR = './public';
const API_URL = process.env.API_URL || 'http://localhost:3001';

const mimeTypes = {
  '.html': 'text/html',
  '.css': 'text/css',
  '.js': 'application/javascript',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.svg': 'image/svg+xml'
};

createServer(async (req, res) => {
  try {
    let url = req.url.split('?')[0];
    if (url.startsWith('/api')) {
      const apiRes = await fetch(`${API_URL}${url}`, {
        method: req.method,
        headers: { ...req.headers, host: undefined },
        body: ['POST', 'PUT', 'PATCH'].includes(req.method) ? req : undefined,
        duplex: 'half'
      });
      res.writeHead(apiRes.status, Object.fromEntries(apiRes.headers));
      apiRes.body.pipe(res);
      return;
    }
    if (url === '/') url = '/index.html';
    const filePath = join(PUBLIC_DIR, url);
    const fileStat = await stat(filePath);
    if (fileStat.isDirectory()) {
      res.statusCode = 404;
      res.end('Not found');
      return;
    }
    const ext = extname(filePath);
    res.setHeader('Content-Type', mimeTypes[ext] || 'application/octet-stream');
    createReadStream(filePath).pipe(res);
  } catch {
    res.statusCode = 404;
    res.end('Not found');
  }
}).listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
