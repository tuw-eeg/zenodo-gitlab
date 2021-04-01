import pytest
import gitlab
import gitlab.v4.objects as glo
from .config import env
import zenodo_gitlab.base as base
import zenodo_gitlab.objects as obj
import typing as ty


@pytest.fixture(scope='session')
def gitlab_instance() -> gitlab.Gitlab:
    yield gitlab.Gitlab(env['gitlab']['url'], env['gitlab']['token'])


@pytest.fixture(scope='session')
def gitlab_project(gitlab_instance: gitlab.Gitlab) -> glo.Project:
    yield gitlab_instance.projects.get(env['gitlab']['test-project-id'])


@pytest.fixture(scope='session')
def gitlab_project_release(gitlab_project: glo.Project) -> glo.ProjectRelease:
    [tag.delete() for tag in gitlab_project.tags.list()]
    tag = gitlab_project.tags.create({'tag_name': '1.0', 'ref': 'master'})
    tag.set_release_description("This is the release description")
    return gitlab_project.releases.list()[0]


@pytest.mark.parametrize('archive_format', [
    obj.ArchiveFormat.ZIP,
    obj.ArchiveFormat.TAR,
    obj.ArchiveFormat.TAR_GZ,
    obj.ArchiveFormat.TAR_BZ2,
])
def test_get_archive_url_when_format_is_valid(gitlab_project_release, archive_format):
    base.get_archive_url(gitlab_project_release, archive_format)


@pytest.mark.parametrize('archive_format', [
    'zip',
    1,
    2.0
])
def test_get_archive_url_when_format_has_invalid_type(gitlab_project_release, archive_format):
    with pytest.raises(TypeError):
        base.get_archive_url(gitlab_project_release, archive_format)


@pytest.fixture()
def archive_url() -> str:
    return 'https://gitlab.com/zenodo-test/some-spring-project/-/archive/1.0/some-spring-project-1.0.zip'


def test_download_archive(archive_url):
    base.download_archive(archive_url=archive_url)


@pytest.fixture(scope='session')
def deposition_metadata() -> ty.Dict[str, ty.Any]:
    import datetime
    return {
        'metadata': {
            'upload_type': 'software',
            'title': f'DOI Test - {datetime.datetime.now()}',
            'creators': [
                {
                    'name': 'Doe, John',
                    'affiliation': 'TU Wien'
                }
            ],
            'description': '<h1>HTML-compatible Description</h1>',
            'access_right': 'open',
            'license': 'LO-FR-2.0',  # https://zenodo.org/api/licenses/
            'keywords': ['k1', 'k2'],
            'notes': '<h2>HTML-compatible Notes</h2>'
        }
    }


@pytest.fixture(scope='session')
def zen_token() -> str:
    return env['zenodo-sandbox']['token']


@pytest.fixture(scope='session')
def zen_base_url() -> str:
    return env['zenodo-sandbox']['url']


def test_new_deposit(zen_token, zen_base_url, deposition_metadata):
    r = base.new_deposit(zen_token=zen_token,
                         zen_base_url=zen_base_url,
                         deposition_metadata=deposition_metadata)
    assert r.status_code == 201


@pytest.fixture(scope='session')
def archive_name() -> str:
    return 'some-spring-project-1.0.zip'


@pytest.fixture(scope='session')
def depo_bucket_url() -> str:
    return 'https://sandbox.zenodo.org/api/files/5a4cf752-7980-4b5b-8e46-b5379b624c7c'


def test_upload_archive(zen_token, archive_name, depo_bucket_url):
    base.upload_archive(zen_token=zen_token, archive_name=archive_name, depo_bucket_url=depo_bucket_url)
