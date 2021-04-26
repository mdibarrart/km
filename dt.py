# -*- coding: utf-8 -*-

import math

class DataFrame :

    def __init__(self, data) :
        self.data = self.data_check(data)

    def data_check(self,data) :
        if type(data) != dict :
            raise TypeError("Data input must be on dictionary form.")
        for name in data.keys() :
            if " " in name :
                raise ValueError("Variable names don't admit spaces.")
            if type(data[name]) != list :
                raise TypeError("For variable {}, values must be on list form.".format(name))
            try :
                if len(data[name]) != l :
                    raise ValueError("Variables must be of the same length")
            except NameError :
                l = len(data[name])
            v = [i for i in data[name] if i != None]
            if v == [] :
                pass
            elif type(v[0]) not in [float, int, complex, bool, str] :
                raise TypeError("Value type in variable {} not valid.".format(name))
            for i in range(len(v)-1) :
                try :
                    [type(float(v[i])), type(float(v[i+1]))] == [float, float]
                except ValueError :
                    if [type(v[i]), type(v[i+1])] != [str, str] :
                        raise TypeError("Observations of variable {} must be of the same type.".format(name))
        for name in data.keys() :
            for i in range(len(data[name])) :
                if type(data[name][i]) != str and data[name][i] != None :
                    data[name][i] = float(data[name][i])
            setattr(self, name, Variable(data[name], name))
        return data

    def preserve(self) :
        preserved = {}
        for name in self.data.keys() :
            preserved[name] = tuple(self.data[name])
        return preserved

    def restore(self,preserved) :
        restored = {}
        for index in self.data.keys() :
            restored[index] = list(preserved[index])
        return restored
    
    def filt_check(self,filt) :
        if type(filt) != list and type(filt) != Variable :
            raise TypeError("Filt input must be on list form.")
        elif len(filt) != len(self) :
            raise ValueError("Filt length must coincide with number of observations.")
        else :
            for index in range(len(filt)) :
                if type(filt[index]) != bool :
                    raise TypeError("Filt elements must be all booleans.")

    def __repr__(self) :
        return "DataFrame: "+str(self.data)

    def __str__(self) :
        just = 0
        for name in self.data.keys() :
            for i in range(len(self)) :
                just = max(just, len(repr(self.data[name][i])))
        string = "Data Frame\n\nObservations : {} (displaying : {})\nVariables : {}\n\n"
        for name in self.data.keys() :
            string = string + name+"  :".ljust(just+1)
            for i in range(min([10, len(self)])) :
                string = string+"{}".format(repr(self.data[name][i]).ljust(just+1))
            string = string+"\n\n"
        return string.format(len(self), min([10, len(self)]), len(self.data.keys()))

    def __len__(self) :
        for name in self.data.keys() :
            obs = len(self.data[name])
            break
        return obs

    def __getitem__(self, index) :
        if index not in range(len(self)) :
            raise IndexError("Data index out of range")
        item = []
        for name in self.data.keys() :
            item.append(self.data[name][index])
        return item

    def __setitem__(self, index, value) :
        p = self.preserve()
        if type(value) != list :
            raise TypeError("Item assignment must be on list form.")
        if index == len(self) :
            for name in self.data.keys() :
                try :
                    self.data[name].append(value.pop(0))
                except IndexError :
                    break
        elif index in range(len(self)) :
            for name in self.data.keys() :
                try :
                    self.data[name][index] = value.pop(0)
                except IndexError :
                    break
        else :
            raise IndexError("Data index out of range.")
        try :
            self.data = self.data_check(self.data)
        except :
            self.data = self.restore(p)
            raise
            
    def __delitem__(self,index) :
        if index not in range(len(self)) :
            raise IndexError("Data index out of range.")
        for name in self.data.keys() :
            self.data[name].pop(index)
        self.data = self.data_check(self.data)

    def add(self, *newdata) :
        p = self.preserve()
        try :
            for index in range(len(newdata)) :
                self[len(self)] = newdata[index]
        except :
            self.data = self.restore(p)
            raise

    def keep(self,filt) :
        self.filt_check(filt)
        i = 0
        for index in range(len(self)) :
            if filt[index] == False :
                del self[index-i]
                i = i+1

    def var(self, name, newdata, filt = None) :
        p = self.preserve()
        if filt == None :
            filt = [True]*len(self)
        if type(newdata) in [float, int, bool, complex, str] :
            newdata = [newdata]*len(self)
        self.filt_check(filt)
        if type(name) != str :
            raise TypeError("Variable name must be string type.")
        if name not in self.data.keys() :
            self.data[name] = [None]*len(self)
        for index in range(len(self)) :
            if filt[index] == True :
                self.data[name][index] = newdata[index]
        try :
            self.data = self.data_check(self.data)
        except :
            self.data = self.restore(p)
            raise

    def del_var(self, name) :
        if type(name) != str :
            raise TypeError("Variable name must be string type.")
        if name not in self.data.keys() :
            raise NameError("Variable doesn't exists.")
        self.data.pop(name)
        delattr(self,name)

    def rename(self, oldname, newname) :
        p = self.preserve()
        if oldname not in self.data.keys() :
            raise ValueError("Variable {} doesn't exists.".format(oldname))
        newdata = {}
        for name in self.data.keys() :
            if name == oldname :
                newdata[newname] = self.data[name]
            else :
                newdata[name] = self.data[name]
        try :
            self.data = self.data_check(newdata)
            delattr(self,oldname)
        except :
            self.data = self.restore(p)
            raise

    def to_float(self, name) :
        p = self.preserve()
        if type(name) != str :
            raise TypeError("Variable name must be string type.")
        if name not in self.data.keys() :
            raise NameError("Variable doesn't exists.")
        try :
            for index in range(len(self)) :
                if self.data[name][index] != None :
                    self.data[name][index] = float(self.data[name][index])
            self.data = self.data_check(self.data)
        except ValueError :
            self.data = self.restore(p)
            raise ValueError("Variable {} can't be converted to float.".format(name))

    def to_string(self, name, integer = True) :
        p = self.preserve()
        if type(name) != str :
            raise TypeError("Variable name must be string type.")
        if name not in self.data.keys() :
            raise NameError("Variable doesn't exists.")
        try :
            for index in range(len(self)) :
                if self.data[name][index] != None :
                    if integer == True :
                        self.data[name][index] = str(int(self.data[name][index]))
                    else :
                        self.data[name][index] = str(self.data[name][index])
            self.data = self.data_check(self.data)
        except :
            self.data = self.data_check(p)

