FROM fredboat/lavalink:3.7.4

COPY application.yml entrypoint.sh ./

USER root

ENTRYPOINT ["/bin/sh", "entrypoint.sh"]
CMD ["java", "-Djdk.tls.client.protocols=TLSv1.1,TLSv1.2", "-Xmx1G", "-jar", "Lavalink.jar"]
