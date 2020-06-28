# -*- coding: utf-8 -*-
"""
Created on Sun Jun 28 09:37:14 2020

@author: kevin
"""
import gurobipy as gp
from gurobipy import GRB
import sys

# Number of TimeSlots required for each Course
Courses, CourseRequirements = gp.multidict({
    "C1":  2,
    "C2":  2,
    "C3":  2,
    "C4":  2,
    "C5":  2,
    "C6":  2,
    "C7":  2,
    "C8":  2,
    "C9":  2,
    "C10": 2,
    })

# Amount each worker is paid to work one Course
TimeSlots, weight = gp.multidict({
        "T11":   1,
        "T12":   1,
        "T13":   1,
        "T14":   1,
        "T15":   1,
        "T21":   1,
        "T22":   1,
        "T23":   1,
        "T24":   1,
        "T25":   1,
        "T31":   1,
        "T32":   1,
        "T33":   1,
        "T34":   1,
        "T35":   1,
        "T41":   1,
        "T42":   1,
        "T43":   1,
        "T44":   1,
        "T45":   1,
    })

# Worker availability
availability = [(c1,c2) for c1 in TimeSlots
                for c2 in Courses]

# Model
m = gp.Model("assignment")

# Assignment variables: x[w,s] == 1 if worker w is assigned to Course s.
# Since an assignment model always produces integer solutions, we use
# continuous variables and solve as an LP.
x = m.addVars(availability, vtype=GRB.BINARY, name="x")

# The objective is to minimize the total weight costs
m.setObjective(gp.quicksum(weight[w]*x[w, c] for w, c in availability), GRB.MINIMIZE)

# Constraints:
reqCts = m.addConstrs((x.sum('*', c) == CourseRequirements[c]
                      for c in Courses), "_")
reqCts_1 = m.addConstrs((x.sum(t,'*') <= 2
                      for t in TimeSlots), "_")
reqCts_2 = m.addConstrs((x.sum(t,'*') >= 0
                      for t in TimeSlots), "_")

# Using Python looping constructs, the preceding statement would be...
#
# reqCts = {}
# for s in Courses:
#   reqCts[s] = m.addConstr(
#        gp.quicksum(x[w,s] for w,s in availability.select('*', s)) ==
#        CourseRequirements[s], s)

# Save model
m.write('workforce1.lp')

# Optimize
m.optimize()
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
        if v.x != 0:
            print(v)
            i += 1
            
f=open('f1.txt','w')
for v in m.getVars():
    if v.x != 0:
        n = len(v.varName)
        f.write(v.varName[2:5]+' '+v.varName[6:n-1]+'\n')
f.close()


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
        




