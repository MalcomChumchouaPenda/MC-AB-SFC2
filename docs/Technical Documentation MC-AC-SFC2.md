

# Technical Documentation

*MC-AB-SFC2: A MASQ-Based Replication of a Multi-Country Agent-Based Stock-Flow Consistent Model*

## Table of Contents



## 1. Introduction


### 1.1 Purpose of the Technical Documentation


### 1.2 Relationship with ODD Documentation


## 2. Engineering Approach

### 2.1. MASQ Metamodel

The design of the computational model is based on an adaptation of the **MASQ** approach.
We have chosen the `agentpy` platform for the implementation of this model.



### 2.2. Test-Driven Development


## 3. Model implementation

### 3.1. Core Abstractions

#### 3.1.1. Abstract Entities

The modelled economy consists of 4 entities:

* **agents** who make economic decisions
* **spaces** in which agents interact
* real or monetary **stocks** resulting from these interactions
* **roles** through which agents interact within these spaces

![model](diagrams\base_model.drawio.svg)


This core abstractions are implemented in the classes of the `code/model/base.py`:

| Classe         | Entity       | Responsabilité                                           |
| -------------- | ------------ | -------------------------------------------------------- |
| `EcoAgent`     | Agent        | process of decision of economic agents                   |
| `EcoRole`      | Role         | spatial behaviour (perceptions + actions) of agents      |
| `EcoStocks`    | Stock        | representation of real or monetary stocks and flows      |
| `EcoSpace`     | Space        | management of interaction mechanisms between agents      |


#### 3.1.2. General Dynamics
The dynamics of the economy consist of a sequence of events.
Each event gives rise to a life cycle comprising four phases:
1. activation of **decision functions** (*agent methods*)
2. activation of **reaction laws** (*role methods*)
3. activation of **interference laws** (*space methods*)
4. activation of local **evolution laws** (*space methods*)

Three types of dynamics can be then distinguished:
* sequential actions (sequential actions and immediate responses)
* simultaneous actions (parallel actions and delayed responses)
* local evolutions (environmental dynamics in the absence of agent actions)


For **sequential actions and responses**, each time agent call for actions, the role react by activating interference laws.

![dyn-sequential-actions](diagrams\dynamic_sequential_actions.drawio.svg)



For **simultaneous actions and responses**, each agent activated call role actions which not activate reaction laws but only change role state. After all agents decision, the space interference laws are activated to make responses.


![dyn-parallel-actions](diagrams\dynamic_parallel_actions.drawio.svg)


Finally for **locale evolutions**: If there are no active agents in an environment the only way it can change its state is by means of reaction laws.

![dyn-local-evolutions](diagrams\dynamic_local_evolutions.drawio.svg)




### 3.2. Economic Structure

#### 3.2.1. Agents

We have identified five agents:

* households
* firms
* banks
* central banks
* governments

![agents](diagrams\hierarchy_agents.drawio.svg)



```python
# exemple d'agent avec roles et parametres

firm = model.firms[0]
delta = firm.p.delta           # acces au parametres delta
role = firm.roles['employer']  # acces au role d'employeur

```


#### 3.2.2. Spaces with Roles and Stocks

In accordance with the MASQ approach, roles, stocks and spaces are objects.
The relationships between these objects have been implemented according to the following rules:
- each role or stock item has a reference to the space that contains it
- each space contains homogeneous sets of stock items or roles
- each role has references to its stock items


```python
# exemple d'espace avec roles et stocks

bond_market = bond.space            # acces au marche d'emission du bond
bond_market = bond_issuer.space     # acces au marche de l'emetteur de bond
bond = bond_issuer.bonds[b]         # acces au bond achete par la banque b
bond = bond_market.bonds[g, b]      # acces au bond emis par g et achete par b
bond_buyer = bond_market.buyers[0]  # acces au premier acheteur de bond

```

These objects have been grouped into three spheres:
- the commercial financial sphere
- the commercial real economy sphere
- the non-commercial institutional sphere

The financial sphere comprises:
- `BondMarket`, where the roles `BondBuyer` and `BondIssuer` trade in `Bond` holdings.
- `CreditMarket`, where the `CreditLender` role grants `Loans` to the `CreditBorrower` role;
- `DepositMarket`, where `Deposit` holdings are exchanged between agents playing the roles of `DepositGuarantee`, `DepositBank` or `Depositor`


![financial-sphere](diagrams\hierarchy_financial_objects.drawio.svg)


The real-world domain consists of:
- `LaborMarket`, where stocks of `Job` are modified by interactions between the `Employer` and `Worker` roles.
- `GoodsMarket`, where the actions of the `GoodsConsumer` and `GoodsSupplier` roles create stocks of `Inventories` or `Sales`


