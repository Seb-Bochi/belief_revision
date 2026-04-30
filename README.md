# Belief Revision Assignment

## How to run
pip install .
python


## The repo

This project is divided into different parts:
1. design and implementation of belief base
2. design and implementation of a method for checking logical entailment
3. implementation of contraction of belief base
4. implementation of expansion of belief base.

### 1. Belief base


### 2. Logical Entailment
To check for logical entailment, the resolution method is used. An in-depth description of it can be found at [Resolution wikipedia page](https://en.wikipedia.org/wiki/Resolution_(logic)).

In short, to check that the entailment $KB \models \varphi$, we show that $KB \land\neg  \varphi$ is unsatisfiable like this:
1. We convert $KB \land\neg  \varphi$ into CNF and extract its clauses (BeliefBase.entails).
2. We apply the resolution rule, i.e.
\[
\dfrac{\ell_1 \lor \dots \lor \ell_n, m_1 \lor \dots \lor m_k }{\ell_1 \lor \dots \lor \ell_{i-1} \lor\ell_{i+1} \lor\dots \lor \ell_n\lor }[\textsf{Full resolution}]
\]
 to the resulting set of clauses