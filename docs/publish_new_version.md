# Publishing a New Version of Your Package

This guide will walk you through the steps to publish a new version of your package.

## Prerequisites

Ensure you have the following:

- Latest code changes committed and pushed to your repository.
- A GitHub account with access to the repository.
- A PyPI account for package distribution.

## Steps

1. **Update the Version Number**

    In your `pyproject.toml` file, update the version number to the new version.
    For example, if the new version is `0.0.8`, it should look like this:

    ```toml
    [project]
    name = "firipy"
    version = "0.0.8"
    ...
    ```

2. **Commit and Push Your Changes**

    Commit the changes to your `pyproject.toml` file and push them to your repository.

    ```bash
    git add pyproject.toml
    git commit -m "Bump version to 0.0.8"
    git push
    ```

3. **Create a New Release on GitHub**

    Navigate to the "Releases" section of your GitHub repository and click "Draft a new release".
    Enter `0.0.8` as the tag version and title, and write a description of the changes in this release.
    Then click "Publish release".

    ![GitHub Release](./images/github_release.png)

## Post-Publishing

After you publish the release, your GitHub Actions workflow will automatically build and publish the new version of your package to PyPI.
You can check the "Actions" tab in your GitHub repository to see the progress and results of the workflow.

## Troubleshooting

If you encounter any issues during the publishing process, refer to the [GitHub](https://docs.github.com/en/github) and [PyPI](https://pypi.org/help/) documentation, or contact the repository maintainer.

Happy coding!