![real-sphere](diagrams\hierarchy_real_objects.drawio.svg)


The institutional sphere comprises:
- a single `MonetaryUnion` space, where `CashMoney` and `CashAdvance` stocks are held and exchanged by the `MonetaryAuthority` and `CashHolder` roles;
- several `Country` spaces, where `Equity` or `Transfer` stocks are managed by the `Citizen`, `Company` or `FiscalAuthority` roles.

![institutionnal-sphere](diagrams\hierarchy_institutionnal_objects.drawio.svg)


The `MonetaryUnion` space acts as the **universe** required in the MASQ approach. This space contains all other spaces.


![space-structure](diagrams\space_structure.drawio.svg)

The relationships between these namespaces have been implemented according to the following rules:
- the `MonetaryUnion` namespace contains references to common markets
- the `MonetaryUnion` namespace contains a dictionary of `Country` objects
- the `Country` namespace contains references to national markets

```python
# exemple d'espaces emboites

union = model.monetary_union            # access a l'univers
country = union.countries[n]            # acces au pays n
credit_market = union.credit_market     # acces au marche commun du credit
goods_market = country.goods_market     # acces au marche national des biens

```

### 3.3. Economic Interactions

The economic structure implemented allows several economic mechanisms:
* adjustment of supply or demand
* matching of agents
* transactions within a market
* transactions across multiple markets
* entry into or exit from markets
* autonomous dynamics


#### 3.3.1. Adjusting supply or demand

The prices or quantities supplied and demanded are objective realities that form part of the dynamic state of the roles. Adjusting supply and demand therefore involves the agent modifying the dynamic state of one of its bodies. This operation is based on:

* the agents' decision-making functions
* the roles' perception functions
* the roles' reaction laws.

In the following example, we implement the revision of the salary offered by a firm:


![adjustment](diagrams\example_adjustment.drawio.svg)

In this sequence:
- the decision function `revise_offered_wage` is active
- the perception functions `get_offered_wage` and `perceive_unemployment` are used
- the reaction laws `set_offered_wage` are active

> [!IMPORTANT]
> In the MASQ approach, action functions generate influences, whilst reaction laws are responses to these influences. In this approach, we favour sequential action over simultaneous action. Consequently, the action functions are identical to the reaction laws of a role.


#### 3.3.2. Matching mechanism

Matching is a mechanism that involves the perception of other agents and the modification of relationships within a space. This mechanism is therefore based on:

* the agents' decision functions
* the role perception functions
* the role reaction laws
* the interference laws of a space

In the following example, we implement a household’s job search:

![matching](diagrams\example_matching.drawio.svg)

In this excerpt:
- the decision function `search_jobs` is activated
- the perception function `find_employers` is used
- the action/reaction rule `accept_job` is activated
- the interference rule `create_job` is activated



#### 3.3.3. Transactions within one space

Transactions correspond to exchanges between agents that involve updating stock levels within a space. They also require compliance with the principle of the four accounting entries.

The transaction mechanism is therefore based on:

* the reaction laws of roles
* the interference laws of a space
* stock transformations

Let us illustrate this mechanism using the transfer of profit between the Central Bank and the Government. Here, we present only the action of the Central Bank’s `CashLender` role:


![transactions-01](diagrams\example_transactions_01.drawio.svg)


In this extract:
- the `transfer_profit` reaction rule is enabled
- the `transfer_profit` interference rule is used
- the `incr_profit` and `incr_amount` transformations are applied to the `Transfer` and `CashMoney` stock types



#### 3.3.4. Transactions across multiple spaces

Transactions involve exchanges between agents that may require the updating of stock levels across multiple spaces. However, the MASQ approach enforces the principle of raw space integrity. 
In such cases, the transaction mechanism is based on:

* role reaction laws
* interference laws of a space
* stock transformations
* method calls between spaces

Here we present the example of the purchase of goods, which requires a flow in the real sphere and a flow in the institutional sphere:


![transactions-02](diagrams\example_transactions_02.drawio.svg)

In this excerpt:
- the `buy_goods` interference rule is active
- the `incr_amount` and `decr_quantity` transformations
- the `transfer_cash` interference rule is called

#### 3.3.5. Mobility (market entry-exit)


![mobility](diagrams\example_mobility.drawio.svg)


#### 3.3.6. Autonomous dynamics


![evolution](diagrams\example_evolution.drawio.svg)





### 4. Model simulation

The dynamics of the economy consist of a sequence of events. These events are triggered by a `EcoModel` class which a subclass of `agentpy.Model`. So `EcoModel` is responsible of simulation orchestration.

## 5. Testing Strategy

