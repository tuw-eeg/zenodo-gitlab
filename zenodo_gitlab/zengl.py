import gitlab
import gitlab.v4.objects as glo
import zenodo_gitlab.const as const
import typing as ty
import zenodo_gitlab.base as base


class ZenodoGitLab:
    """
    Main class to handle the interactions between GitLab repositories and Zenodo.
    """

    def __init__(self, *, gitlab_instance: gitlab.Gitlab, zenodo_token: str, use_sandbox: bool = False):
        """
        ZenodoGitLab constructor.
        Collects all the necessary initial configurations to establish connection with GitLab and Zenodo.
        :param gitlab_instance: a pre-constructed gitlab.Gitlab instance, used for communicating with the GitLab API
        :type gitlab_instance: gitlab.Gitlab
        :param zenodo_token: access token with deposit:actions scope for Zenodo. It can be generated
        for non-sandbox at https://zenodo.org/account/settings/applications/tokens/new/ and
        for sandbox at https://sandbox.zenodo.org/account/settings/applications/tokens/new/
        :type zenodo_token: str
        :param use_sandbox: boolean flag whether sandbox version of Zenodo should be used.
        :type use_sandbox: bool
        Note that if ``use_sandbox`` is set to ``True``, ``zenodo_token`` should be a sandbox token.
        """
        self.gl = gitlab_instance
        self.zenodo_token = zenodo_token
        self.use_sandbox = use_sandbox
        self.base_url = const.zen_url_sandbox if use_sandbox else const.zen_url

    def create_deposit_for(self, *,
                           project: glo.Project,
                           tag_name: str,
                           ref: str,
                           release_description: str = '',
                           metadata: ty.Dict[str, ty.Any] = {}) -> int:
        # Create new deposit
        deposit_response = base.new_deposit(zen_token=self.zenodo_token,
                                            zen_base_url=self.base_url,
                                            deposition_metadata=metadata)
        deposit_json = deposit_response.json()
        deposition_id = deposit_json['id']
        # Create new release
        tag: glo.ProjectTag = project.tags.create(dict(tag_name=tag_name, ref=ref))
        tag.set_release_description(release_description)
        # Get newly created release
        latest_release = project.releases.list()[0]
        archive_url = base.get_archive_url(latest_release, const.default_archive_format)
        archive_name = base.extract_archive_name_from_url(archive_url)
        # Download archive then upload it to the bucket
        base.download_archive(archive_url=archive_url, archive_name=archive_name)
        base.upload_archive(zen_token=self.zenodo_token,
                            archive_name=archive_name,
                            depo_bucket_url=deposit_json["links"]["bucket"])
        return deposition_id

    def get_deposition_data(self, deposition_id: int) -> dict:
        return base.get_deposition_data(zen_token=self.zenodo_token,
                                        zen_base_url=self.base_url,
                                        deposition_id=deposition_id).json()

    def publish_deposition(self, deposition_id: int) -> dict:
        return base.publish_deposition(zen_token=self.zenodo_token,
                                       zen_base_url=self.base_url,
                                       deposition_id=deposition_id).json()

    def get_depositions(self):
        return base.get_depositions(zen_token=self.zenodo_token,
                                    zen_base_url=self.base_url)

    def discard_deposition(self, deposition_id: int):
        return base.discard_deposition(zen_token=self.zenodo_token,
                                       zen_base_url=self.base_url,
                                       deposition_id=deposition_id)