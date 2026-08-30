

# Documentation technique simplifiée
Architecture d'un modèle AB-SFC avec AgentPy et approche TDD


## 1. Objectifs


Cette architecture vise à implémenter un modèle **Agent-Based Stock-Flow Consistent (AB-SFC)** inspiré de Caiani et al.


L'objectif est de construire un modèle :


* orienté objet ;
* modulaire ;
* extensible ;
* compatible avec AgentPy ;
* développé selon une approche Test-Driven Development (TDD).


L'architecture repose sur une séparation claire entre 5 concepts:

* les **modèles** qui orchestre la simulation ;
* les **agents** qui prennent les décisions économiques ;
* les **roles** qui représentent les agents dans l'espace simule ;
* les **stocks** qui representent les stocks dans l'espace simule.
* les **spaces** qui fournissent l'environnement d'interaction.


# 2.7 Responsabilités principales des classes


| Classe         | Concept             | Responsabilité                                              |
| -------------- | ------------------- | ----------------------------------------------------------- |
| `EcoSimModel`  | modele simule       | gestion de la simulation (initialisation, evenements)       |
| `EcoAggModel`  | modele aggrege      | calcul des stocks et flux initiaux                          |
| `EcoAgent`     | agent economique    | representation des décisions économiques                    |
| `EcoRole`      | role economique     | comportement spatiale (perceptions + actions) des agents    |
| `EcoStocks`    | stocks economiques  | representation des stocks et flux reels ou monetaires       |
| `EcoSpace`     | espace economique   | gestion des mecanismes d'interaction entre agents           |


Nous avons prefixe les classes de base pour les distinguer des classes abstraites fournies par `AgentPy`.



## 2. Modélisation


### 2.1. Principes de conception

La conception du modele informatique est base sur une adaptation de l'approche **MASQ**.
Pour l'implementation de ce modele nous avons choisi la platerforme `agentpy`.

Notre implementation du modele repose sur deux modeles :

* un modele informatique de la structure de l'economie
* un modele informatique de la dynamique de l'economie


### 2.2. Modele de la structure d'une economie

Une economie est composee de 5 entites:

* des **agents** qui prennent les decisions economiques
* des **parametres** de comportement des agents
* des **espaces** d'interactions des agents
* des **stocks** reels ou monetaires
* des **roles** jouees par les agents dans les espaces


![masq-meta-model](diagrams\masq_meta_model.drawio.svg)

Selon l'approche MASQ:
* les agents sont des *minds* charge de la decision
* les roles sont des *bodies* permettant la perception et l'action
* les stocks sont des simples *objects* passifs
* les espaces sont des *brute spaces* en charge des interactions
* les parametres sont des *cultures* partages par les agents


#### 2.2.1. Agents et Parametres

Nous avons identifies 5 agents:

* les menages
* les firmes
* les banques
* les banques centrales
* les gouvernements

![mc-abm-agents](diagrams\mc_abm_agents.drawio.svg)

la classe `Agent` herite de `agentpy.Agent` et possede:
- un attribut `p` qui donne acces aux `Parameters`
- un dictionnaire des roles jouees `roles`


```python
# exemple d'agent avec roles et parametres

firm = model.firms[0]
delta = firm.p.delta           # acces au parametres delta
role = firm.roles['employer']  # acces au role d'employeur

```


#### 2.2.2. Roles, Stocks et Espaces

Conformement a l'approche MASQ, les roles, stocks et espaces sont des objets. Tous ces objets ont ete implementes comme des sous-classes de `agentpy.Object`.

Les relations entre ces objets on ete implementees selon les regles suivantes :
- chaque role ou stock a une reference a l'espace qui le contient
- chaque espace contient des ensembles homogenes de stocks ou roles
- chaque role a des references a ses stocks


```python
# exemple d'espace avec roles et stocks

bond_market = bond.space            # acces au marche d'emission du bond
bond_market = bond_issuer.space     # acces au marche de l'emetteur de bond
bond = bond_issuer.bonds[b]         # acces au bond achete par la banque b
bond = bond_market.bonds[g, b]      # acces au bond emis par g et achete par b
bond_buyer = bond_market.buyers[0]  # acces au premier acheteur de bond

```

Ces objects ont ete regroupes dans 3 spheres:
- la sphere financiere marchande
- la sphere reel marchande
- la sphere institutionnel non marchande

