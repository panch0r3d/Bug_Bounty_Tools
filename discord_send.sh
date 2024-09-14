#!/bin/bash

# Generalized Discord Notification Script

channel_url=${2:-'bugbounty'}
if [[ $channel_url == "channel_1" ]]; then
    discord_url="https://discord.com/api/webhooks/XXXXXXXXXXXXXXXXXXX"
elif [[ $channel_url == "channel_2" ]]; then
    discord_url="https://discord.com/api/webhooks/XXXXXXXXXXXXXXXXXXX"
elif [[ $channel_url == "channel_3" ]]; then
    discord_url="https://discord.com/api/webhooks/XXXXXXXXXXXXXXXXXXX"
else # default channel
    discord_url="https://discord.com/api/webhooks/XXXXXXXXXXXXXXXXXXX"
fi

#data=($(cat $1 ))
# Define a function to send a message
send_discord_notification() {
  local message=$1

  # Construct payload
  local payload=$(cat <<EOF
{
  "content": "$message"
}
EOF
)

  # Send POST request to Discord Webhook
  curl -H "Content-Type: application/json" -X POST -d "$payload" $discord_url
}

# Use the function
cat $1 | sed 's/\r//g' | while read data ; do send_discord_notification "$data" ; done
