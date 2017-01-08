#!/bin/sh

for f in src/*.py;
do
    python -m py_compile $f
done

for f in src/*.js;
do
    node -c $f
done

echo "Done"
# end
