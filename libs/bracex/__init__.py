"""
A Bash like brace expander.

Licensed under MIT
Copyright (c) 2018 - 2020 Isaac Muse <isaacmuse@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
IN THE SOFTWARE.
"""
import itertools
import math
import re
from .__meta__ import __version_info__, __version__  # noqa: F401

__all__ = ('expand', 'iexpand')

_alpha = [chr(x) if x != 0x5c else '' for x in range(ord('A'), ord('z') + 1)]
_nalpha = list(reversed(_alpha))

RE_INT_ITER = re.compile(r'(-?\d+)\.{2}(-?\d+)(?:\.{2}(-?\d+))?(?=\})')
RE_CHR_ITER = re.compile(r'([A-Za-z])\.{2}([A-Za-z])(?:\.{2}(-?\d+))?(?=\})')

DEFAULT_LIMIT = 1000


class ExpansionLimitException(Exception):
    """Brace expansion limit exception."""


def expand(string, keep_escapes=False, limit=DEFAULT_LIMIT):
    """Expand braces."""

    return list(iexpand(string, keep_escapes, limit))


def iexpand(string, keep_escapes=False, limit=DEFAULT_LIMIT):
    """Expand braces and return an iterator."""

    if isinstance(string, bytes):
        is_bytes = True
        string = string.decode('latin-1')

    else:
        is_bytes = False

    for count, entry in enumerate(ExpandBrace(keep_escapes, limit).expand(string), 1):
        yield entry.encode('latin-1') if is_bytes else entry


class StringIter(object):
    """Preprocess replace tokens."""

    def __init__(self, string):
        """Initialize."""

        self._string = string
        self._index = 0

    def __iter__(self):
        """Iterate."""

        return self

    def __next__(self):
        """Python 3 iterator compatible next."""

        return self.iternext()

    def match(self, pattern):
        """Perform regex match at index."""

        m = pattern.match(self._string, self._index)
        if m:
            self._index = m.end()
        return m

    @property
    def index(self):
        """Get current index."""

        return self._index

    def previous(self):  # pragma: no cover
        """Get previous char."""

        return self._string[self._index - 1]

    def advance(self, count):
        """Advanced the index."""

        self._index += count

    def rewind(self, count):
        """Rewind index."""

        if count > self._index:  # pragma: no cover
            raise ValueError("Can't rewind past beginning!")

        self._index -= count

    def iternext(self):
        """Iterate through characters of the string."""

        try:
            char = self._string[self._index]
            self._index += 1
        except IndexError:  # pragma: no cover
            raise StopIteration

        return char


