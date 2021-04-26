# -*- coding: utf-8 -*-

import dt
import numpy
import statistics
from scipy.stats import t
from scipy.stats import f

class Reg() :
    def __init__(self, depvar, indepvars, cons = True, filt = None) :
        self.X = []
        self.Xnames = []
        self.Y = tuple(depvar.data)
        self.Yname = depvar.name
        if cons == True :
            self.X.append(tuple([1]*len(depvar)))
            self.Xnames.append("constant")
            self.cons = True
        else :
            self.cons = False
        if filt == None :
            filt = dt.Variable([True]*len(depvar))
        if type(filt) != dt.Variable :
            raise TypeError("Filt input must be on list form.")
        elif len(filt) != len(depvar) :
            raise ValueError("Filt length must coincide with number of observations.")
        else :
            for index in range(len(filt)) :
                if type(filt[index]) != bool :
                    raise TypeError("Filt elements must be all booleans.")
        v = [i for i in depvar if i != None]
        if v == [] :
            raise ValueError("No observations")
        elif type(v[0]) == str :
            raise TypeError("String variables not allowed.")
        for var in indepvars :
            if type(var) == list :
                for ind in var :
                    v = [i for i in ind if i != None]
                    if v == [] :
                        raise ValueError("No observations")
                    elif type(v[0]) == str :
                        raise TypeError("String variables not allowed.")
            elif type(var) == dt.Variable:
                v = [i for i in var if i != None]
                if v == [] :
                    raise ValueError("No observations")
                elif type(v[0]) == str :
                    raise TypeError("String variables not allowed.")
        filt = filt&depvar.filt()
        for var in indepvars :
            if type(var) == list :
                filt = filt&var[0]
                for ind in range(1, len(var)) :
                    self.X.append(tuple(var[ind].data))
                    self.Xnames.append(var[ind].name)
            if type(var) == dt.Variable :
                filt = filt&var.filt()
                self.X.append(tuple(var.data))
                self.Xnames.append(var.name)
        n = 0
        for i in range(len(depvar)) :
            if filt[i] == False :
                for k in range(len(self.X)) :
                    self.X[k] = self.X[k][:i-n] + self.X[k][i-n+1:]
                self.Y = self.Y[:i-n] + self.Y[i-n+1:]
                n = n+1
        self.X = numpy.array(self.X).T
        self.Y = numpy.array(self.Y).T
        self.filt = filt
    
    @property
    def N(self) :
        return len(self.Y)
    
    @property
    def K(self) :
        return len(self.Xnames)
    
    @property
    def mco_n(self) :
        return numpy.dot(numpy.dot(numpy.linalg.inv(numpy.dot(self.X.T,self.X)),self.X.T),self.Y)
    
    @property
    def mco(self) :
        mco = {}
        for k in range(self.K) :
            mco[self.Xnames[k]] = self.mco_n[k]
        return mco

    @property
    def predict(self) :
        return numpy.dot(self.X, self.mco_n)

    @property
    def resid(self) :
        return numpy.subtract(self.Y,self.predict)

    @property    
    def var(self) :
        e2 = []
        for i in range(self.N) :
            e2.append(self.resid[i]**2)
        return sum(e2)/(self.N-self.K)
            
    @property
    def r2(self) :
        sst = []
        for i in range(self.N) :
            sst.append((self.Y[i]-statistics.mean(self.Y))**2)
        return 1-((self.N-self.K)*self.var)/sum(sst)
    
    @property
    def ar2(self) :
        return 1-(1-self.r2)*(self.N-1)/(self.N-self.K)
    
    @property
    def bvar(self) :
        return numpy.linalg.inv(numpy.dot(self.X.T,self.X))*self.var
    
    @property
    def se_n(self) :
        return numpy.diag(numpy.sqrt(self.bvar))
            
    @property
    def se(self) :
        se ={}
        for i in range(self.K) :
            se[self.Xnames[i]] = self.se_n[i]
        return se

    @property
    def t_n(self) :
        return numpy.divide(self.mco_n, self.se_n)
    
    @property
    def t(self) :
        t ={}
        for i in range(self.K) :
            t[self.Xnames[i]] = self.t_n[i]
        return t
    
    @property
    def p_n(self) :
        p =[]
        for i in range(self.K) :
            p.append(2*(1-t.cdf(abs(self.t_n[i]),self.N-self.K)))
        return numpy.array(p)
    
    @property
    def p(self) :
        p ={}
        for i in range(self.K) :
            p[self.Xnames[i]] = self.p_n[i]
        return p
    
    @property
    def ci_l_n(self, c = 0.95) :
        return numpy.subtract(self.mco_n, t.ppf(1-(1-c)/2, self.N-self.K)*self.se_n)

    @property
    def ci_u_n(self, c = 0.95) :
        return numpy.add(self.mco_n, t.ppf(1-(1-c)/2, self.N-self.K)*self.se_n)
    
    @property
    def ci(self, c = 0.95) :
        ci = {}
        for i in range(self.K) :
            ci[self.Xnames[i]] = [self.ci_l_n[i], self.ci_u_n[i]]
        return ci
    
    @property
    def f(self) :
        return ((self.r2)/(self.K-1))/((1-self.r2)/(self.N-self.K))
    
    @property
    def fp(self) :
        if self.cons == True :
            p = 1-f.cdf(self.f, self.K-1, self.N-self.K)
        else :
            p = 1-f.cdf(self.f, self.K, self.N-self.K)
        return p
    
    def wald_test(self, q, *R) :
        J = len(R)
        if type(q) != list :
            raise TypeError("Constants must be in list form.")
        elif len(q) != J :
            raise ValueError("Number of constants and number of restrictions must be the same.")
        else :
            for r in R :
                if type(r) != list :
                    raise TypeError("Restrictions must be in list form.")
                elif len(r) != self.K :
                    raise ValueError("Restriction length must be the same as the number of variables.")
        R = numpy.array(R)
        q = numpy.array(q).T
        Rb = numpy.dot(R,self.mco_n)
        RXXR = numpy.linalg.inv(numpy.dot(numpy.dot(R,numpy.linalg.inv(numpy.dot(self.X.T,self.X))),R.T))
        F = numpy.dot(numpy.dot(numpy.subtract(Rb,q).T,RXXR),numpy.subtract(Rb,q))/(J*self.var)
        p = 1 - f.cdf(F, J, self.N - self.K)
        return [F, p]
