#!/bin/bash
cd `dirname $0`
script_dir=$(cd $(dirname $0); pwd)
npx livereloadx $script_dir