
# parsetab.py
# This file is automatically generated. Do not edit.
# pylint: disable=W,C,R
_tabversion = '3.10'

_lr_method = 'LALR'

_lr_signature = 'leftMASMAS NUMERO\n    expresion : expresion MAS expresion\n    expresion : NUMERO'
    
_lr_action_items = {'NUMERO':([0,3,],[2,2,]),'$end':([1,2,4,],[0,-2,-1,]),'MAS':([1,2,4,],[3,-2,-1,]),}

_lr_action = {}
for _k, _v in _lr_action_items.items():
   for _x,_y in zip(_v[0],_v[1]):
      if not _x in _lr_action:  _lr_action[_x] = {}
      _lr_action[_x][_k] = _y
del _lr_action_items

_lr_goto_items = {'expresion':([0,3,],[1,4,]),}

_lr_goto = {}
for _k, _v in _lr_goto_items.items():
   for _x, _y in zip(_v[0], _v[1]):
       if not _x in _lr_goto: _lr_goto[_x] = {}
       _lr_goto[_x][_k] = _y
del _lr_goto_items
_lr_productions = [
  ("S' -> expresion","S'",1,None,None,None),
  ('expresion -> expresion MAS expresion','expresion',3,'p_expresion','ply_test.py',51),
  ('expresion -> NUMERO','expresion',1,'p_expresion_numero','ply_test.py',58),
]