class Variable :

    def __init__(self, data, name = None) :
        self.data = []
        for i in range(len(data)) :
            self.data.append(data[i])
        if name != None :
            if type(name) != str :
                raise TypeError("Variable name must be string.")
            else :
                self.name = name

    def __repr__(self) :
        return str(self.data)

    def __getitem__(self,index) :
        return self.data[index]
    
    def __setitem__(self,index,value) :
        self.data[index] = value

    def __len__(self) :
        return len(self.data)

    def __eq__(self, other) :
        result = []
        if type(other) in [float, int, bool, complex, str] or type(other) == type(None) :
            other = [other]*len(self)
        for i in range(len(self)) :
            result.append(self[i]==other[i])
        return Variable(result)

    def __ne__(self, other) :
        result = []
        if type(other) in [float, int, bool, complex, str] or type(other) == type(None) :
            other = [other]*len(self)
        for i in range(len(self)) :
            result.append(self[i]!=other[i])
        return Variable(result)

    def __lt__(self, other) :
        result = []
        if type(other) in [float, int, bool, complex, str] or type(other) == type(None) :
            other = [other]*len(self)
        for i in range(len(self)) :
            if self[i] != None and other[i] != None :
                result.append(self[i]<other[i])
            else :
                result.append(False)
        return Variable(result)

    def __gt__(self, other) :
        result = []
        if type(other) in [float, int, bool, complex, str] or type(other) == type(None) :
            other = [other]*len(self)
        for i in range(len(self)) :
            if self[i] != None and other[i] != None :
                result.append(self[i]>other[i])
            else :
                result.append(False)
        return Variable(result)

    def __le__(self, other) :
        result = []
        if type(other) in [float, int, bool, complex, str] or type(other) == type(None) :
            other = [other]*len(self)
        for i in range(len(self)) :
            if self[i] != None and other[i] != None :
                result.append(self[i]<=other[i])
            else :
                result.append(False)
        return Variable(result)

    def __ge__(self, other) :
        result = []
        if type(other) in [float, int, bool, complex, str] or type(other) == type(None) :
            other = [other]*len(self)
        for i in range(len(self)) :
            if self[i] != None and other[i] != None :
                result.append(self[i]>=other[i])
            else :
                result.append(False)
        return Variable(result)

    def __pos__(self) :
        result = []
        for i in range(len(self)) :
            if self[i] != None :
                result.append(+self[i])
            else :
                result.append(None)
        return Variable(result)

    def __neg__(self) :
        result = []
        for i in range(len(self)) :
            if self[i] != None :
                result.append(+self[i])
            else :
                result.append(None)
        return Variable(result)

    def __abs__(self) :
        result = []
        for i in range(len(self)) :
            if self[i] != None :
                result.append(abs(self[i]))
            else :
                result.append(None)
        return Variable(result)

    def __invert__(self) :
        result = []
        for i in range(len(self)) :
            if self[i] != None :
                result.append(~self[i])
            else :
                result.append(None)
        return Variable(result)

    def __round__(self) :
        result = []
        for i in range(len(self)) :
            if self[i] != None :
                result.append(round(self[i]))
            else :
                result.append(None)
        return Variable(result)

    def __floor__(self) :
        result = []
        for i in range(len(self)) :
            if self[i] != None :
                result.append(math.floor(self[i]))
            else :
                result.append(None)
        return Variable(result)

    def __ceil__(self) :
        result = []
        for i in range(len(self)) :
            if self[i] != None :
                result.append(math.ceil(self[i]))
            else :
                result.append(None)
        return Variable(result)

    def __trunc__(self) :
        result = []
        for i in range(len(self)) :
            if self[i] != None :
                result.append(math.trunc(self[i]))
            else :
                result.append(None)
        return Variable(result)

    def __add__(self, other) :
        result = []
        if type(other) in [float, int, bool, complex, str] or type(other) == type(None) :
            other = [other]*len(self)
        for i in range(len(self)) :
            if self[i] != None and other[i] != None :
                result.append(self[i]+other[i])
            else :
                result.append(None)
        return Variable(result)

    def __sub__(self, other) :
        result = []
        if type(other) in [float, int, bool, complex, str] or type(other) == type(None) :
            other = [other]*len(self)
        for i in range(len(self)) :
            if self[i] != None and other[i] != None :
                result.append(self[i]-other[i])
            else :
                result.append(None)
        return Variable(result)

    def __mul__(self, other) :
        result = []
        if type(other) in [float, int, bool, complex, str] or type(other) == type(None) :
            other = [other]*len(self)
        for i in range(len(self)) :
            if self[i] != None and other[i] != None :
                result.append(self[i]*other[i])
            else :
                result.append(None)
        return Variable(result)

    def __floordiv__(self, other) :
        result = []
        if type(other) in [float, int, bool, complex, str] or type(other) == type(None) :
            other = [other]*len(self)
        for i in range(len(self)) :
            if self[i] != None and other[i] != None :
                result.append(self[i]//other[i])
            else :
                result.append(None)
        return Variable(result)

    def __div__(self, other) :
        result = []
        if type(other) in [float, int, bool, complex, str] or type(other) == type(None) :
            other = [other]*len(self)
        for i in range(len(self)) :
            if self[i] != None and other[i] != None :
                result.append(self[i]/other[i])
            else :
                result.append(None)
        return Variable(result)

    def __mod__(self, other) :
        result = []
        if type(other) in [float, int, bool, complex, str] or type(other) == type(None) :
            other = [other]*len(self)
        for i in range(len(self)) :
            if self[i] != None and other[i] != None :
                result.append(self[i]%other[i])
            else :
                result.append(None)
        return Variable(result)

    def __pow__(self, other) :
        result = []
        if type(other) in [float, int, bool, complex, str] or type(other) == type(None) :
            other = [other]*len(self)
        for i in range(len(self)) :
            if self[i] != None and other[i] != None :
                result.append(self[i]**other[i])
            else :
                result.append(None)
        return Variable(result)

    def __lshift__(self, other) :
        result = []
        if type(other) in [float, int, bool, complex, str] or type(other) == type(None) :
            other = [other]*len(self)
        for i in range(len(self)) :
            if self[i] != None and other[i] != None :
                result.append(self[i]<<other[i])
            else :
                result.append(None)
        return Variable(result)

    def __rshift__(self, other) :
        result = []
        if type(other) in [float, int, bool, complex, str] or type(other) == type(None) :
            other = [other]*len(self)
        for i in range(len(self)) :
            if self[i] != None and other[i] != None :
                result.append(self[i]>>other[i])
            else :
                result.append(None)
        return Variable(result)

    def __and__(self, other) :
        result = []
        if type(other) in [float, int, bool, complex, str] or type(other) == type(None) :
            other = [other]*len(self)
        for i in range(len(self)) :
            if self[i] != None and other[i] != None :
                result.append(self[i]&other[i])
            else :
                result.append(False)
        return Variable(result)

    def __or__(self, other) :
        result = []
        if type(other) in [float, int, bool, complex, str] or type(other) == type(None) :
            other = [other]*len(self)
        for i in range(len(self)) :
            if self[i] != None and other[i] != None :
                result.append(self[i]|other[i])
            else :
                result.append(False)
        return Variable(result)

    def __xor__(self, other) :
        result = []
        if type(other) in [float, int, bool, complex, str] or type(other) == type(None) :
            other = [other]*len(self)
        for i in range(len(self)) :
            if self[i] != None and other[i] != None :
                result.append(self[i]^other[i])
            else :
                result.append(False)
        return Variable(result)
    
    def ind(self, base = None) :
        v = [i for i in self.data if i != None]
        v = v[0]
        values = list(set(self.data)-{None})
        if len(values) < 2 :
            raise ValueError("Not enough different values in the variable {} to create indicators.".format(self.name))
        if base != None:
            if base not in values :
                raise ValueError("Indicated base not valid.")
            else :
                values.remove(base)
        else :
            values.remove(v)
        result = []
        result.append(Variable(self.filt()))
        for val in values :
            result.append(Variable(self == val,"{}_{}".format(repr(self.name),repr(val).strip())))
        for index in range(1,len(values)+1):
            for n in range(len(self)) :
                result[index].data[n] = float(result[index].data[n])
        return result

    def filt(self) :
        return self != None

    def pop(self, index) :
        pop = self.data[index]
        self.data.pop(index)
        return pop
    
def from_csv(file, firstrow = True, sep = ";") :
    aux = []
    with open(file, "r", encoding='utf-8-sig') as data :
        for line in data :
            aux.append(line.split(sep))
    data = {}
    if firstrow == True:
        for n in range(len(aux[0])) :
            if n+1 == len(aux[0]) :
                data[aux[0][n][:-1].replace(" ","")] = []
            else :
                data[aux[0][n].replace(" ","")] = []
        aux.pop(0)
    else :
        for n in range(len(aux[0])) :
            data["var"+str(n+1)] = []
    n=0
    for name in data.keys() :
        for index in range(len(aux)) :
            if n+1 == len(aux[0]) :
                data[name].append(aux[index][n][:-1])
            else :
                data[name].append(aux[index][n])
        n = n+1
    for name in data.keys() :
        values = [i for i in data[name] if i != ""]
        try :
            for index in range(len(values)) :
                float(values[index])
            for index in range(len(data[name])) :
                if data[name][index] == "" :
                    data[name][index] = None
                else :
                    data[name][index] = float(data[name][index])
        except ValueError :
            for index in range(len(data[name])) :
                if data[name][index] == "" :
                    data[name][index] = None
    return DataFrame(data)
