# JB Filetools

A collection of lightweight tools for managing and organizing files across media storage workflows. Designed to be installed into a local virtual environment with easy update support.

---

## Quick Start: Install Locally

To install `jb-filetools` into `/opt/jb-filetools` with a virtual environment:

### 1. Download the installer bundle

```bash
curl -L https://github.com/james-berkheimer/jb-filetools/releases/latest/download/install-jb-filetools.tar.gz | tar xz
cd jb-filetools-installer
chmod +x install.sh
```

### 2. Run the installer

```bash
sudo ./install.sh
```

This will:

- Install Python and required tools
- Create a virtual environment in `/opt/jb-filetools/venv`
- Download the latest jb-filetools wheel from GitHub Releases
- Install jb-filetools into the venv
- Add aliases and environment config via `/etc/profile.d/filetools.sh`

---

## Aliases

After reboot or `source /etc/profile`, the following commands will be available:

```bash
filetools             # Run the CLI
update_filetools      # Pull latest jb-filetools release and install it
```

---

## Updating

To update the app:

```bash
update_filetools
```

This will:

- Download the latest jb-filetools wheel from GitHub Releases
- Install the new version into the existing venv
- Clean up temporary files

---

## Uninstalling

To remove jb-filetools completely:

```bash
sudo ./uninstall.sh
```

This will:

- Remove `/opt/jb-filetools`
- Remove the `/etc/profile.d/filetools.sh` alias file
- Recommend reboot or `source /etc/profile` to finalize cleanup

---

## Developer Info

This repo includes:

- Full CI pipeline with version bumping, wheel building, and GitHub Release upload
- Installer files live in the `install/` directory
- Releases available at: https://github.com/james-berkheimer/jb-filetools/releases

---

## Versioning

Versioning is handled automatically via GitHub Actions. The `VERSION` file is updated and tagged on every push to `main`.

---

## License

MIT © James Berkheimer
