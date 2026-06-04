# Publishing to PyPI

This project is configured to publish the `blakemere-autowrapper` distribution using GitHub Actions trusted publishing.

Use TestPyPI first, then production PyPI. TestPyPI and PyPI are separate services with separate accounts, separate trusted-publisher settings, and separate package namespaces.


## One-time TestPyPI setup

1. Create or sign in to a TestPyPI account: <https://test.pypi.org/account/register/>
2. Enable 2FA on the TestPyPI account.
3. Add a pending trusted publisher for the TestPyPI project name `blakemere-autowrapper`.
4. In TestPyPI, configure a trusted publisher with:
   - Owner: `RusDavies`
   - Repository name: `blakemere-autowrapper`
   - Workflow filename: `publish-testpypi.yml`
   - Environment name: `testpypi`

No TestPyPI API token is needed when trusted publishing is configured correctly.

## GitHub TestPyPI environment

The TestPyPI publishing workflow uses the GitHub environment named `testpypi`.

Recommended GitHub settings:

- Require manual approval for the `testpypi` environment.
- Restrict who can approve deployments to trusted maintainers.

## Publishing to TestPyPI first

Because the package distribution name changed after `v0.1.0`, use `v0.1.1`, use the manual TestPyPI workflow once TestPyPI trusted publishing is configured:

1. Open: <https://github.com/RusDavies/blakemere-autowrapper/actions/workflows/publish-testpypi.yml>
2. Click **Run workflow**.
3. Enter `v0.1.1` as the `ref`.
4. Approve the `testpypi` GitHub environment deployment if prompted.
5. Verify the TestPyPI page: <https://test.pypi.org/project/blakemere-autowrapper/>
6. Test installation from TestPyPI:

   ```bash
   python -m venv /tmp/blakemere-autowrapper-testpypi
   /tmp/blakemere-autowrapper-testpypi/bin/python -m pip install --upgrade pip
   /tmp/blakemere-autowrapper-testpypi/bin/python -m pip install --index-url https://test.pypi.org/simple/ blakemere-autowrapper==0.1.1
   /tmp/blakemere-autowrapper-testpypi/bin/python -c "from autowrapper import AutoWrapper; print(AutoWrapper)"
   ```

Only publish to production PyPI after TestPyPI upload and install verification succeed.

## One-time PyPI setup

1. Create or sign in to a PyPI account: <https://pypi.org/account/register/>
2. Enable 2FA on the PyPI account. PyPI requires this for publishing.
3. Create the project on PyPI by publishing the first release, or add a pending trusted publisher for the project name `blakemere-autowrapper`.
4. In PyPI, configure a trusted publisher with:
   - Owner: `RusDavies`
   - Repository name: `blakemere-autowrapper`
   - Workflow filename: `publish-pypi.yml`
   - Environment name: `pypi`

No PyPI API token is needed when trusted publishing is configured correctly. GitHub requests a short-lived publishing token from PyPI using OIDC.

## GitHub production PyPI environment

The production publishing workflow uses the GitHub environment named `pypi`.

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

## Python 3.8 and license metadata warning policy

The project currently supports Python 3.8 through 3.13. To keep Python 3.8 builds working with the setuptools versions resolved by CI, `pyproject.toml` intentionally uses the older compatible license metadata form:

```toml
license = {file = "LICENSE"}
```

Recent setuptools versions emit deprecation warnings recommending SPDX metadata, for example `license = "MIT"`, and removal of the MIT license classifier. Those warnings are accepted for now because the SPDX form previously broke the Python 3.8 CI wheel build.

Do not modernize the license metadata in isolation. When the project is ready to drop Python 3.8, update these together in one release-prep change:

- `requires-python`
- GitHub Actions CI matrix
- README support statement
- `pyproject.toml` license metadata and classifiers
- package version

Until then, a successful build that includes `LICENSE` in both the sdist and wheel is preferred over warning-free metadata that breaks Python 3.8.

## Publishing a production release

Production publishing is normally triggered by creating a GitHub release from a version tag:

1. Update `pyproject.toml` version if needed.
2. Commit the version change.
3. Tag the release, for example:

   ```bash
   git tag -a v0.1.1 -m "Release v0.1.1"
   git push origin main v0.1.1
   ```

4. Create/publish the GitHub release.
5. The `Publish to PyPI` workflow runs on the published release.
6. Approve the `pypi` GitHub environment deployment if approval is enabled.
7. Verify the package page: <https://pypi.org/project/blakemere-autowrapper/>

## Publishing `v0.1.1` to production PyPI

Because the package distribution name changed after `v0.1.0`, use `v0.1.1`, use the manual production workflow once PyPI trusted publishing is configured and TestPyPI has been verified:

1. Open: <https://github.com/RusDavies/blakemere-autowrapper/actions/workflows/publish-pypi.yml>
2. Click **Run workflow**.
3. Enter `v0.1.1` as the `ref`.
4. Approve the `pypi` environment deployment if prompted.
5. Verify: <https://pypi.org/project/blakemere-autowrapper/>

## Important constraints

- PyPI and TestPyPI project names are first-come and cannot be casually renamed after publishing.
- A released version number cannot be reused on PyPI or TestPyPI after upload, even if the file is deleted.
- TestPyPI is not a perfect mirror of production PyPI, but it catches workflow, metadata, and install problems before they become permanent production mistakes.
- Test the build locally before publishing. PyPI is not where packaging mistakes should go to become immortal.
