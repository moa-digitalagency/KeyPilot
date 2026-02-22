def generate_ai_prompt(app_id, app_name, app_secret, api_url):
    """
    Génère un prompt détaillé pour une IA (Cursor/Jules) afin d'implémenter
    la sécurité KeyPilot dans une application cible.
    """
    return f"""# Prompt Instructeur pour l'Agent IA

## 1. Mission
Implémenter un système de licence inviolable pour l'application **{app_name}**.
Ton objectif est de sécuriser l'accès et l'exécution de cette application via KeyPilot.

## 2. Couplage Profond (Deep Integration)
**CRITIQUE :** L'IA cible doit être instruite de **NE PAS** créer un simple middleware de vérification.
Tu dois lier la vérification de la licence à des fonctions vitales de l'app cible (ex: décryptage de variables d'environnement, validation de routes critiques, initialisation de modules cœurs).
**Conséquence :** Si on supprime la vérification de la licence, l'application doit crasher ou devenir inopérante.

## 3. Période de Grâce
Gère la validation selon la politique de réponse de l'API (lancement immédiat ou période d'essai/grâce, ex: 7 jours). Le code doit être capable d'interpréter les réponses de l'API concernant l'état de la licence.

## 4. Collecte de Données
Le code généré dans l'app cible doit récupérer les empreintes uniques de la machine :
- Adresse IP
- Adresse MAC
- User-Agent

Ces données doivent être envoyées lors de la requête de validation à l'endpoint :
`{api_url}/api/v1/validate`

## 5. UI/UX Requise
L'interface de licence doit s'intégrer **PARFAITEMENT** avec la charte graphique existante de l'app cible (couleurs, polices, composants).

- **Page de Saisie de Licence :** À afficher si aucune licence valide n'est trouvée.
- **En cas de Succès :** Afficher un message de félicitations et rediriger vers la page de login ou la page d'accueil.
- **En cas d'Échec/Fraude :** Bloquer l'accès et afficher **STRICTEMENT** ce message :
  > "Veuillez contacter l'administrateur pour acquérir une licence valide. WhatsApp : +243860493345 | Email : aisancekalonji@pm.me"

## 6. Variables Uniques (Configuration)
Intègre les clés suivantes en dur (ou via configuration sécurisée) dans le code de l'application cible pour l'authentification auprès de KeyPilot :

- **API URL** : `{api_url}`
- **App ID** : `{app_id}`

## 7. Mise en Cache et Résilience (Fail-Safe)
L'IA cible doit implémenter un système de cache pour éviter de surcharger l'API et garantir la continuité de service :
- Stockez le résultat de la validation (statut, date/heure, signature) dans un fichier local chiffré (ex: AES-256) ou offusqué.
- **Mode Hors-Ligne Toléré (Grace Period)** : Si la requête HTTP vers l'API KeyPilot échoue (Timeout, Erreur 500), le système DOIT consulter ce cache local.
- Si le cache indique une licence valide et que la dernière validation réussie date de moins de **72 heures**, l'application doit démarrer normalement.
- Au-delà de 72 heures sans contact avec le serveur, l'application se verrouille.

---
**Instruction Finale :** Analyse la structure actuelle du projet `{app_name}` et propose une implémentation qui respecte ces contraintes de sécurité maximale.
"""
