# -*- coding: utf-8 -*-

import dt
import km

def to_latex(regs, indep_labs = None, dep_labs = None, col_lab = None) :
    if type(regs) != list :
        raise TypeError("List of regressions must be in list form.")
    elif :
        for r in regs :
            if type(r) != km.Reg :
                raise TypeError("Regresions must be of Reg type.")
    col = len(regs)
    pass