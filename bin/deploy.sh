#!/bin/bash

tar -zcvf \
    /tmp/image_scraper.tar.gz \
    --dereference \
    --exclude=output \
    --exclude=.git  \
    ./

ansible-playbook playbook/deploy.yml -K
