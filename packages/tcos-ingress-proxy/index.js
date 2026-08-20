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

  return new Response('Not found', { status: 404 })
}
