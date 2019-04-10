from .graph_api import FacebookGraphApi


class UserProfileApi(FacebookGraphApi):
    async def get(self, user_id, fields=None):
        params = {}
        if fields is not None and isinstance(fields, (list, tuple)):
            params['fields'] = ",".join(fields)

        params.update(self.auth_args)

        request_endpoint = '{0}/{1}'.format(self.graph_url, user_id)
        async with self.session.get(request_endpoint, params=params) as resp:
            status_code = await resp.status
            if status_code == 200:
                return await resp.json()
            return None
