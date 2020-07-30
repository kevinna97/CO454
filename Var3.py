# -*- coding: utf-8 -*-
"""
Created on Tue Jul 14 10:02:17 2020

@author: HZZZ
"""


import gurobipy as gp
from gurobipy import GRB
import sys


# Number of TimeSlots required for each Course

# for courses we use AFM courses in Uwaterloo
course={}
keys=range(16)
values= range(1,17)
for i in keys:
    course['C'+str(values[i])]=2
Courses, CourseRequirements = gp.multidict(course)

#Timeslot: courses start form 830 to 530 form Monday to Friday. Duration of
#class will be 80 mins
TimeSlot_day=[]
keys=range(8)
values=range(1,9)
for i in keys:
    TimeSlot_day.append('T'+ str(values[i]))
TimeSlot_week=[]
for j in range(1,6):
    for k in (range (len(TimeSlot_day))):
        TimeSlot_week.append(TimeSlot_day[k]+str(j))
TimeSlots={}
for i in TimeSlot_week:
    TimeSlots[i]=1
TimeSlots, weight=gp.multidict(TimeSlots)

#Students 
Student, Course1, Course2= gp.multidict({
    "S1":   ["C1", "C5"],
    "S2":   ["C1", "C5"],
    "S3":   ["C1", "C5"],
    "S4":   ["C1", "C5"],
    "S5":   ["C1", "C5"],
    "S6":   ["C1", "C5"],
    "S7":   ["C1", "C5"],
    "S8":   ["C1", "C7"],
    "S9":   ["C1", "C7"],
    "S10":   ["C1", "C8"],
    "S11":   ["C1", "C8"],
    "S12":   ["C1", "C8"],
    "S13":   ["C2", "C5"],
    "S14":   ["C2", "C5"],
    "S15":   ["C2", "C6"],
    "S16":   ["C2", "C6"],
    "S17a":   ["C3", "C5"],
    "S17b":   ["C5", "C8"],
    "S18":   ["C3", "C6"],
    "S19":   ["C4", "C6"],
    "S20a":   ["C4", "C5"],
    "S20b":   ["C5", "C8"],
    })

days = [1,2,3,4,5]

# Worker availability
availability = [(c1,c2,c1[2]) for c1 in TimeSlots
                for c2 in Courses]

def incs(var):
    b = var[len(var)-2]
    b = chr(ord(b)+1)
    c = b + var[len(var) - 1]
    return c

def inc(var):
    b = var[len(var)-1]
    b = chr(ord(b)+1)
    c = var[0:len(var) - 1] + b
    return c

def inc1(var):
    b = var[len(var)-1]
    b = chr(ord(b)+1)
    c = var[0:len(var) - 2] + "1" + b
    return c
def inc2(var):
    b = var[len(var)-1]
    b = chr(ord(b)+1)
    c = var[0:len(var) - 2] + "2" + b
    return c
def inc3(var):
    b = var[len(var)-1]
    b = chr(ord(b)+1)
    c = var[0:len(var) - 2] + "3" + b
    return c
def inc4(var):
    b = var[len(var)-1]
    b = chr(ord(b)+1)
    c = var[0:len(var) - 2] + "4" + b
    return c

def inc5(var):
    b = var[len(var)-1]
    b = chr(ord(b)+1)
    c = var[0:len(var) - 2] + "5" + b
    return c

def inc6(var):
    b = var[len(var)-1]
    b = chr(ord(b)+1)
    c = var[0:len(var) - 2] + "6" + b
    return c
# Model
m = gp.Model("assignment")

# Assignment variables: x[w,s] == 1 if worker w is assigned to Course s.
# Since an assignment model always produces integer solutions, we use
# continuous variables and solve as an LP.
x = m.addVars(availability, vtype=GRB.BINARY, name="x")
totClass = m.addVars(Student, name='totClass')

# The objective is to minimize the total weight costs
m.ModelSense = GRB.MINIMIZE
m.setObjectiveN(gp.quicksum(x[w, c, y] for w, c, y in availability), index=0, priority=4, abstol=2.0,
                            reltol=0.1)

# Constraints:
reqCts = m.addConstrs((x.sum('*',c,'*') == CourseRequirements[c]
                      for c in Courses), "_")
reqCts_1 = m.addConstrs((x.sum(t,'*','*') <= 1
                      for t in TimeSlots), "_")
reqCts_2 = m.addConstrs((x.sum(t,'*','*') >= 0
                      for t in TimeSlots), "_")
reqCts_3 = m.addConstrs((x.sum(t,Course1[s],'*') + x.sum(t,Course2[s],'*') <= 1
                      for t in TimeSlots
                      for s in Student))
reqCts_5 = m.addConstrs((x.sum(t,c,'*') + x.sum(inc1(t),c,'*') + x.sum(inc2(t),c,'*') + x.sum(inc3(t),c,'*') + x.sum(inc4(t),c,'*') + x.sum(inc5(t),c,'*') + x.sum(inc6(t),c,'*')<= 1
                         for c in Courses
                      for t in TimeSlots))
reqCts_6 = m.addConstrs((totClass[s] == x.sum('*',Course1[s],d) + x.sum('*',Course2[s],d)
                      for d in days
                      for s in Student))
