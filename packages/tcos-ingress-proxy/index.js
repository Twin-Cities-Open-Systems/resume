addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

// Keep in sync with dist/people.json (slug -> public_dns)
const PEOPLE = {
  'spencer': 'spencer.blog.tcos.us',
  'touchy-claude': 'touchy.blog.tcos.us',
}

async function handleRequest(request) {
  const url = new URL(request.url)
  const match = url.pathname.match(/^\/people\/([^/]+)\/?$/)

  if (match && PEOPLE[match[1]]) {
    return Response.redirect(`https://${PEOPLE[match[1]]}${url.search}`, 301)
  }

  if (match) {
    return notFoundPage(match[1])
  }

  return new Response('Not found', { status: 404 })
}

function notFoundPage(slug) {
  const html = `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Not found — TCOS</title>
<meta http-equiv="refresh" content="3;url=https://tcos.us/people">
<style>
  :root { color-scheme: dark; }
  body {
    margin: 0; min-height: 100vh; display: flex; align-items: center; justify-content: center;
    background: #0b0d10; color: #e6e8eb;
    font: 16px/1.5 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  }
  main { text-align: center; max-width: 28rem; padding: 2rem; }
  h1 { font-size: 1.25rem; margin: 0 0 0.5rem; }
  p { color: #9aa4b2; margin: 0 0 1.5rem; }
  code { color: #e6e8eb; background: #171a1f; padding: 0.1rem 0.4rem; border-radius: 0.25rem; }
  a {
    display: inline-block; color: #0b0d10; background: #e6e8eb; text-decoration: none;
    padding: 0.6rem 1.2rem; border-radius: 0.4rem; font-weight: 600;
  }
  a:hover { opacity: 0.85; }
</style>
</head>
<body>
  <main>
    <h1>No one here named <code>${escapeHtml(slug)}</code></h1>
    <p>Redirecting you to the People page in a few seconds.</p>
    <a href="https://tcos.us/people">Go to People →</a>
  </main>
</body>
</html>`
  return new Response(html, { status: 404, headers: { 'Content-Type': 'text/html; charset=utf-8' } })
}

function escapeHtml(s) {
  return s.replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]))
}
