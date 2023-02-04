
#!/bin/sh

_=$(id -u lavalink &>/dev/null || groupadd -g 322 lavalink)
_=$(id -u lavalink &>/dev/null || useradd -u 322 -g 322 lavalink)
chown -R 322:322 ./logs
exec runuser -u lavalink -- "$@"