La sphere financiere est compose de:
- `BondMarket` ou les roles `BondBuyer` ou `BondIssuer` echangent des stocks de `Bond`.
- `CreditMarket` ou les roles `CreditLender` octroie des `Loans` aux roles `CreditBorrower`
- `DepositMarket` ou s'echangent des stocks de `Deposit` entre agents jouant les roles de `DepositGuarantee`, `DepositBank`ou `Depositor`

![financial-sphere](diagrams\hierarchy_financial_objects.drawio.svg)


La sphere reel est compose de:
- `LaborMarket` ou des stocks de `Job` sont modifie par les interactions entre les roles `Employer` ou `Worker`.
- `GoodsMarket` ou l'action des roles `GoodsConsumer` et `GoodsSupplier` creer des stocks de `Inventories` ou `Sales`


![real-sphere](diagrams\hierarchy_real_objects.drawio.svg)


La sphere institutionnelle est compose:
- d'un espace unique `MonetaryUnion` ou des stocks de `CashMoney` et `CashAdvance` sont detenus et echange par des roles `MonetaryAuthority` et `CashHolder`
- de plusieurs espaces `Country` ou des stocks de `Equity` ou`Transfer` sont manipules par des roles `Citizen`, `Company` ou `FiscalAuthority`.

![institutionnal-sphere](diagrams\hierarchy_institutionnal_objects.drawio.svg)


L'espace `MonetaryUnion` joue le role d'**univers** requis dans l'approche MASQ. Cette espace contient tous les autres espaces.


![space-structure](diagrams\space_structure.drawio.svg)

Les relations entre ces espaces on ete implementees selon les regles suivantes :
- l'espace `MonetaryUnion` contient des references au marches communs
- l'espace `MonetaryUnion` contient un dictionnaire des pays `Country`
- l'espace `Country` contient des references aux marches nationaux

```python
# exemple d'espaces emboites

union = model.monetary_union            # access a l'univers
country = union.countries[n]            # acces au pays n
credit_market = union.credit_market     # acces au marche commun du credit
goods_market = country.goods_market     # acces au marche national des biens

```

### 2.3. Modele de la dynamique de economie

la dynamique de l'economie est compose d'une sequence d'evenements. Chaque evenement donne naissance a un cycle de vie (approche MASQ). Ce cycle est compose de 4 phases:
1. activation des **fonctions de decisions**
2. activation des **lois de reactions**
3. activation des **lois d'interferences**
4. activation des **lois d'evolution** locale

