# CI/CD Pipeline

Weather Shield uses GitHub Actions for continuous integration, testing, and deployment.

## Workflows

### 1. CI/CD Pipeline (`ci-cd.yml`)

Main pipeline that runs on every push and pull request.

#### Stages:

**Lint and Test**
- Runs on Python 3.8, 3.9, 3.10, 3.11, 3.12
- Syntax checking with flake8
- Code style with black
- Import sorting with isort
- Python compilation check

**Build and Test**
- Installs dependencies
- Runs application test
- Tests imports

**Docker Build**
- Builds Docker image
- Tests Docker container

**Release** (on tag creation)
- Builds distribution packages
- Creates GitHub release
- Publishes to PyPI

**Docker Release** (on tag creation)
- Builds and pushes to Docker Hub

**Security Scan**
- Trivy vulnerability scanning
- Reports to GitHub Security

**Coverage**
- Runs coverage analysis
- Uploads to Codecov

### 2. Code Quality (`code-quality.yml`)

Runs on every push and pull request to main/develop branches.

- Pylint analysis (target score: 8.0)
- Type checking with mypy
- Security scan with bandit
- SonarCloud integration

### 3. Documentation (`documentation.yml`)

Runs on documentation changes.

- Markdown linting
- Builds documentation
- Deploys to GitHub Pages (on merge to main)

## Triggering Workflows

### Automatic Triggers

- **Push to main/develop**: All workflows run
- **Pull request to main/develop**: Lint and code quality checks run
- **Tag creation** (v*): Release and docker-release jobs run

### Manual Trigger

You can manually trigger workflows using:

```bash
# Trigger via GitHub CLI
gh workflow run ci-cd.yml --ref main
gh workflow run code-quality.yml --ref main
gh workflow run documentation.yml --ref main
```

## Configuration

### Secrets Required

Set these in GitHub repository settings (Settings → Secrets and variables → Actions):

```
PYPI_API_TOKEN      # PyPI authentication token
DOCKER_USERNAME     # Docker Hub username
DOCKER_PASSWORD     # Docker Hub password
SONAR_TOKEN         # SonarCloud token
```

### Optional Configuration

- Modify Python versions in `ci-cd.yml` strategy matrix
- Adjust pylint threshold in `code-quality.yml`
- Update documentation deployment settings in `documentation.yml`

## Release Process

### Creating a Release

1. Update version in:
   - `weather_shield.py` (if version constant exists)
   - `setup.py`
   - `flake.nix`
   - `debian/changelog`

2. Commit changes:
   ```bash
   git add -A
   git commit -m "bump: version to 1.1.0"
   ```

3. Create annotated tag:
   ```bash
   git tag -a v1.1.0 -m "Release version 1.1.0"
   git push origin v1.1.0
   ```

4. GitHub Actions will:
   - Run all tests
   - Build and publish to PyPI
   - Build and push Docker image
   - Create GitHub release

### Version Numbering

Follow semantic versioning: `MAJOR.MINOR.PATCH`

- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes

## Monitoring Workflows

### View Workflow Status

1. Go to repository → Actions tab
2. Click on workflow name to see details
3. Click on specific run to see logs

### Debugging Failed Workflows

1. Click on failed workflow run
2. Expand failed job section
3. Review error logs
4. Make fixes and push again

## Local Testing

Before pushing, test locally:

```bash
# Install dependencies
pip install -r requirements.txt
pip install flake8 black isort

# Run linting
flake8 weather_shield.py
black --check weather_shield.py
isort --check-only weather_shield.py

# Build Docker image
docker build -t weather-shield:test .

# Test syntax
python -m py_compile weather_shield.py
```

## Performance Optimization

### Caching

Workflows use caching for:
- Python pip dependencies
- Docker layers

To clear cache:

```bash
# Via GitHub CLI
gh actions-cache delete <cache-key> -R <repo>

# Or via web interface: Settings → Actions → General
```

### Parallel Execution

Jobs that don't depend on each other run in parallel:
- lint-and-test
- security-scan

This significantly reduces total pipeline time.

## Troubleshooting

### PyPI Upload Fails

- Verify PYPI_API_TOKEN is correct
- Ensure version is not already published
- Check PyPI account has necessary permissions

### Docker Push Fails

- Verify DOCKER_USERNAME and DOCKER_PASSWORD
- Ensure Docker Hub account has repository access
- Check image naming is correct

### Tests Timeout

- Increase timeout in workflow YAML
- Check for hanging processes
- Review resource constraints

### Code Quality Checks Fail

- Run linters locally to fix issues
- Update configuration thresholds if needed
- Review SonarCloud feedback

## Badges

Add to README.md:

```markdown
![CI/CD Pipeline](https://github.com/palpitate013/weather-shield/workflows/CI%2FCD%20Pipeline/badge.svg)
![Code Quality](https://github.com/palpitate013/weather-shield/workflows/Code%20Quality/badge.svg)
![Documentation](https://github.com/palpitate013/weather-shield/workflows/Documentation/badge.svg)
[![codecov](https://codecov.io/gh/palpitate013/weather-shield/branch/main/graph/badge.svg)](https://codecov.io/gh/palpitate013/weather-shield)
[![SonarCloud](https://sonarcloud.io/api/project_badges/measure?project=palpitate013_weather-shield&metric=alert_status)](https://sonarcloud.io/dashboard?id=palpitate013_weather-shield)
```

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Workflow syntax reference](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions)
- [PyPI Publishing](https://packaging.python.org/tutorials/packaging-projects/)
- [Docker Hub](https://hub.docker.com/)
