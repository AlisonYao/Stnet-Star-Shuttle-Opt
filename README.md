# Stnet-Star-Shuttle-Opt

Code for paper: Spatio-Temporal Network for Star-shaped Shuttle Bus Scheduling Optimization

## Code

- `NYUSH_solution.py` specifies the evolution_depth and terminates as soon as it reaches the evolution_depth, no matter if a feasible solution is found or not.

- `NYUSH_solution_mutation_type.py` is the code for comparing the 2 mutation methods: conventional method vs new method (similar to `NYUSH_solution.py`).

- `NYUSH_solution_no_violation.py` automatically reruns itself when a feasible solution is unfound after a certain number of iteration. If the program ends naturally, there is a feasible solution. If not, it may loop forever (WARNING).

- `NYUSH_solution_no_violation_hpc.py` and `NYUSH_solution_no_violation_hpc.sh` are scripts for HPC. There are not many changes in these two.

- `test_results` has all the output (txt + png) classified in different folders.

## Pseudocode for solution algorithm

<pre>
1: initialize population P(i)
2: calculate operation costs and fitness scores for individuals in population P(i) (fitness score = operation cost + penalties from infeasibility)
3: while best solution is infeasible
4:     select best individuals to next generation population P(i+1) from P(i)
5:     create new individuals in P(i+1) using crossover and mutation from P(i)
6:     calculate operation costs and fitness scores for individuals in population P(i+1)
7:     i += 1
8: end while
9: return the best feasible solution during evolution
</pre>

## Notes

Repo adapted from [DURF-Bus-Schedule-Optimization](https://github.com/AlisonYao/DURF-Bus-Schedule-Optimization).
