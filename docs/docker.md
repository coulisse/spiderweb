<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/docker/docker-original-wordmark.svg" alt="Docker logo" width="100" />

You can run Spiderweb using a Docker image to simplify deployment and the runtime environment.

#### 1. Download the pre-built Docker image

If you want to avoid building locally, you can download the ready-to-use Docker image from the **GitHub Container Registry** for a specific version:

```console
docker pull ghcr.io/coulisse/spiderweb:<TAG>
```

Check the available tags on the [project's GitHub Container Registry page](https://github.com/coulisse/spiderweb/pkgs/container/spiderweb).  
After downloading, you can start the container by following the instructions in the “Running with Docker” section.

If the image is not yet publicly available, follow the next section to build it locally.

#### 2. Building the Docker image (alternative)

To build the Docker image locally, **use the `scripts/docker_build.sh` script** which handles all necessary operations and automatically tags the image according to the version specified in `static/version.txt`.

Run from the root of the repository:

```console
cd scripts
./docker_build.sh
```

The image will be created and tagged as:

```
spiderweb:<version>
```

where `<version>` matches the content of the `static/version.txt` file.

> **Note:** There is no need to run `docker build` manually: everything is already handled by the `docker_build.sh` script.  
> If you want to update the version, edit the `static/version.txt` file first.

For more details or additional options, check the [`scripts/docker_build.sh`](https://github.com/coulisse/spiderweb/blob/main/scripts/docker_build.sh) script directly.

#### 3. Running with Docker

To start the container, you **must** mount the `local` folder from your host into the container and **must expose the port actually used by the WSGI server** (for example, 8080):

```console
docker run -d \
  --name spiderweb \
  -p 8080:8080 \
  -v $(pwd)/local:/app/local \
  ghcr.io/coulisse/spiderweb:latest
```

- `-p 8080:8080` exposes port 8080 of the container on the same port of the host. **Be sure to use the port configured in the WSGI server inside the container!**
- `-v $(pwd)/local:/app/local` is **mandatory** and is used to share essential files for DXSpider integration and custom configurations.

**Structure of the `local` folder**

The `local` folder, mounted as a volume, contains persistent data and configuration. Its typical structure is:

```
local/
└── cfg/
│   └── config.json
└── log/
└── data/
    └── visits.json

```

> **Important:**  
> Everything stored in `local` is **never overwritten** when you update the Docker image or restart/recreate the container.  
> This way, your custom configurations and local data remain intact across updates.

> **Note:** The application reads all configuration (DB, user, password, telnet, etc.) from the file `/app/local/cfg/config.json`, which corresponds to `local/cfg/config.json` on your host machine.  
> If you want to change database connection parameters or other options, edit this file directly in the `local` folder.

#### 4. Connecting to MariaDB/MySQL from the container

To run Spiderweb, the Docker container must be able to connect to a MariaDB/MySQL instance accessible over the network.

**Techniques for connecting between container and database on the host**

- **MariaDB/MySQL running on the host (not in Docker):**
  - In the configuration file (`local/cfg/config.json`), you can set the database host as:
    - **host.docker.internal**  
      This special hostname is recognized by Docker on Windows and macOS, and allows the container to reach the host directly.
      - On Linux, `host.docker.internal` is only available with recent Docker versions. If it doesn't work, use the host's IP address.
    - **Host IP address**  
      Alternatively, get your machine's IP (e.g., with `ip a` or `ifconfig`) and use it as the host in the config.
      - Example: `"host": "192.168.1.100"`

  - **GRANT for the MariaDB/MySQL user (READ ONLY):**  
    If you use the host's IP address, make sure the user has read-only permissions from that IP.  
    Example command to grant read-only privileges:
    ```sql
    GRANT SELECT ON spiderwebdb.* TO 'spiderwebuser'@'172.17.%.%' IDENTIFIED BY 'password';
    FLUSH PRIVILEGES;
    ```
    Replace `'172.17.%.%'` with the IP or subnet from which Docker connects (for example, Docker's bridge subnet).

- **MariaDB/MySQL on a remote server:**
  - Set the remote server's hostname or IP directly in the config.
  - Make sure the remote server's firewall allows connections from the Docker container.
  - Be sure to grant only the necessary read privileges to the user you use for Spiderweb.

> **Note:**  
> For security reasons, only grant SQL privileges for the specific host or subnet required, and never use the root user in production.

#### 5. Accessing the application

After starting, the application will be available at `http://localhost:8080` (or whichever port you exposed).
