# Release Notes / Notes de Version - WeeWX ModbusTcp Driver

## Version 1.2 - Feature Release: Rain Support / Ajout de Fonctionnalité : Support de la Pluie

**Release Date / Date de Sortie:** October 6, 2025 / 6 octobre 2025

### Major Enhancements and Reliability / Améliorations Majeures et Fiabilité

* **Rain Delta Calculation Integrated into the Driver (Robust Solution):**
    * The calculation of interval rain (**`rain`**) has been moved from the internal WeeWX service (**`StdDelta`**) directly into the `ModbusTcpDriver`.
    * **Critical Fix:** This change resolves recurring failures and **`NULL`** values in the `rain` field, which were caused by unreliable persistence of the cumulative value (**`rain_total`**) in the database (specifically MariaDB) and synchronization issues with the `StdDelta` service.
    * The driver now uses internal memory (**`self.last_rain`**) to subtract the new cumulative reading from the old one, ensuring that the delta (`rain`) is always correctly calculated and inserted into the packet before archiving.

* **Calcul du Delta de Pluie intégré au Driver (Solution Robuste) :**
    * Le calcul de la pluie par intervalle (**`rain`**) a été déplacé du service interne de WeeWX (**`StdDelta`**) directement dans le `ModbusTcpDriver`.
    * **Correction Critique :** Cette modification résout les échecs récurrents et les valeurs **`NULL`** dans le champ `rain`, qui étaient causés par la persistance peu fiable de la valeur cumulative (**`rain_total`**) dans la base de données (notamment MariaDB) et des problèmes de synchronisation avec le service `StdDelta`.
    * Le driver utilise désormais sa mémoire interne (**`self.last_rain`**) pour soustraire la nouvelle lecture cumulative de l'ancienne, garantissant que le delta (`rain`) est toujours correctement calculé et inséré dans le paquet avant l'archivage.

### Code Changes / Modifications du Code

* **`genLoopPackets` Method:** Delta logic is fully implemented. If the field read is **`rain_total`**, the driver calculates `pkt['rain'] = calculate_rain(value, self.last_rain)` and updates `self.last_rain`. / *La logique de delta est entièrement implémentée. Si le champ lu est **`rain_total`**, le driver calcule `pkt['rain'] = calculate_rain(value, self.last_rain)` et met à jour `self.last_rain`.*
* **Unit System Update:** Changed the default packet unit system from `weewx.METRIC` to **`weewx.METRICWX`** (Standard Weather Metric) for generated loop packets. / *Le système d'unités par défaut des paquets a été changé de `weewx.METRIC` à **`weewx.METRICWX`** (Météo Métrique Standard) pour les paquets de boucle générés.*

### Impact on Configuration (`weewx.conf`) / Impact sur la Configuration (`weewx.conf`)

* **Required / Obligatoire :** The sensor field name for the cumulative reading **must** be named **`rain_total`** in `weewx.conf` for the internal delta calculation to activate. / *Le nom du champ de capteur pour la lecture cumulative **doit** être nommé **`rain_total`** dans `weewx.conf` pour que le calcul de delta interne s'active.*
* **Recommended / Recommandé :** It is strongly advised to **remove** the `weewx.wxxtypes.StdDelta` service from the `xtype_services` list in the `[Engine]` section to avoid conflicts and simplify the processing pipeline. / *Il est fortement conseillé de **retirer** le service `weewx.wxxtypes.StdDelta` de la liste `xtype_services` dans la section `[Engine]` pour éviter les conflits et simplifier le pipeline de traitement.*

---

## 🐛 Version 1.1.1 - Fix Release: Logger / Correction : Logger

**Release Date / Date de Sortie:** October 3, 2025 / 3 octobre 2025

Fix the log level error. / *Correction de l'erreur de niveau de journalisation.*

---

## Version 1.1 - Feature Release: 32-bit Data Support / Ajout de Fonctionnalité : Support des Données 32 bits

**Release Date / Date de Sortie:** October 3, 2025 / 3 octobre 2025

This minor release introduces a crucial feature for compatibility with sensors that report high-resolution or accumulated values across two Modbus registers. / *Cette version mineure introduit une fonctionnalité cruciale pour la compatibilité avec les capteurs qui signalent des valeurs haute résolution ou accumulées sur deux registres Modbus.*

### ✨ New Feature / Nouvelle Fonctionnalité

#### 32-bit Value Support (`int32`) / Support des Valeurs 32 bits (`int32`)

* **New Addition:** The configuration parameter **`data_type = int32`** has been added to the field definitions in `weewx.conf`. / *Le paramètre de configuration **`data_type = int32`** a été ajouté aux définitions de champs dans `weewx.conf`.*
* **Functionality:** The driver can now read two consecutive 16-bit registers and assemble them into a single 32-bit integer, primarily used for sensors such as illumination (**`radiation`**). / *Le driver peut désormais lire deux registres consécutifs de 16 bits et les assembler en un seul entier de 32 bits, principalement utilisé pour des capteurs tels que l'éclairement (**`radiation`**).*
* **Robustness:** Includes specific error handling to detect and log if the configured Modbus read length is insufficient for the requested 32-bit type. / *Inclut une gestion des erreurs spécifique pour détecter et journaliser si la longueur de lecture Modbus configurée est insuffisante pour le type 32 bits demandé.*

### 🐛 Bug Fixes and Minor Improvements / Corrections de Bugs et Améliorations Mineures

* Updated the `default_stanza` documentation to include a clear example for using `data_type = int32`. / *Mise à jour de la documentation `default_stanza` pour inclure un exemple clair d'utilisation de `data_type = int32`.*

---

## Version 1.0 - Initial Stable Release / Première Version Stable Initiale

---

This major release provides a stable, robust platform for reading Modbus TCP data into WeeWX. / *Cette version majeure fournit une plateforme stable et robuste pour lire les données Modbus TCP dans WeeWX.*

### 🚀 Key Features / Fonctionnalités Clés

#### Enhanced Connection Resilience / Résilience Améliorée de la Connexion

* **Exponential Backoff:** Implemented an exponential backoff strategy for all connection failures. The driver now automatically increases the delay between reconnection attempts (up to **60s** max) to prevent network flooding and reduce system load during outages. / *Implémentation d'une stratégie de *backoff* exponentiel pour toutes les erreurs de connexion. Le driver augmente désormais automatiquement le délai entre les tentatives de reconnexion (jusqu'à **60 secondes** maximum) pour prévenir l'engorgement du réseau et réduire la charge système pendant les pannes.*
* **Advanced Diagnostics:** Modbus protocol errors now log the **specific Modbus exception code**, which simplifies the troubleshooting of configuration issues (e.g., `ILLEGAL DATA ADDRESS`). / *Les erreurs du protocole Modbus journalisent désormais le **code d'exception Modbus spécifique**, ce qui simplifie le dépannage des problèmes de configuration (par exemple, `ILLEGAL DATA ADDRESS`).*

#### Configuration Stability / Stabilité de la Configuration

* **Input Validation:** Strict validation of all mandatory configuration parameters (`slave_id`, `registry`, `length`, `index`, `scale`) during driver startup. / *Validation stricte de tous les paramètres de configuration obligatoires (`slave_id`, `registry`, `length`, `index`, `scale`) lors du démarrage du driver.*

---
*License: Distributed under the MIT License. / Licence : Distribué sous la licence MIT.*