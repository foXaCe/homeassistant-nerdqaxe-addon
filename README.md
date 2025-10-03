# NerdQAxe+ Miner - Home Assistant HACS Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

Intégration HACS pour monitorer et contrôler votre NerdQAxe+ Bitcoin Miner dans Home Assistant.

## Description

Cette custom integration permet d'intégrer votre miner NerdQAxe+ dans Home Assistant. Elle crée automatiquement des sensors pour suivre les performances, la température, la consommation électrique et bien plus.

**Type d'intégration :** Custom Component HACS (pas un addon Docker)

## Architecture du projet

### API REST du NerdQAxe+

Le firmware NerdQAxe+ expose déjà une API REST complète (pas besoin de modifications firmware) :

**Endpoints disponibles :**
- `GET /api/system/info` - Informations système complètes
- `GET /api/system/asic` - Informations ASIC
- `GET /api/swarm/info` - Informations Swarm
- `PATCH /api/system` - Modifier la configuration
- `POST /api/system/restart` - Redémarrer le miner

**Données retournées par `/api/system/info` :**
```json
{
  "hashRate": 1200.5,
  "hashRate_1m": 1185.2,
  "hashRate_1h": 1150.8,
  "temp": 65.3,
  "vrTemp": 58.7,
  "power": 15.2,
  "voltage": 12.1,
  "current": 1.25,
  "fanspeed": 75,
  "fanrpm": 4500,
  "sharesAccepted": 1234,
  "sharesRejected": 5,
  "isStratumConnected": true,
  "deviceModel": "NerdQAxePlus",
  "hostname": "nerdqaxe-123"
}
```

### Structure de l'intégration

```
custom_components/nerdqaxe/
├── __init__.py          # Initialisation et coordinateur
├── manifest.json        # Métadonnées de l'intégration
├── const.py             # Constantes
├── config_flow.py       # Configuration via UI
├── sensor.py            # Sensors (hashrate, temp, power, etc.)
└── binary_sensor.py     # Binary sensors (stratum connected)
```

## Sensors créés

L'intégration crée automatiquement les sensors suivants :

### Hashrate
- `sensor.nerdqaxe_hashrate` - Hashrate actuel (GH/s)
- `sensor.nerdqaxe_hashrate_1m` - Hashrate moyenne 1 minute (GH/s)
- `sensor.nerdqaxe_hashrate_10m` - Hashrate moyenne 10 minutes (GH/s)
- `sensor.nerdqaxe_hashrate_1h` - Hashrate moyenne 1 heure (GH/s)
- `sensor.nerdqaxe_hashrate_1d` - Hashrate moyenne 1 jour (GH/s)

### Température
- `sensor.nerdqaxe_temperature` - Température du chip (°C)
- `sensor.nerdqaxe_vr_temperature` - Température du régulateur de tension (°C)

### Puissance
- `sensor.nerdqaxe_power` - Consommation électrique (W)
- `sensor.nerdqaxe_voltage` - Tension (V)
- `sensor.nerdqaxe_current` - Courant (A)
- `sensor.nerdqaxe_core_voltage` - Voltage du core (mV)

### Ventilation
- `sensor.nerdqaxe_fan_speed` - Vitesse du ventilateur (%)
- `sensor.nerdqaxe_fan_rpm` - Tours par minute du ventilateur (RPM)

### Mining
- `sensor.nerdqaxe_shares_accepted` - Shares acceptés
- `sensor.nerdqaxe_shares_rejected` - Shares rejetés
- `sensor.nerdqaxe_best_difficulty` - Meilleure difficulté trouvée
- `sensor.nerdqaxe_best_session_difficulty` - Meilleure difficulté de la session
- `sensor.nerdqaxe_found_blocks` - Blocs trouvés (session actuelle)
- `sensor.nerdqaxe_total_found_blocks` - Total des blocs trouvés
- `binary_sensor.nerdqaxe_stratum_connected` - État de connexion au pool

### Informations
- `sensor.nerdqaxe_device_model` - Modèle du device
- `sensor.nerdqaxe_hostname` - Nom d'hôte du miner
- `sensor.nerdqaxe_wifi_rssi` - Puissance du signal WiFi (dBm)
- `sensor.nerdqaxe_frequency` - Fréquence ASIC (MHz)
- `sensor.nerdqaxe_version` - Version du firmware

### Contrôle et Mise à jour
- `button.nerdqaxe_restart` - Bouton pour redémarrer le miner
- `update.nerdqaxe_firmware_update` - Entité de mise à jour firmware (vérifie automatiquement les nouvelles versions sur GitHub)

## Installation

### Méthode 1 : Via HACS (recommandée)

1. Ouvrir HACS dans Home Assistant
2. Aller dans "Integrations"
3. Cliquer sur les 3 points en haut à droite → "Custom repositories"
4. Ajouter l'URL : `https://github.com/VOTRE_USERNAME/homeassistant-nerdqaxe`
5. Catégorie : "Integration"
6. Cliquer sur "Add"
7. Rechercher "NerdQAxe+" et installer
8. Redémarrer Home Assistant

### Méthode 2 : Installation manuelle

