#!/bin/bash
coffee --watch --compile static/js/*.coffee&
jade -w -P view/*.jade&

echo "The development environment has ready!"