class ExpandBrace(object):
    """Expand braces like in Bash."""

    def __init__(self, keep_escapes=False, limit=DEFAULT_LIMIT):
        """Initialize."""

        self.max_limit = limit
        self.count = 0
        self.expanding = False
        self.keep_escapes = keep_escapes

    def update_count(self, count):
        """Update the count and assert if count exceeds the max limit."""

        if isinstance(count, int):
            self.count += count
        else:
            self.count -= sum(count)
            prod = 1
            for c in count:
                prod *= c
            self.count += prod
        if self.max_limit > 0 and self.count > self.max_limit:
            raise ExpansionLimitException(
                'Brace expansion has exceeded the limit of {:d}'.format(
                    self.max_limit)
            )

    def set_expanding(self):
        """Set that we are expanding a sequence, and return whether a release is required by the caller."""

        status = not self.expanding
        if status:
            self.expanding = True
        return status

    def is_expanding(self):
        """Get status of whether we are expanding."""

        return self.expanding

    def release_expanding(self, release):
        """Release the expand status."""

        if release:
            self.expanding = False

    def get_escape(self, c, i):
        """Get an escape."""

        try:
            escaped = next(i)
        except StopIteration:
            escaped = ''
        return c + escaped if self.keep_escapes else escaped

    def squash(self, a, b):
        """
        Returns a generator that squashes two iterables into one.

        ```
        ['this', 'that'], [[' and', ' or']] => ['this and', 'this or', 'that and', 'that or']
        ```
        """

        return ((''.join(x) if isinstance(x, tuple) else x) for x in itertools.product(a, b))

    def get_literals(self, c, i, depth):
        """
        Get a string literal.

        Gather all the literal chars up to opening curly or closing brace.
        Also gather chars between braces and commas within a group (is_expanding).
        """

        result = ['']
        is_dollar = False

        count = True
        seq_count = []

        try:
            while c:
                ignore_brace = is_dollar
                is_dollar = False

                if c == '$':
                    is_dollar = True

                elif c == '\\':
                    c = [self.get_escape(c, i)]

                elif not ignore_brace and c == '{':
                    # Try and get the group
                    index = i.index
                    try:
                        if self.max_limit > 0:
                            current_count = self.count
                        seq = self.get_sequence(next(i), i, depth + 1)
                        if seq:
                            if self.max_limit > 0:
                                diff = self.count - current_count
                                seq_count.append(diff)
                            count = False
                            c = seq
                    except StopIteration:
                        # Searched to end of string
                        # and still didn't find it.
                        i.rewind(i.index - index)

                elif self.is_expanding() and c in (',', '}'):
                    # We are Expanding within a group and found a group delimiter
                    # Return what we gathered before the group delimiters.
                    i.rewind(1)
                    self.update_count(1 if count else seq_count)
                    return (x for x in result)

                # Squash the current set of literals.
                result = self.squash(result, [c] if isinstance(c, str) else c)

                c = next(i)
        except StopIteration:
            if self.is_expanding():
                return None

        self.update_count(1 if count else seq_count)
        return (x for x in result)

    def combine(self, a, b):
        """A generator that combines two iterables."""

        for l in (a, b):
            for x in l:
                yield x

    def get_sequence(self, c, i, depth):
        """
        Get the sequence.

        Get sequence between `{}`, such as: `{a,b}`, `{1..2[..inc]}`, etc.
        It will basically crawl to the end or find a valid series.
        """

        result = []
        release = self.set_expanding()
        # Used to indicate validity of group (`{1..2}` are an exception).
        has_comma = False
        # Tracks whether the current slot is empty `{slot,slot,slot}`.
        is_empty = True

        # Detect numerical and alphabetic series: `{1..2}` etc.
        i.rewind(1)
        item = self.get_range(i)
        i.advance(1)
        if item is not None:
            self.release_expanding(release)
            return (x for x in item)

        try:
            while c:
                # Bash has some special top level logic. if `}` follows `{` but hasn't matched
                # a group yet, keep going except when the first 2 bytes are `{}` which gets
                # completely ignored.
                # and i.index not in self.skip_index
                keep_looking = depth == 1 and not has_comma
                if (c == '}' and (not keep_looking or i.index == 2)):
                    # If there is no comma, we know the sequence is bogus.
                    if is_empty:
                        result = (x for x in self.combine(result, ['']))
                    if not has_comma:
                        result = ('{' + literal + '}' for literal in result)
                    self.release_expanding(release)
                    return (x for x in result)

                elif c == ',':
                    # Must be the first element in the list.
                    has_comma = True
                    if is_empty:
                        result = (x for x in self.combine(result, ['']))
                    else:
                        is_empty = True

                else:
                    if c == '}':
                        # Top level: If we didn't find a comma, we haven't
                        # completed the top level group. Request more and
                        # append to what we already have for the first slot.
                        if not result:
                            result = (x for x in self.combine(result, [c]))
                        else:
                            result = self.squash(result, [c])
                        value = self.get_literals(next(i), i, depth)
                        if value is not None:
                            result = self.squash(result, value)
                            is_empty = False
                    else:
                        # Lower level: Try to find group, but give up if cannot acquire.
                        value = self.get_literals(c, i, depth)
                        if value is not None:
                            result = (x for x in self.combine(result, value))
                            is_empty = False

                c = next(i)
        except StopIteration:
            self.release_expanding(release)
            raise

    def get_range(self, i):
        """
        Check and retrieve range if value is a valid range.

        Here we are looking to see if the value is series or range.
        We look for `{1..2[..inc]}` or `{a..z[..inc]}` (negative numbers are fine).
        """

        try:
            m = i.match(RE_INT_ITER)
            if m:
                return self.get_int_range(*m.groups())

            m = i.match(RE_CHR_ITER)
            if m:
                return self.get_char_range(*m.groups())
        except ExpansionLimitException:
            raise
        except Exception:  # pragma: no cover
            # TODO: We really should never fail here,
            # but if we do, assume the sequence range
            # was invalid. This catch can probably
            # be removed in the future with more testing.
            pass

        return None

    def format_value(self, value, padding):
        """Get padding adjusting for negative values."""

        if padding:
            return "{:0{pad}d}".format(value, pad=padding)

        else:
            return str(value)

    def get_int_range(self, start, end, increment=None):
        """Get an integer range between start and end and increments of increment."""

        first, last = int(start), int(end)
        increment = int(increment) if increment is not None else 1
        max_length = max(len(start), len(end))

        # Zero doesn't make sense as an incrementer
        # but like bash, just assume one
        if increment == 0:
            increment = 1

        if start[0] == '-':
            start = start[1:]

        if end[0] == '-':
            end = end[1:]

        if (len(start) > 1 and start[0] == '0') or (len(end) > 1 and end[0] == '0'):
            padding = max_length

        else:
            padding = 0

        if first < last:
            self.update_count(math.ceil(abs(((last + 1) - first) / increment)))
            r = range(first, last + 1, -
                      increment if increment < 0 else increment)
        else:
            self.update_count(math.ceil(abs(((first + 1) - last) / increment)))
            r = range(first, last - 1, increment if increment <
                      0 else -increment)

        return (self.format_value(value, padding) for value in r)

    def get_char_range(self, start, end, increment=None):
        """Get a range of alphabetic characters."""

        increment = int(increment) if increment else 1
        if increment < 0:
            increment = -increment

        # Zero doesn't make sense as an incrementer
        # but like bash, just assume one
        if increment == 0:
            increment = 1

        inverse = start > end
        alpha = _nalpha if inverse else _alpha

        start = alpha.index(start)
        end = alpha.index(end)

        if start < end:
            self.update_count(math.ceil(((end + 1) - start) / increment))
            return (c for c in alpha[start:end + 1:increment])

        else:
            self.update_count(math.ceil(((start + 1) - end) / increment))
            return (c for c in alpha[end:start + 1:increment])

    def expand(self, string):
        """Expand."""

        self.expanding = False
        empties = []
        found_literal = False
        if string:
            i = iter(StringIter(string))
            value = self.get_literals(next(i), i, 0)
            if value is not None:
                for x in value:
                    # We don't want to return trailing empty strings.
                    # Store empty strings and output only when followed by a literal.
                    if not x:
                        empties.append(x)
                        continue
                    found_literal = True
                    while empties:
                        yield empties.pop(0)
                    yield x
        empties = []

        # We found no literals so return an empty string
        if not found_literal:
            yield ""