reqCts_7 = m.addConstrs((x.sum('*',c,1) <= 1
                         for c in Courses))

m.setObjectiveN(gp.quicksum(totClass[s] for s in Student), index=1, priority=3)

# Save model
m.write('workforce1.lp')

# Optimize
m.optimize()
print(x)
status = m.status
result = [(v) for v in m.getVars()
          if v.x != 0]
if status == GRB.UNBOUNDED:
    print('The model cannot be solved because it is unbounded')
    sys.exit(0)
if status == GRB.OPTIMAL:
    print('The optimal objective is %g' % m.objVal)
    for v in m.getVars():
        i=0
        if v.x != 0 and v.varName[0] == 'x':
            print(v)
            i += 1
            
f=open('f1.txt','w')
for v in m.getVars():
    if v.x != 0 and v.varName[0] == 'x':
        n = len(v.varName)
        f.write(v.varName[2:5]+' '+v.varName[6:n-1]+'\n')
f.close()


    

Timeslot_Class=[]
i = 0
for v in m.getVars():
    if v.x!=0 and v.varName[0] == 'x':
        n = len(v.varName)
        a,b,c = v.varName[2:n-1].split(',')
        Timeslot_Class.append((a,b))

    

#Number of Classroom and each classroom can be used 2 times a day
#(SANITIZE TIME IS INCLUDED)

Rooms = []

Classroom = []

for r in range(4):
    for t in range(8):
        for d in range(7):
            rs = r + 1
            ts = t + 1
            ds = d + 1
            string1 = 'R' + str(r)
            string2 = str(ts) + str(ds)
            Classroom.append((string1,string2))

def filters(a,b):
    c = a + b
    return c

print(Classroom)
    
availability2 = [(filters(c1,c2)) for c1 in Timeslot_Class
                for c2 in Classroom
                if c1[0][1:3] == c2[1]]
print(availability2)

m2 = gp.Model("assignment")

# Assignment variables: x[w,s] == 1 if worker w is assigned to Course s.
# Since an assignment model always produces integer solutions, we use
# continuous variables and solve as an LP.
x = m2.addVars(availability2, vtype=GRB.BINARY, name="x")
totRooms = m2.addVars(availability2)
totSlack = m2.addVars(totRooms,lb=-1000, vtype=GRB.SEMIINT)

# The objective is to minimize the total weight costs
m2.ModelSense = GRB.MINIMIZE
m2.setObjectiveN(gp.quicksum(x[w, c, y, z] for w, c, y, z in availability2), index=0, priority=2, abstol=2.0,
                            reltol=0.1)
#m2.setObjectiveN(maxShift - minShift, index=1, priority=1)

# Constraints:
reqCts_n = m2.addConstrs((x.sum('*','*', c[0], c[1]) <= 1
                      for c in Classroom))
reqCts_1_n= m2.addConstrs((x.sum(t[0],t[1],'*', '*') == 1
                      for t in Timeslot_Class))
reqCts_2_n= m2.addConstrs((x.sum('*','*',c[0],incs(c[1])) + x.sum('*','*',c[0], c[1]) <= 1
                      for c in Classroom))
reqCts_4 = m2.addConstrs((x.sum(c[0],c[1],c[2],c[3]) + x.sum('*', c[1], c[2], '*') + totRooms.sum('*', c[1], c[2], '*') == 3
                                   for c in availability2))

reqCts_n = m2.addConstrs((totSlack[c] == 2*(totRooms[c]-2)
                      for c in totRooms))

m2.setObjectiveN(totSlack.sum(), index=1, priority=3)


# Using Python looping constructs, the preceding statement would be...
#
# reqCts = {}
# for s in Courses:
#   reqCts[s] = m.addConstr(
#        gp.quicksum(x[w,s] for w,s in availability.select('*', s)) ==
#        CourseRequirements[s], s)

# Save model
m2.write('workforce2.lp')

# Optimize
m2.optimize()
status = m2.status
#result = [(v) for v in m2.getVars()
 #         if v.x != 0]

                
print("herro")
for c in totRooms:
    print(totSlack[c])

for c in availability2:
    print(totRooms[c])
if status == GRB.UNBOUNDED:
    print('The model cannot be solved because it is unbounded')
    sys.exit(0)
if status == GRB.OPTIMAL:
    print('The optimal objective is %g' % m2.objVal)
    for v in Timeslot_Class:
            print(v)
    for v in m2.getVars():
        i=0
        if v.x != 0 and v.varName[0] == 'x':
            print(v)
            i += 1
    sys.exit(0)

if status != GRB.INF_OR_UNBD and status != GRB.INFEASIBLE:
    print('Optimization was stopped with status %d' % status)
    sys.exit(0)
    # do IIS
    print('The model is infeasible; computing IIS')
    m.computeIIS()
    if m.IISMinimal:
        print('IIS is minimal\n')
    else:
        print('IIS is not minimal\n')
        print('\nThe following constraint(s) cannot be satisfied:')
        for c in m.getConstrs():
            if c.IISConstr:
                print('%s' % c.constrName)

    
