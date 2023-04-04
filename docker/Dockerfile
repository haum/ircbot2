FROM alpine:3.16

RUN apk add --no-cache git python3 py3-pip py3-pillow make rsync musl-locales \
 && pip install irc pelican icalendar piexif

CMD ["/app/run.sh"]
