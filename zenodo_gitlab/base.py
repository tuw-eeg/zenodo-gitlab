import gitlab.v4.objects as glo
import zenodo_gitlab.objects as obj
import zenodo_gitlab.exceptions as exc
import typing as ty
import requests
import os


def get_archive_url(release: glo.ProjectRelease, archive_format: obj.ArchiveFormat) -> str:
    if not isinstance(archive_format, obj.ArchiveFormat):
        raise TypeError(f'archive_format should be of type {type(obj.ArchiveFormat)} and not {type(archive_format)}')
    try:
        return [source['url'] for source in release.assets['sources'] if source['format'] == archive_format.value][0]
    except IndexError:
        raise exc.NoSuchSourceArchiveException(f"No archive in the release of {archive_format.value} format")


def extract_archive_name_from_url(archive_url: str) -> str:
    return archive_url.split('/')[-1]


def download_archive(*, archive_url: str,
                     archive_name: ty.Optional[str] = None,
                     archive_name_fn: ty.Callable[[str], str] = extract_archive_name_from_url) -> None:
    r = requests.get(archive_url)
    filename = archive_name if archive_name is not None else archive_name_fn(archive_url)
    with open(filename, 'wb') as f:
        f.write(r.content)


def new_deposit(*, zen_token: str,
                zen_base_url: str,
                deposition_metadata: ty.Optional[ty.Dict[str, str]]) -> requests.Response:
    tail: str = '/api/deposit/depositions'
    url = "".join([zen_base_url, tail])
    params = dict(access_token=zen_token)
    json = deposition_metadata if deposition_metadata is not None else {}
    r = requests.post(url=url, json=json, params=params)
    return r


def upload_archive(*, zen_token: str, archive_name: str,
                   depo_bucket_url: str, cleanup: bool = True) -> requests.Response:
    with open(archive_name, 'rb') as fp:
        params = dict(access_token=zen_token)
        url = '/'.join([depo_bucket_url, archive_name])
        r = requests.put(url, params=params, data=fp)
    if cleanup:
        os.remove(archive_name)
    return r


def publish_deposition(*, zen_token: str, zen_base_url: str, deposition_id: int) -> requests.Response:
    url = f'{zen_base_url}/api/deposit/depositions/{deposition_id}/actions/publish'
    params = dict(access_token=zen_token)
    return requests.post(url, params=params)


def get_deposition_data(*, zen_token: str, zen_base_url: str, deposition_id: int) -> requests.Response:
    url = f'{zen_base_url}/api/deposit/depositions/{deposition_id}'
    params = dict(access_token=zen_token)
    return requests.get(url, params=params)


def get_depositions(*, zen_token: str, zen_base_url: str) -> requests.Response:
    url = f'{zen_base_url}/api/deposit/depositions'
    params = dict(access_token=zen_token)
    return requests.get(url, params=params)


def discard_deposition(*, zen_token: str, zen_base_url: str, deposition_id: int) -> requests.Response:
    url = f"{zen_base_url}/api/deposit/depositions/{deposition_id}"
    params = dict(access_token=zen_token)
    return requests.delete(url, params=params)
