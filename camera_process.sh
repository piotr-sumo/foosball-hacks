#!/bin/bash

rm -f $1.mp4
MP4Box -fps 60 -add $1.h264:fps=60 $1.mp4
rm -f $1.h264

