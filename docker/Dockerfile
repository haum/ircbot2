FROM ubuntu:24.04

RUN apt-get update && apt-get install -y locales tzdata git make rsync curl && rm -rf /var/lib/apt/lists/* \
	&& localedef -i fr_FR -c -f UTF-8 -A /usr/share/locale/locale.alias fr_FR.UTF-8
ENV LANG fr_FR.utf8

CMD ["/app/run.sh"]
