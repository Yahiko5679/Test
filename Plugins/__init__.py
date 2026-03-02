from aiohttp import web

routes = web.RouteTableDef()


@routes.get("/", allow_head=True)
async def root(request):
    return web.Response(text="CosmicBotz is running!", status=200)


@routes.get("/health", allow_head=True)
async def health(request):
    return web.json_response({"status": "ok"})


async def web_server():
    app = web.Application(client_max_size=30_000_000)
    app.add_routes(routes)
    return app
