import gurobipy as grb
from gurobipy import GRB
import numpy as np


def master_problem(column, vtype):
    m = grb.Model()
    x = m.addMVar(shape=column.shape[1], lb=0, vtype=vtype)
    m.addConstr(lhs=column @ x >= demand_number_array)
    m.setObjective(x.sum(), GRB.MINIMIZE)
    m.optimize()

    if vtype == GRB.CONTINUOUS:
        return np.array(m.getAttr('Pi', m.getConstrs()))
    else:
        return m.objVal, np.array(m.getAttr('X'))


def restricted_lp_master_problem(column):
    return master_problem(column, GRB.CONTINUOUS)


def restricted_ip_master_problem(column):
    return master_problem(column, GRB.INTEGER)


def knapsack_subproblem(kk):
    m = grb.Model()
    x = m.addMVar(shape=kk.shape[0], lb=0, vtype=GRB.INTEGER)
    m.addConstr(lhs=demand_width_array @ x <= roll_width)
    m.setObjective(1 - kk @ x, GRB.MINIMIZE)
    m.optimize()

    flag_new_column = m.objVal < 0
    if flag_new_column:
        new_column = m.getAttr('X')
    else:
        new_column = None
    return flag_new_column, new_column


roll_width = np.array(17)
demand_width_array = np.array([3, 6, 7,8])
demand_number_array = np.array([25, 20, 18,10])
initial_cut_pattern = np.diag(np.floor(roll_width / demand_width_array))


flag_new_cut_pattern = True
new_cut_pattern = None
cut_pattern = initial_cut_pattern
while flag_new_cut_pattern:
    if new_cut_pattern:
        cut_pattern = np.column_stack((cut_pattern, new_cut_pattern))
    kk = restricted_lp_master_problem(cut_pattern)
    flag_new_cut_pattern, new_cut_pattern = knapsack_subproblem(kk)

minimal_stock, optimal_number = restricted_ip_master_problem(cut_pattern)

print('************************************************')
print('parameter:')
print(f'roll_width: {roll_width}')
print(f'demand_width_array: {demand_width_array}')
print(f'demand_number_array: {demand_number_array}')
print('result:')
print(f'minimal_stock: {minimal_stock}')
print(f'cut_pattern: {cut_pattern}')
print(f'optimal_number: {optimal_number}')