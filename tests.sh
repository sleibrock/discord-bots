#!/bin/sh

for f in bots/*.py;
do
    python -m py_compile $f
done

echo "Done"
# end
