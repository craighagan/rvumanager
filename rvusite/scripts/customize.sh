#!/bin/bash
if [ ! -d /etc/rvu ]; then
  sudo mkdir /etc/rvu
  sudo chmod +rx /etc/rvu
fi

aws s3 --region us-east-1 cp s3://com-cih-rvu-config/etc/rvu/config.json /tmp/config.json && sudo mv /tmp/config.json /etc/rvu

