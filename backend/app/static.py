from pathlib import PurePosixPath
from starlette.exceptions import HTTPException
from starlette.staticfiles import StaticFiles


class SPAStaticFiles(StaticFiles):
    """Serve the built React app after API routes, including client navigation."""

    async def get_response(self, path, scope):
        if path == 'api' or path.startswith('api/'):
            raise HTTPException(404, 'Not Found')
        try:
            return await super().get_response(path, scope)
        except HTTPException as exc:
            # Missing assets, dotfiles and non-GET requests must remain errors.
            if exc.status_code != 404 or scope['method'] not in ('GET', 'HEAD'):
                raise
            if PurePosixPath(path).suffix or any(p.startswith('.') for p in PurePosixPath(path).parts):
                raise
            return await super().get_response('index.html', scope)
