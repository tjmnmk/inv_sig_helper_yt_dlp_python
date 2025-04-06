# inv_sig_helper (Python Replacement)

* `inv_sig_helper` is a drop-in replacement for the original Rust-based `inv_sig_helper`. This Python implementation uses `yt-dlp` for decrypting YouTube signatures instead of relying on custom-built decryption code. It provides the same TCP interface for signature decryption and related operations.
* Fully compatible with the original `inv_sig_helper` API.

### Replace default inv_sig_helper

* `docker stop "$(docker ps |grep sig_helper |awk '{print 1$}')"` # and remove the service from `docker-compose.yaml`
* `git clone https://github.com/tjmnmk/inv_sig_helper_yt_dlp_python.git`
* `cd inv_sig_helper_yt_dlp_python`
* `./docker_rebuild.sh`

### Automating Updates with Cron

You can add the docker_rebuild.sh script to your system's cron jobs. This will periodically rebuild and restart the service, ensuring that yt-dlp are kept up-to-date.

1. Open the crontab editor: `crontab -e`
2. Add the following line to schedule the script to run every 6 hours (adjust the schedule as needed):
```
0 */6 * * * cd /path/to/inv_sig_helper_yt_dlp_python/; ./docker_rebuild.sh`
```
3. Save and exit the editor.

**Note:** Replace /path/to/inv_sig_helper_yt_dlp_python with the actual path to the project directory on your system.

This will ensure the service is rebuilt and restarted automatically, keeping all dependencies and the service itself up-to-date.

###  Environment Variables
The following environment variables can be configured to customize the behavior of the inv_sig_helper_yt_dlp_python service:

Variable|Default Value|Description
| -------- | ------- | ------- |
HOST|0.0.0.0|The host address the service will bind to.
PORT|12999|The port the service will listen on.
LOG_LEVEL|INFO|The logging level for the service. Valid values are DEBUG, INFO, WARNING, ERROR, and CRITICAL.

#### How to Set Environment Variables

You can set these environment variables in the `docker-compose.yaml`.

**Note:** If you change the `PORT` environment variable, make sure to also update the `EXPOSE` directive in the `Dockerfile` to match the new port.

