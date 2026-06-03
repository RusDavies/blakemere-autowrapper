# Publishing to PyPI

This project is configured to publish the `autowrapper` distribution to PyPI using GitHub Actions trusted publishing.

## One-time PyPI setup

1. Create or sign in to a PyPI account: <https://pypi.org/account/register/>
2. Enable 2FA on the PyPI account. PyPI requires this for publishing.
3. Create the project on PyPI by publishing the first release, or add a pending trusted publisher for the project name `autowrapper`.
4. In PyPI, configure a trusted publisher with:
   - Owner: `RusDavies`
   - Repository name: `blakemere-autowrapper`
   - Workflow filename: `publish-pypi.yml`
   - Environment name: `pypi`

No PyPI API token is needed when trusted publishing is configured correctly. GitHub requests a short-lived publishing token from PyPI using OIDC.

## GitHub environment

The publishing workflow uses the GitHub environment named `pypi`.

Recommended GitHub settings:

- Require manual approval for the `pypi` environment, at least while the package is new.
- Restrict who can approve deployments to trusted maintainers.

## Pre-publish checklist

Before publishing a release:

```bash
git status --short --branch
python -m py_compile AutoWrapper.py autowrapper.py tests/test_autowrapper.py
python -m unittest discover -s tests -v
python -m pip install --upgrade build twine
python -m build
python -m twine check dist/*
```

Also confirm that GitHub Actions CI is green for the commit being released.

## Publishing a release

Publishing is normally triggered by creating a GitHub release from a version tag:

1. Update `pyproject.toml` version if needed.
2. Commit the version change.
3. Tag the release, for example:

   ```bash
   git tag -a v0.1.0 -m "Release v0.1.0"
   git push origin main v0.1.0
   ```

4. Create/publish the GitHub release.
5. The `Publish to PyPI` workflow runs on the published release.
6. Approve the `pypi` GitHub environment deployment if approval is enabled.
7. Verify the package page: <https://pypi.org/project/autowrapper/>

## Publishing the existing `v0.1.0` release

Because `v0.1.0` already exists, use the manual workflow once PyPI trusted publishing is configured:

1. Open: <https://github.com/RusDavies/blakemere-autowrapper/actions/workflows/publish-pypi.yml>
2. Click **Run workflow**.
3. Enter `v0.1.0` as the `ref`.
4. Approve the `pypi` environment deployment if prompted.
5. Verify: <https://pypi.org/project/autowrapper/>

## Important constraints

- PyPI project names are first-come and cannot be casually renamed after publishing.
- A released version number cannot be reused on PyPI after upload, even if the file is deleted.
- Test the build locally before publishing. PyPI is not where packaging mistakes should go to become immortal.
