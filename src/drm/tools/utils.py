#!/usr/bin/python3

import argparse

class EnumType(object):
    """Factory for creating enum object types
    """
    def __init__(self, enumclass, action):
        self.enums = enumclass
        self.action = action

    def __call__(self, astring):
        name = self.enums.__name__
        try:
            v = self.enums[astring.upper()]
        except KeyError:
            msg = ', '.join([t.name.lower() for t in self.enums])
            msg = 'use one of: %s' % msg
            raise argparse.ArgumentTypeError(msg)
        else:
            self.action.choices = None  # hugly hack to prevent post validation from choices
            return v

    def __repr__(self):
        astr = ', '.join([t.name.lower() for t in self.enums])
        return '%s(%s)' % (self.enums.__name__, astr)

class StoreEnumAction(argparse._StoreAction):
  def __init__(self, option_strings, dest, type, nargs = None, const = None, default = None,
               required = False, help = None, metavar = None):
      super().__init__(option_strings = option_strings, dest = dest, nargs = nargs,
                       const = const, default = default, type = EnumType(type, self),
                       choices = tuple(str(t) for t in type), required = required,
                       help = 'one of: %s' % ', '.join(str(t) for t in type),
                       metavar = metavar)