1. Télécharger le dossier `custom_components/nerdqaxe`
2. Copier dans `<config>/custom_components/nerdqaxe`
3. Redémarrer Home Assistant

## Configuration

### Via l'interface utilisateur

1. Aller dans **Paramètres** → **Appareils et services**
2. Cliquer sur **+ Ajouter une intégration**
3. Rechercher "NerdQAxe+"
4. Entrer l'adresse IP de votre miner (ex: `192.168.1.100`)
5. L'intégration va se connecter et créer automatiquement tous les sensors

### Options

Après l'installation, vous pouvez configurer :
- **Scan interval** : Intervalle de mise à jour en secondes (5-300, défaut: 30)

Pour modifier les options :
1. Aller dans **Paramètres** → **Appareils et services**
2. Trouver "NerdQAxe+ Miner"
3. Cliquer sur **Options**

## Utilisation

### Exemple de carte Lovelace

```yaml
type: entities
title: NerdQAxe+ Miner
entities:
  - entity: sensor.nerdqaxe_hashrate
    name: Hashrate
  - entity: sensor.nerdqaxe_hashrate_1h
    name: Hashrate 1h
  - entity: sensor.nerdqaxe_temperature
    name: Température
  - entity: sensor.nerdqaxe_power
    name: Consommation
  - entity: sensor.nerdqaxe_shares_accepted
    name: Shares acceptés
  - entity: binary_sensor.nerdqaxe_stratum_connected
    name: Pool connecté
```

### Carte avec graphique

```yaml
type: vertical-stack
cards:
  - type: entities
    title: NerdQAxe+ Miner
    entities:
      - entity: sensor.nerdqaxe_hashrate_1h
        name: Hashrate 1h
      - entity: sensor.nerdqaxe_temperature
      - entity: sensor.nerdqaxe_power
      - entity: binary_sensor.nerdqaxe_stratum_connected

  - type: history-graph
    title: Hashrate
    hours_to_show: 24
    entities:
      - entity: sensor.nerdqaxe_hashrate_1h

  - type: history-graph
    title: Température
    hours_to_show: 24
    entities:
      - entity: sensor.nerdqaxe_temperature
```

### Exemple d'automatisation - Alerte température

```yaml
automation:
  - alias: "Alerte température miner élevée"
    trigger:
      - platform: numeric_state
        entity_id: sensor.nerdqaxe_temperature
        above: 80
    action:
      - service: notify.mobile_app
        data:
          message: "⚠️ Température miner élevée : {{ states('sensor.nerdqaxe_temperature') }}°C"
          title: "NerdQAxe+ Alert"
```

### Exemple d'automatisation - Pool déconnecté

```yaml
automation:
  - alias: "Alerte pool déconnecté"
    trigger:
      - platform: state
        entity_id: binary_sensor.nerdqaxe_stratum_connected
        to: "off"
        for: "00:05:00"
    action:
      - service: notify.mobile_app
        data:
          message: "⚠️ Le miner NerdQAxe+ est déconnecté du pool depuis 5 minutes"
```

### Exemple d'automatisation - Hashrate faible

```yaml
automation:
  - alias: "Alerte hashrate faible"
    trigger:
      - platform: numeric_state
        entity_id: sensor.nerdqaxe_hashrate_1h
        below: 1000
        for: "00:10:00"
    action:
      - service: notify.mobile_app
        data:
          message: "⚠️ Hashrate faible : {{ states('sensor.nerdqaxe_hashrate_1h') }} GH/s"
```

### Redémarrage du miner

Le bouton de redémarrage est disponible dans l'interface :

```yaml
type: button
entity: button.nerdqaxe_restart
name: Redémarrer le miner
icon: mdi:restart
```

Ou dans une automatisation :

```yaml
automation:
  - alias: "Redémarrage automatique si pool déconnecté"
    trigger:
      - platform: state
        entity_id: binary_sensor.nerdqaxe_stratum_connected
        to: "off"
        for: "00:15:00"
    action:
      - service: button.press
        target:
          entity_id: button.nerdqaxe_restart
      - service: notify.mobile_app
        data:
          message: "🔄 Redémarrage du miner suite à déconnexion prolongée du pool"
```

### Mise à jour du firmware

L'entité `update.nerdqaxe_firmware_update` vérifie automatiquement les nouvelles versions sur GitHub :

**Affichage dans Lovelace :**

```yaml
type: update
entity: update.nerdqaxe_firmware_update
show_title: true
show_current_version: true
show_latest_version: true
```

**Installation d'une mise à jour :**

L'entité de mise à jour apparaît automatiquement dans le dashboard Home Assistant quand une nouvelle version est disponible. Cliquez simplement sur "Installer" pour télécharger et flasher la nouvelle version directement depuis GitHub.

**Note importante :** Le miner redémarrera automatiquement après l'installation de la mise à jour.

## Développement

### Architecture technique

#### `__init__.py`
Fichier principal qui :
- Initialise l'intégration
- Crée le `DataUpdateCoordinator` pour gérer les mises à jour
- Configure les plateformes (sensor, binary_sensor)

