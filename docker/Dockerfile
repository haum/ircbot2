FROM alpine:3.16

RUN apk add --no-cache git python3 py3-pip make rsync musl-locales \
 && pip install irc pelican icalendar

CMD ["/app/run.sh"]
