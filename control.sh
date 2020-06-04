#!/bin/sh

declare -a SYMBOLS=(
                 "ETHBTC" 
                 "BTCUSDT" 
                 "ETHUSDT"
                )

declare -a INTERVALS=(
                    "1m"
                    "30m"
                    "1h"
                    "4h"
                    "8h"
)

for i in "${INTERVALS[@]}"; do
  for s in "${SYMBOLS[@]}"; do
    python SMIerg2020.py "$s" "$i" > /dev/null &
    sleep 20
  done 
  sleep 60
done
