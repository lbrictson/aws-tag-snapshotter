Welcome to aws-tag-snapshotter
===================

### Contents

- [aws-tag-snapshotter](#aws-tag-snapshotter)
    - [Description](#description)
    - [Installation](#installation)
    - [Example](#example)
    - [Docker](#docker)

## Description ##
A simple tool for creating a daily snapshot of all volumes attached to an ec2 instance in AWS.  It removes the snapshot after 5 days.  This will leave you with a rolling 5 days worth of snapshots to perform restores on.

You will need aws credentials configured via the awscli or as ENV vars to run this tool.

For each instance you want a snapshot taken of just tag it with:

key: autosnap
value: true

## Installation ##
Simply run

    pip3 install aws-tag-snapshotter

## Example ##

Before running the examples make sure to tag instances you want snapshotted with the key autosnap and the value true

*Running it once*

    From awstagsnapshotter.app import run
    run()

*Running it as an endless process*

    From awstagsnapshotter.app import main
    main()

## Docker ##
A docker image of this utility is available that will run endlessly (until the container is stopped). 
Check the docker folder for the Dockerfile to build it.  Coming soon to dockerhub.