on pourra distinguer trois types de dynamiques:
* les actions sequencielles (actions sequencielles et reponses immediates)
* les actions simultannees (actions paralleles et reponses differees)
* les evolutions locales (dynamique de l'environnement en l'absence d'actions des agents)

**modele d'actions et reponses sequentielles**

After deliberating, a mind decides on a set of actions that it wants to perform through its bodies.

![dyn-sequential-actions](diagrams\dynamic_sequential_actions.drawio.svg)



**modele d'actions et reponses simultannees**

After deliberating, a mind decides on a set of actions that it wants to perform through its bodies.

![dyn-parallel-actions](diagrams\dynamic_parallel_actions.drawio.svg)


**modele d'evolutions locales**

If there are no active agents in an environment the only way it can change its state is by means of reaction laws.

![dyn-local-evolutions](diagrams\dynamic_local_evolutions.drawio.svg)


Pour implementer ces phases:
- les fonctions de decisions sont des methodes d'agents
- les lois de reactions sont des methodes de roles
- les lois d'interferences sont des methodes d'espaces
- les lois d'evolution sont des methodes de tous objets

Ces cycles permettent d'implementer plusieurs mecanismes economiques:
* ajustement des offres ou demandes
* appariement des agents
* transactions  dans un espace
* transactions sur plusieurs espaces
* entrée ou sortie des espaces
* dynamique autonome


#### 2.3.1. Ajustement des offres ou demandes

Les prix ou quantites offertes et demandees sont des realites objectives qui font partie de l'etat dynamique des roles. Ajuster les offres et demandes consiste donc pour l'agent a modifier l'etat dynamique d'un de ses corps. Cette operation repose sur:

* les fonctions de decisions des agents
* les fonctions de perceptions des roles
* les lois de reactions des roles.

Dans l'exemple suivant, on implemente la revision du salaire offert par une firme:

![adjustment](diagrams\example_adjustment.drawio.svg)

Dans cette sequence:
- la fonction de decision `revise_offered_wage` est active
- les fonctions de perception `get_offered_wage` et `perceive_unemployment` sont utilise
- les lois de reactions `set_offered_wage` sont actives

> [!IMPORTANT]
> Dans l'approche MASQ les fonctions d'actions produisent des influence tandis que les lois de reactions sont des reponses a ces influences. Dans cette approche, nous privilegions l'action sequentielle a celle simultanee. Par consequent les fonctions d'actions sont identique aux lois de reactions d'un role.


#### 2.3.2. Appariement des agents

L'appariement est un mecanisme qui impliquent la perception des autres agents et la modification des relations a l'interieur d'un espace. Ce mecanisme repose donc sur:

* les fonctions de decisions des agents
* les fonctions de perceptions des roles
* les lois de reactions des roles
* les lois d'interference d'un espace

Dans l'exemple suivant, on implemente la recherche d'emploi par un menage:

![matching](diagrams\example_matching.drawio.svg)

Dans cette sequence extraite:
- la fonction de decision `search_jobs` est activee
- la fonction de perception `find_employers` est utilise
- la fonction d'action/loi de reaction `accept_job` est activee
- la loi d'interference `create_job` est activee



#### 2.3.3. Transactions dans un espace

Les transactions correspondent a des echanges entre agents qui implique la mise a jour des stocks dans un espace. Elle necessite egalement le respect du principle des 4 entrees comptables.

Le mecanisme de transaction repose donc sur:

* les lois de reactions des roles
* les lois d'interference d'un espace
* les transformations des stocks

illustrons ce mecanisme par le transfert de profit entre Banque  Centrale et Governement. Nous presentons ici juste l'action du role `CashLender` de la Banque Centrale:

![transactions-01](diagrams\example_transactions_01.drawio.svg)


Dans cet extrait:
- la loi de reaction `transfer_profit` est activee
- la loi d'interference `transfer_profit` est utilise
- les transformations `incr_profit` et `incr_amount` sont effectues sur les stocks de type `Transfer` et `CashMoney`



#### 2.3.4. Transactions sur plusieurs espaces


Les transactions correspondent a des echanges entre agents qui peuvent impliquer la mise a jour des stocks dans plusieurs espaces. Or l'approche MASQ impose le pincipe d'integrite des espaces  brutes. 
Dans ces cas, le mecanisme de transaction repose sur:

* les lois de reactions des roles
* les lois d'interference d'un espace
* les transformations des stocks
* les appels de methodes entre espaces

Nous presentons ici l'exemple l'achat de biens qui necessite un flux dans la sphere reel et un flux dans la sphere institutionnel:

![transactions-02](diagrams\example_transactions_02.drawio.svg)

Dans cette sequence extraite:
- la loi d'interference `buy_goods` est activee
- les transformations `incr_amount` et `decr_quantity`
- la loi d'interference `transfer_cash` est appele

#### 2.3.5. Mobilite (entrees - sorties)


![mobility](diagrams\example_mobility.drawio.svg)


#### 2.3.6. Dynamique autonome


![evolution](diagrams\example_evolution.drawio.svg)





## 3. Simulation

la simulation est realiser grace a une classe `EcoModel` qui herite de `agentpy.Model`. Cette classe est responsable du deroulement des phases de simulation:

* creation des agents, roles, espaces et stocks initiaux;
* déclenchement des événements;
* collecte des résultats.



## 4. Fichiers








# 3. Vérification : stratégie TDD


Le développement suit trois niveaux de tests.





# 3.1 Tests unitaires


Les tests unitaires vérifient une unité isolée.


Une classe est testée indépendamment de son environnement.


Les dépendances sont remplacées par des mocks.




# 3.2 Tests d'intégration


Les tests d'intégration vérifient un sous-système complet.


Ils utilisent plusieurs composants réels.







# 3.3 Tests d'acceptation


Les tests d'acceptation vérifient le comportement global du modèle.


Ils exécutent une simulation complète :


```
ABSFCModel


↓


Agents


↓


Roles


↓


Markets


↓


Evolution macroéconomique


```


Ils vérifient :


* le comportement global du modèle ;
* la cohérence dynamique ;
* les propriétés économiques attendues ;
* la reproduction des résultats de référence.


Ils incluent également :


* les tests de cohérence SFC ;
* les tests de réplication du modèle de Caiani et al.





# Principes directeurs


* Le **Model orchestre la simulation**.
* Les **agents prennent les décisions**.
* Les **rôles représentent les agents dans les marchés**.
* Les **marchés assurent l'infrastructure d'interaction**.
* Les **marchés ne décident pas et ne mettent pas à jour les agents**.
* Chaque fonctionnalité est développée avec une stratégie TDD.
* La cohérence Stock-Flow Consistent est vérifiée au niveau global.



