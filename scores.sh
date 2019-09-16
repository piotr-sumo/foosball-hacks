#!/bin/bash

synthesize() {
	aws polly synthesize-speech --output-format mp3 --voice-id Kendra \
	--text "$1" "$2" --region us-west-2 --engine neural
	ffmpeg -i "$2" "$3"
}

synthesize "Game started! Good luck!" "voice_gamestarted.0.mp3" "voice_gamestarted.0.wav"

MAX_SCORE=10

MAPPINGS=("zero" "one" "two" "three" "four" "five" "six" "seven" "eight" "nine" "ten")

for reds in `seq 0 $MAX_SCORE`;
do
	for blues in `seq 0 $MAX_SCORE`;
	do
		REDZ="${MAPPINGS[$reds]}"
		BLUEZ="${MAPPINGS[$blues]}"

		if [ $reds -gt $blues ]; then
			echo "Reds are winning $REDZ $BLUEZ"
			synthesize "Reds are winning $REDZ $BLUEZ" "voice$reds.$blues.0.mp3" "voice$reds.$blues.0.wav"
			synthesize "$REDZ $BLUEZ for reds" "voice$reds.$blues.1.mp3" "voice$reds.$blues.1.wav"
			synthesize "Reds $REDZ $BLUEZ" "voice$reds.$blues.2.mp3" "voice$reds.$blues.2.wav"
			synthesize "Game ended! Reds won with score $REDZ $BLUEZ" "voice_gameended.$reds.$blues.0.mp3" "voice_gameended.$reds.$blues.0.wav"
		elif [[ $blues -gt $reds ]]; then
			echo "Blues are winning $BLUEZ $REDZ"
			synthesize "Blues are winning $BLUEZ $REDZ" "voice$reds.$blues.0.mp3" "voice$reds.$blues.0.wav"
			synthesize "$BLUEZ $REDZ for blues" "voice$reds.$blues.1.mp3" "voice$reds.$blues.1.wav"
			synthesize "Blues $BLUEZ $REDZ" "voice$reds.$blues.2.mp3" "voice$reds.$blues.2.wav"
			synthesize "Game ended! Blues won with score $BLUEZ $REDZ" "voice_gameended.$reds.$blues.0.mp3" "voice_gameended.$reds.$blues.0.wav"
		else
			echo "Tied $BLUEZ $REDZ"
			synthesize "Tied $BLUEZ $REDZ" "voice$reds.$blues.0.mp3" "voice$reds.$blues.0.wav"
			synthesize "$BLUEZ $REDZ draw" "voice$reds.$blues.1.mp3" "voice$reds.$blues.1.wav"
			synthesize "Game ended! The teams are tied!" "voice_gameended.$reds.$blues.0.mp3" "voice_gameended.$reds.$blues.0.wav"
		fi
	done
done    

#aws polly synthesize-speech --output-format mp3 --voice-id Kendra --text 'Hello, my name is Joanna. I learned about the W3C on 10/3 of last year.' hello.mp3 --region us-west-2 --engine neural