**Classe `NerdQAxeDataUpdateCoordinator` :**
- Se connecte à `http://<host>/api/system/info` toutes les X secondes
- Parse les données JSON
- Distribue les données aux sensors via le pattern Coordinator

#### `config_flow.py`
Gère la configuration via l'UI :
- Validation de la connexion au miner
- Configuration de l'intervalle de scan
- Détection automatique du hostname et modèle

#### `sensor.py`
Définit tous les sensors :
- Utilise `CoordinatorEntity` pour les mises à jour automatiques
- Device class appropriés pour l'Energy Dashboard
- State class pour les statistiques long-terme

#### `binary_sensor.py`
Sensor binaire pour l'état de connexion au pool Stratum.

#### `button.py`
Définit le bouton de redémarrage :
- Appelle l'API `POST /api/system/restart` du miner
- Redémarre le miner instantanément

#### `update.py`
Entité de mise à jour firmware :
- Vérifie les releases GitHub automatiquement
- Compare la version installée avec la dernière version disponible
- Filtre les pre-releases et versions RC
- Télécharge et installe le firmware directement depuis GitHub
- Utilise l'endpoint `POST /api/system/OTA/github` avec l'URL du firmware
- Affiche les release notes dans Home Assistant

### Ajouter un nouveau sensor

1. Dans `const.py`, ajouter la constante :
```python
ATTR_NOUVEAU_CHAMP = "nouveauChamp"
```

2. Dans `sensor.py`, ajouter dans la liste `entities` :
```python
NerdQAxeSensor(
    coordinator,
    "nouveau_sensor",
    "Nom du Sensor",
    ATTR_NOUVEAU_CHAMP,
    icon="mdi:icon-name",
    unit="unité",
    device_class=SensorDeviceClass.XXX,
    state_class=SensorStateClass.MEASUREMENT,
),
```

### Test en local

1. Copier `custom_components/nerdqaxe` dans votre config HA
2. Redémarrer HA
3. Ajouter l'intégration via l'UI
4. Vérifier les logs : **Paramètres** → **Système** → **Journaux**

### Debug

Activer les logs de debug dans `configuration.yaml` :

```yaml
logger:
  default: info
  logs:
    custom_components.nerdqaxe: debug
```

## Roadmap / Features futures

### ✅ Features implémentées :
- [x] Bouton de redémarrage du miner
- [x] Entité de mise à jour avec vérification automatique des versions GitHub
- [x] Sensor de version du firmware
- [x] Intégration avec Energy Dashboard de HA (sensors power, voltage, current)
- [x] Sensors pour l'uptime (via hashrate 1d)

### 🔜 Features à ajouter :
- [ ] Support WebSocket pour mises à jour temps réel du hashrate
- [ ] Service HA pour modifier la fréquence/voltage dynamiquement
- [ ] Support multi-miners (plusieurs appareils dans une seule intégration)
- [ ] Auto-découverte des miners sur le réseau (mDNS)
- [ ] Dashboard Lovelace pré-configuré avec toutes les cartes
- [ ] Sensor pour le pool difficulty
- [ ] Alertes configurables intégrées via UI
- [ ] Notification lors des mises à jour disponibles
- [ ] Backup/restore de la configuration du miner

### Améliorations possibles :
- Ajout de services Home Assistant pour contrôler le miner
- Support de plusieurs miners simultanément avec un seul entry
- Graphiques de performance intégrés
- Notifications push configurables via UI
- Support des boards NerdAxeGamma et autres variantes

## Différence avec un Addon HA

**Custom Integration (HACS) :**
- ✅ S'intègre directement dans Home Assistant
- ✅ Utilise les sensors natifs HA
- ✅ Léger et performant
- ✅ Statistiques long-terme automatiques
- ✅ Compatible Energy Dashboard
- ❌ Pas d'interface web séparée

**Addon (Docker) :**
- ✅ Peut avoir une interface web
- ✅ Indépendant de HA
- ❌ Plus lourd (conteneur Docker)
- ❌ Nécessite Supervisor

Ce projet est une **Custom Integration HACS**, donc plus légère et mieux intégrée !

## Contribution

Les contributions sont bienvenues ! N'hésitez pas à :
- Ouvrir une issue pour un bug ou une feature request
- Soumettre une pull request
- Améliorer la documentation

## Licence

MIT

## Crédits

- **Firmware NerdQAxe+** : https://github.com/shufps/ESP-Miner-NerdQAxePlus
- **Hardware NerdQAxe+** : https://github.com/shufps/qaxe
- **BitAxe devs** : @skot (ESP-Miner), @ben, @jhonny
- **NerdAxe dev** : @BitMaker

## Support

- **Issues intégration HA** : [GitHub Issues](https://github.com/VOTRE_USERNAME/homeassistant-nerdqaxe/issues)
- **Issues firmware** : [ESP-Miner-NerdQAxePlus Issues](https://github.com/shufps/ESP-Miner-NerdQAxePlus/issues)
- **Discord NerdMiner** : [![Discord](https://dcbadge.vercel.app/api/server/3E8ca2dkcC)](https://discord.gg/3E8ca2dkcC)
