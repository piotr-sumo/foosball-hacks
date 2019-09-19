#!/bin/bash

SLACK_TOKEN=$(<slack_token.txt)

MP4Box -fps 60 -add $1.h264:fps=60 $1.mp4
rm -f $1.h264

ffmpeg \
  -i $1.mp4 \
  -r 5 \
  -ss 00:00:25 \
  -to 00:00:33 \
  -filter:v "scale=512:-1, setpts=2*PTS" \
  $1.nonoptimized.gif

gifsicle -i $1.nonoptimized.gif --colors 64 --optimize=3 -o $1.gif
rm -f $1.nonoptimized.gif

aws s3 cp $1.mp4 s3://foosball-replays/ --acl public-read
rm -f $1.mp4

aws s3 cp $1.gif s3://foosball-replays/ --acl public-read
rm -f $1.gif

echo "https://foosball-replays.s3.eu-central-1.amazonaws.com/$1.mp4"
curl -X POST -H 'Content-type: application/json' --data "{\"channel\": \"pl-foosball-hacking-replays\", \"text\": \":soccer: GOAL! :soccer: \n See replay: https://foosball-replays.s3.eu-central-1.amazonaws.com/$1.mp4\", \"attachments\": [{\"fallback\": \"GIF\", \"text\": \"Replay GIF\", \"image_url\": \"https://foosball-replays.s3.eu-central-1.amazonaws.com/$1.gif\"}]}" "https://sumologic.slack.com/services/hooks/jenkins-ci?token=$SLACK_TOKEN"
