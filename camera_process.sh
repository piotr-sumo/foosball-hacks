#!/bin/bash

SLACK_TOKEN=$(<slack_token.txt)

rm -f $1.mp4
MP4Box -fps 60 -add $1.h264:fps=60 $1.mp4
ffmpeg \
  -i $1.mp4 \
  -r 15 \
  -vf scale=384:-1 \
  -ss 00:00:15 \
  $1.gif
rm -f $1.h264
aws s3 cp $1.mp4 s3://foosball-replays/ --acl public-read
aws s3 cp $1.gif s3://foosball-replays/ --acl public-read
echo "https://foosball-replays.s3.eu-central-1.amazonaws.com/$1.mp4"
curl -X POST -H 'Content-type: application/json' --data "{\"channel\": \"pl-foosball-hacking-replays\", \"text\":\"https://foosball-replays.s3.eu-central-1.amazonaws.com/$1.mp4\"}" "https://sumologic.slack.com/services/hooks/jenkins-ci?token=$SLACK_TOKEN"
rm -f $1.mp4
rm -f $1.gif
