
# Documentation technique simplifiée

## Architecture d’un modèle AB-SFC avec AgentPy et approche TDD

---

# 1. Objectifs

Cette architecture vise à implémenter un modèle **Agent-Based Stock-Flow Consistent (AB-SFC)** inspiré de Caiani et al.

L’objectif est de construire un modèle :

* orienté objet ;
* modulaire ;
* extensible ;
* compatible avec AgentPy ;
* développé selon une approche Test-Driven Development (TDD).

L’architecture repose sur une séparation claire entre :

* le **Modèle**, qui orchestre la simulation ;
* les **Agents**, qui prennent les décisions économiques ;
* les **Roles**, qui représentent les agents dans les marchés ;
* les **Markets**, qui fournissent l’environnement d’interaction.

---

# 2. Modélisation

# 2.1 Principes de conception

L’architecture générale est :

```
                           +----------------+
                         |     Model      |
                         |  ABSFCModel    |
                         +----------------+
                         | - crée agents  |
                         | - crée marchés |
                         | - orchestre    |
                         |   événements   |
                         +-------+--------+
                                 |
                --------------------------------
                |                              |
                |                              |
                v                              v

        +---------------+              +----------------+
        |     Agent     |              |     Market     |
        | Firm/Household|              | Network        |
        +---------------+              +----------------+
        | - état        |              | - règles       |
        | - bilan SFC   |              |   interaction  | 
        | - décisions   |              | - contrats     |
        +-------+-------+              | - transactions |
                |                      +-------+--------+
                |                              ^
                | possède                      |
                |                              |
                v                              |
        +---------------+                      |
        |     Role      |----------------------+
        |  AgentNode    |
        +---------------+
        | - représente |
        |   l'agent    |
        |   sur marché |
        | - expose     |
        |   actions    |
        +---------------+


```

Chaque composant possède une responsabilité limitée.

---

# 2.2 Classe Model (`ABSFCModel`)

Le modèle est le **chef d’orchestre de la simulation**.

Il est responsable de :

* créer les agents ;
* créer les marchés ;
* créer les rôles associés aux agents ;
* gérer le calendrier de simulation ;
* déclencher les événements dans le bon ordre ;
* collecter les résultats.

Le modèle ne contient pas de comportement économique individuel.

Exemple :

```
ABSFCModel

1. création des firmes
2. création des ménages
3. création des marchés
4. association des rôles
5. exécution des périodes
```

Une période suit une séquence d’événements définie par le modèle :

```
Début période

      ↓

Décisions des agents

      ↓

Actions des rôles

      ↓

Interactions via les marchés

      ↓

Transactions comptables

      ↓

Mise à jour des états

      ↓

Fin période

```

---

# 2.3 Agents

Un agent représente une unité économique autonome.

Exemples :

* Firm
* Household

L’agent possède :

* un état interne ;
* un bilan comptable ;
* une mémoire ;
* des règles de décision.

L’agent est responsable uniquement de ses choix.

Exemple :

```
Firm

decide_production()

decide_price()

decide_hiring()
```

```
Household

decide_consumption()

decide_labor_supply()
```

L’agent ne :

* recherche pas directement un partenaire ;
* ne crée pas de contrat ;
* ne réalise pas les transactions.

---

# 2.4 Roles (`AgentNode`)

Un rôle représente la participation d’un agent à un marché.

Les rôles sont des sous-classes de :

```
AgentNode
```

Exemples :

```
Firm

 ├── ProducerRole
 └── EmployerRole
```

```
Household

 ├── ConsumerRole
 └── WorkerRole
```

Un rôle sert d’interface entre :

```
Agent  ←→  Market
```

Il permet :

* d’exposer les informations nécessaires aux interactions ;
* de recevoir les résultats d’une interaction ;
* de représenter l’agent dans un marché donné.

Le rôle ne décide pas.

---

# 2.5 Markets (`Network`)

Un marché est une sous-classe de :

```
Network
```

Exemples :

```
LaborMarket

GoodsMarket
```

Un marché contient des rôles comme nœuds :

```
LaborMarket

EmployerRole

WorkerRole
```

Le marché est une infrastructure d’interaction.

Ses responsabilités sont :

## Gestion des participants

* enregistrer les rôles présents ;
* permettre la recherche d’un rôle ;
* fournir un accès aux informations nécessaires.

Exemple :

```
find_available_workers()
```

---

## Application des règles d’interaction

Le marché applique les règles qui régissent les relations entre rôles.

Exemple :

```
EmployerRole

propose_contract()

        ↓

LaborMarket

vérifie les règles

        ↓

WorkerRole

accepte ou refuse

```

---

## Gestion des transactions

Le marché réalise les opérations techniques liées aux échanges :

* création de contrats ;
* création de liens entre rôles ;
* exécution des écritures comptables associées aux transactions.

Exemple :

```
EmploymentContract

Firm

↔

Household

```

Le marché ne décide pas :

* qui est embauché ;
* quel salaire choisir ;
* combien produire ;
* quel prix appliquer.

Ces décisions appartiennent aux agents.

---

# 2.6 Exemple d’interaction

## Marché du travail

```
Firm

decide_hiring()

        ↓

EmployerRole

déclare une demande

        ↓

LaborMarket

cherche des WorkerRole disponibles

        ↓

Application des règles

        ↓

Création du contrat

        ↓

Mise à jour comptable

```

---

# 2.7 Responsabilités principales des classes

| Classe             | Responsabilité                                                  |
| ------------------ | --------------------------------------------------------------- |
| `ABSFCModel`       | création des objets, séquence des événements, orchestration     |
| `Agent`            | décisions économiques, état interne, bilan SFC                  |
| `Role (AgentNode)` | représentation d’un agent dans un marché                        |
| `Market (Network)` | règles d’interaction, accès aux rôles, transactions et contrats |

---

# 3. Vérification : stratégie TDD

Le développement suit trois niveaux de tests.

---

# 3.1 Tests unitaires

Les tests unitaires vérifient une unité isolée.

Une classe est testée indépendamment de son environnement.

Les dépendances sont remplacées par des mocks.

Exemples :

### Agent

```
Firm

decide_production()

```

Vérification :

* la décision respecte les règles internes.

---

### Role

```
EmployerRole

create_offer()

```

Vérification :

* l’action générée correspond à la décision de la firme.

---

### Market

```
LaborMarket

create_contract()

```

Vérification :

* les règles d’interaction sont correctement appliquées.

---

# 3.2 Tests d’intégration

Les tests d’intégration vérifient un sous-système complet.

Ils utilisent plusieurs composants réels.

Exemple :

## Sous-système marché du travail

```
Firm

↓

EmployerRole

↓

LaborMarket

↓

WorkerRole

↓

Household

```

Vérification :

* génération des offres ;
* recherche des travailleurs ;
* création des contrats ;
* cohérence des flux associés.

---

## Sous-système marché des biens

```
Firm

↓

ProducerRole

↓

GoodsMarket

↓

ConsumerRole

↓

Household

```

Vérification :

* interaction producteurs-consommateurs ;
* transactions ;
* flux monétaires.

---

# 3.3 Tests d’acceptation

Les tests d’acceptation vérifient le comportement global du modèle.

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

---

# Principes directeurs

* Le **Model orchestre la simulation**.
* Les **agents prennent les décisions**.
* Les **rôles représentent les agents dans les marchés**.
* Les **marchés assurent l’infrastructure d’interaction**.
* Les **marchés ne décident pas et ne mettent pas à jour les agents**.
* Chaque fonctionnalité est développée avec une stratégie TDD.
* La cohérence Stock-Flow Consistent est vérifiée au niveau global.


