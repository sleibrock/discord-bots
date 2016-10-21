Installation Guide
==================

# Matplotlib

Matplotlib secretly uses the Tcl/Tk library as a means of creating windowed graphs. 
It will burp up errors saying something along the lines of "libtk is missing" so 
make sure your system is installed with `libtk`.

# NumPy and SciPy

NumPy has no problems. It is a self-contained library.

However, SciPy uses a lot more libraries. It depends upon the `blas` package as 
well as the `lapack` package. Make sure to install those on your system before 
even trying to install SciPy.
