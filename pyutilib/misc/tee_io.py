#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________

import sys
import six


class TeeStream(object):
    """This class implements a simple output stream 'Tee'.

    This class presents a standard FILE interface.  Methods called on
    this object are passed verbatim to each of the underlying streams
    passed to the constructor.  Since this presents a full file
    interface, TeeStream objects may be arbitrarily nested.

    """

    def __init__(self, *streams):
        if not streams:
            raise ValueError("TeeStream not passed at least one output stream")
        self.streams = stream

    def write(self, data):
        for stream in self.streams:
            stream.write(data)

    def writelines(self, sequence):
        for x in sequence:
            self.write(x)

    def flush(self):
        for stream in self.streams:
            try:
                stream.flush()
            except:
                pass

    def close(self):
        for stream in self.streams:
            stream.close()

    # TODO: determine if we should implement tell, seek, read, and readline


class ConsoleBuffer(object):
    """This class implements a simple 'Tee' of the python stdout and
    stderr so the output can be captured and reported programmatically.
    We need a specialized class here because other applications /
    methods explicitly write to sys.stderr and sys.stdout, so it is
    insufficient to 'wrap' the streams like the TeeStream class;
    instead, we must replace the standard stdout and stderr objects with
    our own duplicator."""

    def __init__(self):
        self._dup_out = self._dup_err = None
        self._raw_out = sys.stdout
        self._raw_err = sys.stderr
        self.reset()

    def __del__(self):
        if self._dup_out is not None and self._dup_out is not sys.stdout:
            raise RuntimeError("ConsoleBuffer: Nesting violation " \
                  "(attempting to delete the buffer while stdout is " \
                  "redirected away from this buffer).")
        if self._dup_err is not None and self._dup_err is not sys.stderr:
            raise RuntimeError("ConsoleBuffer: Nesting violation " \
                  "(attempting to delete the buffer while stderr is " \
                  "redirected away from this buffer).")
        sys.stdout = self._raw_out
        sys.stderr = self._raw_err

    def reset(self):
        if self._dup_out is not None and self._dup_out is not sys.stdout:
            raise RuntimeError("ConsoleBuffer: Nesting violation " \
                  "(attempting to reset() when stdout has been redirected " \
                  "away from this buffer).")
        if self._dup_err is not None and self._dup_err is not sys.stderr:
            raise RuntimeError("ConsoleBuffer: Nesting violation " \
                  "(attempting to reset() when stderr has been redirected " \
                  "away from this buffer).")

        self.out = six.StringIO()
        self.err = six.StringIO()
        self._dup_out = sys.stdout = TeeStream(self.out, self._raw_out)
        self._dup_err = sys.stderr = TeeStream(self.err, self._raw_err)
