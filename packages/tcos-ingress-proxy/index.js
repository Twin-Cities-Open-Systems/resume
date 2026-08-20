addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  const url = new URL(request.url)
  const TARGET_HOST = 'resume-9wa.pages.dev'
  
  url.hostname = TARGET_HOST
  
  if (url.pathname.startsWith('/people/spencer')) {
    url.pathname = url.pathname.replace('/people/spencer', '')
    if (url.pathname === '') {
      url.pathname = '/'
    }
  }

  const modifiedRequest = new Request(url.toString(), {
    method: request.method,
    headers: new Headers(request.headers),
    body: request.body,
    redirect: 'manual'
  })

  modifiedRequest.headers.set('Host', TARGET_HOST)

  try {
    return await fetch(modifiedRequest)
  } catch (err) {
    return new Response(`Ingress Proxy Error: ${err.message}`, { status: 502 })
  }
}

