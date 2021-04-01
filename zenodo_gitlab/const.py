import typing as ty
import zenodo_gitlab.objects

zen_url_sandbox: str = 'https://sandbox.zenodo.org'
zen_url: str = 'https://zenodo.org'
gl_archive_formats: ty.Set[str] = {'zip', 'tar.gz', 'tar.bz2', 'tar'}
default_archive_format: zenodo_gitlab.objects.ArchiveFormat = zenodo_gitlab.objects.ArchiveFormat.ZIP
