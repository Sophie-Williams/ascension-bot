"""
  Decodes the input files into Card objects

  Usage: cards = CardDecoder().decode_cards()
  This automatically reads all of the requisite files.
  It returns a CardDictionary (see cards.py)

  read_card_counts() is also useful for creating the initial deck.
"""

import src.input.files as files
from cards import Acquirable, Defeatable, CardDictionary
from effects import SimpleEffect, CompoundEffect

"""
  Read how many of each card belong in the deck.

  Returns a dictionary of card name to count
"""
def read_card_counts():
  return files.read_kvp_file('counts.txt', int)


decoder = None

def get_decoder():
  global decoder
  if decoder is None:
    CardDecoder()

  return decoder

def get_effects():
  global decoder
  if decoder is None:
    CardDecoder()

  return decoder.effects

def get_dict():
  global decoder
  if decoder is None:
    CardDecoder()

  return decoder.card_dict

class CardDecoder(object):
  def __init__(self):
    global decoder
    assert decoder is None
    decoder = self
    self.card_dict = self.decode_cards()

  def decode_cards(self):
    # We pad with an empty string because the effect indices are one-indexed
    self.effects = [''] + files.read_lines('effects.txt')
    return CardDictionary(self._decode_acquirables() + self._decode_defeatables())

  def _decode_acquirables(self):
    rows = files.parse_csv_file('acquirable.csv')
    return [self._row_to_acquirable(row) for row in rows]

  def _row_to_acquirable(self, row):
    name, cost, honor_str, card_type = row[:4]
    honor = int(honor_str)
    effects = self._decode_effects(row[4:])
    single = effects[0] if len(effects) == 1 else CompoundEffect('AND', effects, False)
    return Acquirable(name, cost, honor, card_type, single)

  def _decode_defeatables(self):
    rows = files.parse_csv_file('defeatable.csv')
    return [self._row_to_defeatable(row) for row in rows]

  def _row_to_defeatable(self, row):
    name, cost, card_type = row[:3]
    effects = self._decode_effects(row[3:])
    single = effects[0] if len(effects) == 1 else CompoundEffect('AND', effects, False)
    return Defeatable(name, cost, card_type, single)

  # Return (function, args, is_optional) from something of the form
  # function(args)? or function(args)
  def _decode_function(self, string):
    is_optional = string.endswith('?')

    left = string.index('(')
    right = string.rindex(')')

    if is_optional:
      assert right == len(string) - 2, (
        "optional effect string (%s) doesn't end in )?" % string)
    else:
      assert right == len(string) - 1, (
        "effect string (%s) doesn't end in )" % string)

    function = string[:left]
    args = string[left + 1:right]
    return (function, args, is_optional)

  # Can be in the form of AND(effect1, effect2) or OR(AND(e1, e2), e3)?
  def _decode_compound_effect(self, effect_str):
    if not (effect_str.startswith('AND(') or effect_str.startswith('OR(')):
      return self._decode_simple_effect(effect_str)

    # Otherwise it's a compound effect
    (compound_type, effects_str, is_optional) = self._decode_function(effect_str)
    effects = self._decode_effects(effects_str.split(';'))
    return CompoundEffect(compound_type, effects, is_optional)

  # Should be in the form index(param) where param can be '' and
  # there might be a ? at the end of the string
  def _decode_simple_effect(self, effect_str):
    (index_str, param_str, is_optional) = self._decode_function(effect_str)
    index = int(index_str)
    param = int(param_str) if param_str != '' else None

    return SimpleEffect(index, self.effects[index], param, is_optional)

  # This is used for parsing the effects at the end of a row,
  # not for parsing the strings in effects.txt
  def _decode_effects(self, effect_strs):
    return [self._decode_compound_effect(effect_str) for effect_str in effect_strs]

if __name__ == '__main__':
  print '\n'.join(str(card) for card in CardDecoder().decode_cards())

