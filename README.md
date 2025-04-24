# JB Filetools

A collection of lightweight tools for managing and organizing files across media storage workflows. Designed to be containerized for repeatable deployment on self-hosted infrastructure.

---

## 🚀 Quick Start: Deploy with LXC

To install and run `jb-filetools` in an LXC container:

### 1. Create a directory for deployment

```bash
mkdir -p ~/jb-filetools-deploy
cd ~/jb-filetools-deploy
```

### 2. Download the deployment scripts

Replace the version tag below with the latest release (e.g. `v0.1.1`):

```bash
curl -L https://github.com/james-berkheimer/jb-filetools/releases/download/v0.1.1/lxc-deploy-0.1.1.tar.gz | tar xz
```

### 3. Configure environment

Open `env-template` and adjust paths, networking, and settings for your Proxmox node.

Then rename it:

```bash
mv env-template env
```

### 4. Run the installer

```bash
sudo ./create.sh
```

This will:

- Create the LXC container
- Mount your media volumes
- Install `jb-filetools`
- Set up update and usage aliases inside the container

---

## 🛠 Features

- Dual-NIC container deployment for isolated media networking
- Mounts NFS shares directly from TrueNAS
- Handles LXC container creation, package install, and app setup
- Supports `filetools` CLI inside container
- Simple `update.sh` to pull latest version

---

## 🔁 Updating

To update the app inside the container:

```bash
update
```

This command is aliased to `/opt/jb-filetools/update.sh` and will:

- `git pull` the latest code
- Upgrade Python dependencies
- Reinstall the application

---

## 🔧 Developer Info

This repo includes:

- Full CI pipeline with version bump, tarball packaging, and GitHub Release upload
- Deployment scripts live in `deployment/lxc/`
- Releases available at:
  [https://github.com/james-berkheimer/jb-filetools/releases](https://github.com/james-berkheimer/jb-filetools/releases)

---

## 📦 Versioning

Versioning is handled automatically via GitHub Actions. You do not need to manually modify the `VERSION` file — it will be bumped, tagged, and released by the pipeline when changes are pushed to `main`.

---

## 📜 License

MIT © James Berkheimer
