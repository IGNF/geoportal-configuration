#!/bin/sh

# Définit le nombre maximum de commits à conserver (argument 1, ou 100 par défaut).
MAX="${1:-100}"
# Définit la branche cible à traiter (argument 2, ou dist par défaut).
TARGET_BRANCH="${2:-dist}"

# Récupère le nom de la branche Git actuellement checkoutée.
CURRENT_BRANCH="$(git rev-parse --abbrev-ref HEAD)"

# Vérifie que le script est exécuté sur la branche cible.
if [ "$CURRENT_BRANCH" != "$TARGET_BRANCH" ]; then
    # Informe que la branche courante ne correspond pas et qu'aucune action ne sera faite.
    echo "La branche courante est '$CURRENT_BRANCH', attendu '$TARGET_BRANCH'. Nettoyage de l'historique ignoré."
    # Quitte sans erreur pour ne pas casser le workflow quand on n'est pas sur la bonne branche.
    exit 0
fi

# Compte le nombre total de commits accessibles depuis HEAD.
COUNT="$(git rev-list --count HEAD)"

# Lance la réécriture uniquement si le nombre de commits dépasse la limite MAX.
if [ "$COUNT" -gt "$MAX" ]; then
    # Crée un commit racine orphelin (sans parent) dont l'arbre est identique au
    # MAX-ième commit depuis HEAD. Cela évite les conflits liés à la ré-application
    # séquentielle de commits qui touchent les mêmes fichiers.
    ORPHAN_ROOT=$(git commit-tree "HEAD~$((MAX - 1))^{tree}" -m "$(git log --format='%s' "HEAD~$((MAX - 1))")")

    # Rejoue uniquement les (MAX - 1) commits les plus récents par-dessus la
    # nouvelle racine orpheline, pour obtenir exactement MAX commits au total.
    git rebase --onto "$ORPHAN_ROOT" "HEAD~$((MAX - 1))" HEAD

    # Force la mise à jour distante de la branche cible avec protection --force-with-lease.
    git push --force-with-lease origin "$TARGET_BRANCH"
fi