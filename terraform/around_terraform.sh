#!/bin/sh

directories=$(find . -name "resources.*" -maxdepth 2 -type d)

if [ 0 = ${#directories[@]} ]; then
  echo "target is nothing"
  exit 0
fi

for directory in $directories
do
  prefix=$(echo $directory | sed -e "s%/%%")
  prefix=$(echo $prefix | sed -e "s%.%%")
  prefix=$(echo $prefix | sed -e "s%/%_%g")
  for file in $(ls -F $directory | grep -v /)
  do
    if [ "before" = $1 ]; then
      ln -s $directory/$file $prefix.$file
    fi
    if [ "after" = $1 ]; then
      unlink $prefix.$file
    fi
  done
done

