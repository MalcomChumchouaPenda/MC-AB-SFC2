# Replicating Multi-Country AB-SFC Model: A Modular and Test-Driven approach based on MASQ Metamodel


## Table of Contents

1. [Overview](#1-overview)
2. [Scientific Reference](#2-scientific-reference)
3. [Replication Scope](#3-replication-scope)
4. [Technical Architecture](#4-technical-architecture)
5. [Project Structure](#5-project-structure)
6. [Installation](#6-installation)
7. [Running Simulations](#7-running-simulations)
8. [Running Tests](#8-running-tests)
9. [Deviations](#9-deviations)
10. [License](#10-license)



## 1. Overview

This repository presents a replication of the multi-country Agent-Based Stock-Flow Consistent (MC-AB-SFC) model developed by Caiani et al. (2018).

The model is implemented using the MASQ metamodel (Dinu et al., 2012) through a modular and test-driven engineering approach, with the objective of providing a transparent, reproducible, and extensible implementation.


## 2. Scientific Reference

* Caiani, A., Catullo, E., and Gallegati, M. (2018). *The effects of fiscal targets in a monetary union: a multi-country agent based-stock flow consistent model*. Industrial and Corporate Change.

* Dinu, R., Stratulat,T., and Ferber, J. (2012). *A Formal Model of Agent Interaction Based on MASQ*. AMPLE: Agent-based Modeling for PoLicy Engineering. Montpellier, France.


## 3. Replication Scope

This replication focuses on preserving the main institutional sectors the main economic relationships, the core economic mechanisms, the accounting consistency principles and the emergent macroeconomic properties of the original framework.

Extensions, refinements, and additional empirical calibration procedures are considered outside the initial scope of this implementation.

## 4. Technical Architecture


## 5. Project Structure
The repository is organized into three main parts: 
* `code/`: model implementation, associated tests, and experiment scripts; 
* `data/`: input datasets, generated simulation outputs, and analysis results; 
* `docs/`: scientific and technical documentation (including exploratory notebooks). 

```
MC-AB-SFC2/
│
├── code/
│   │
│   ├── model/                   # model implementation based on MASQ approach
│   │   ├── agents/              # definition of agents state and behaviors
│   │   ├── roles/               # implementation of agent roles
│   │   ├── spaces/              # representation of interaction spaces
│   │   ├── stocks/              # representation of economic stocks
│   │   ├── base.py              # definitions of basic model entities
│   │   └── model.py             # model simulation tools
│   │
│   ├── scripts/                 # experiments scripts (scenarios)
│   │
│   ├── tests/                   # tests of novel model implementation
│   │   ├── unit/                # unit tests of agents, roles, stocks and spaces
│   │   ├── integration/         # integration tests of economic mechanisms
│   │   └── acceptance/          # acceptance tests (model verification)
│   │
│   └── notebooks/               # data analysis notebooks
│
├── data/                        # Input/Intermediate/Ouput data
├── docs/                        # Model and replication documentation (include notebooks)
│   ├── ODD document.pdf         # Scientific documentation (ODD standard)
│   └── Technical document.pdf   # Technical documentation of implementation
│
├── pyproject.toml               # Python project configuration and dependencies
├── README.md                    # Project overview, installation and usage informations
└── LICENSE                      # License governing the use and distribution of the project

```


The `code/model/agents/` folder contains : 
* `public/` sub-folder for public agents definition
* `private/` sub-folder for private agents definition

Within `code/model/`, the `roles/`, `stocks/` and `spaces/` folders each contains : 
* a `institutionnal/` sub-folder for institutionnal entities
* a `financial/` sub-folder for financial entities
* a `real/` sub-folder for real entities


## 6. Installation


## 7. Running Simulations


## 8. Running Tests


## 9. Deviations


## 10. License

