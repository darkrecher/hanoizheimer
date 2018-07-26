# -*- coding: utf-8 -*-

"""
--------------
Algorithme alzheimerien de résolution des tours de Hanoï.
Réchèr. 2017. Licence GNU ou CC-BY ou Art Libre (au choix).
--------------

Cet algo est appelé "alzheimerien", car chaque mouvement est déterminé uniquement à partir de
la situation actuelle (la position des disques sur les poteaux).
Les mouvements précédents ne sont pas enregistrés, et il n'y a pas de récursivité.

--------------
Méthode :
--------------
Il faut d'abord déterminer le nombre de "coupures" dans l'ordre des disques.
Lorsque deux disques de taille N-1 et N sont empilés sur un même poteau, il n'y a pas
de coupure entre eux. Lorsqu'ils sont sur deux poteaux différents, on compte une coupure.
De plus, lorsque le gros disque du bas n'est pas sur le poteau de fin, on compte également
une coupure.

Exemple :
Le disque 1 (le plus petit) est sur le poteau de départ.
Les disques 2 et 3 sont sur le poteau intermédiaire.
Le disque 4 (le plus gros) est sur le poteau de départ.

    |           |           |
    |           |           |
    |           |           |
   +++        -----         |
---------    +++++++        |
.................................

On compte les coupures en partant du plus gros disque vers le plus petit
(mais on aurait pu compter dans l'autre sens).

 - Le 4 n'est pas sur le poteau de fin. +1 coupure
 - Le 4 et le 3 ne sont pas sur le même poteau. +1 coupure
 - Le 3 et le 2 sont sur le même poteau. OK
 - Le 2 et le 1 ne sont pas sur le même poteau. +1 coupure

Total : 3 coupures.

 * Si le nombre de coupures est impair, il faut déplacer le disque 1 (le petit).
   Pour déterminer son poteau de destination :
    - Si le nombre total de disque est pair, le petit disque doit se déplacer vers l'avant :
      poteau de départ -> poteau intermédiaire -> poteau de fin -> poteau de départ -> etc.
    - Si le nombre total de disque est impair, il doit se déplacer vers l'arrière :
      poteau de fin -> poteau intermédiaire -> poteau de départ -> poteau de fin -> etc.

 * Si le nombre de coupures est pair, il faut déplacer un disque autre que le petit disque.
   Dans ce cas, il n'y a toujours qu'un seul mouvement possible.
    - Parmi les deux poteaux ne contenant pas le petit disque, l'un d'eux est vide.
      Il faut alors déplacer un disque du poteau non vide vers le poteau vide.
    - Parmi les deux poteaux ne contenant pas le petit disque, aucun n'est vide.
      Il faut prendre le plus petit disque parmi ces deux poteaux,
      et le déplacer vers l'autre.

Lorsque le nombre de coupures est 0, le jeu est terminé. Tous les disques sont
sur le poteau de fin, dans le bon ordre.

Il faudrait une vraie démonstration mathématique pour prouver que cet algo fonctionne, mais je ne
sais pas la faire. Ça semble fonctionner quel que soit le nombre de disques.

--------------
Vocabulaire (pour le nommage des variables et des objets) :
--------------

chip : un disque posé sur l'un des poteaux du jeu.
size : taille d'un disque. Elle varie de 1 jusqu'au nombre total de disque dans le jeu.
tiny_chip : le plus petit disque (avec une taille de 1).
mast : poteau, mât, l'une des tours de Hanoï.

mast_start : le poteau de départ, celui sur lequel tous les disques sont placés au début du jeu.
mast_interm : le poteau intermédiaire.
mast_end : le poteau de fin, celui sur lequel tous les disques doivent se trouver à la fin du jeu.

mast_source : le poteau de source, pour le coup à jouer en cours. (On y prend un disque).
mast_dest : le poteau de destination, pour le coup à jouer en cours. (On y pose le disque pris).

move, turn : un mouvement = un coup = un déplacement d'un disque d'un poteau vers un autre.
gap : une coupure dans la disposition des disques (voir plus haut).
"""

from enum import Enum

# Les différentes valeurs possibles pour un type de mouvement.
Movement = Enum('Movement', (
    'OTHER_CHIP', # on doit bouger un disque autre que le plus petit disque
    'TINY_CHIP_FORWARD', # on doit bouger le plus petit disque, vers l'avant
    'TINY_CHIP_BACKWARD', # on doit bouger le plus petit disque, vers l'arrière
))

# Les différents valeurs possibles pour un type de poteau
MastType = Enum('Mast', (
 'START', # le poteau de départ
 'INTERM', # le poteau intermédiaire
 'END', # le poteau de fin
))


# --- Les classes pour l'algo en lui-même. ---

class Chip():
    """ Un disque du jeu. """

    def __init__(self, size):
        """
        :param size: Un nombre entier strictement positif.
        """
        self.size = size


class Mast():
    """ Un poteau du jeu, n'importe lequel des trois. """

    def __init__(self, mast_type):
        """
        :param mast_type: Le type du poteau. Une valeur de type MastType.*
        """
        # Liste des disques empilés sur le poteau. Ne contient que des objets de classe Chip.
        # L'élément d'indice 0 est le disque tout en bas. L'élément d'indice 1 est le disque
        # empilé dessus, etc. Le nombre de disque sur le poteau peut varier.
        self._chips = []
        # La variable contenant le type de mât n'est pas utile pour l'algo en lui-même.
        # Elle sert juste pour logger la description des coups joués.
        # (voir la classe TurnDisplayer).
        self.mast_type = mast_type

    def get_nb_chips(self):
        """
        :return: nombre entier positif ou nul. Nombre de Chips sur le poteau.
        """
        return len(self._chips)

    def get_max_size_chips(self):
        """
        :return: nombre entier positif ou nul. Size du plus grand Chip sur le poteau.
        Si le poteau n'a aucune Chip, la fonction renvoie 0.
        (Le plus logique aurait été de renvoyer None, mais c'est plus simple pour le code
        extérieur de renvoyer 0).
        """
        if self._chips:
            # Il y a au moins un disque. On renvoie le max.
            return max([ chip.size for chip in self._chips ])
        else:
            # Pas de disque sur ce poteau.
            return 0

    def get_top_chip(self):
        """
        Retourne le disque placé en haut du poteau.
        C'est à dire, celui qui est accessible et qu'on peut prendre pour déplacer ailleurs.
        :return: un objet Chip, ou None si pas de disque sur le poteau.
        """
        if self._chips:
            # Il y a au moins un disque. On renvoie le dernier élément de la liste,
            # c'est à dire le disque le plus haut sur le poteau.
            return self._chips[-1]
        else:
            # Pas de disque sur ce poteau.
            return None

    def get_chip(self, index_floor):
        """
        Retourne un disque placé à un certain étage de la tour.
        :param index_floor: Entier positif ou nul, indiquant l'étage du disque à récupérer.
        (Étage 0 = tout en bas).
        :return: un objet Chip, ou None si les disques ne vont pas jusqu'à l'étage demandé.
        """
        if index_floor < len(self._chips):
            # Il y a un disque à l'étage demandé. On le renvoie
            return self._chips[index_floor]
        else:
            # Pas de disque à l'étage demandé. (Pas assez de disque sur le poteau).
            return None

    def pop_chip(self):
        """
        Enlève le disque placé en haut du poteau, et le retourne.
        :return: un objet Chip.
        Lève une exception si le poteau n'a aucun disque.
        """
        if self._chips:
            # Il y a au moins un disque sur ce poteau.
            # On enlève le dernier élément de la liste (le disque du haut), et on le renvoie.
            return self._chips.pop()
        else:
            # Pas de disque sur ce poteau.
            raise Exception("Illegal move. Poteau vide : %s" % self.mast_type)

    def add_chip(self, chip_to_add):
        """
        Ajoute un nouveau disque en haut du poteau. La taille des disques est contrôlée.
        :param chip_to_add: un objet Chip.
        Lève une exception si le disque qu'on tente d'ajouter est plus grand
        que le disque se trouvant actuellement en haut du poteau.
        """

        # Récupération du disque actuellement en haut du poteau.
        top_chip = self.get_top_chip()
        if top_chip is None:
            # Pas de disque sur le poteau. On peut ajouter le nouveau disque sans problème.
            self._chips.append(chip_to_add)
        elif top_chip.size > chip_to_add.size:
            # Il y a des disques sur le poteau. Le disque à ajouter à une taille plus petite
            # que celui qui est en haut du poteau. On peut donc l'ajouter.
            self._chips.append(chip_to_add)
        else:
            # Le disque a ajouter à une taille plus grande que celui en haut du poteau.
            # On lève une exception.
            exc_msg = "Illegal move. Poteau: %s. Chip: %s. chip to add: %s."
            exc_data = (self.mast_type, top_chip.size, chip_to_add.size)
            raise Exception(exc_msg % exc_data)


class HanoiGame():
    """ Le jeu des tour de Hanoï. Avec les trois poteaux et les disques. """

    def __init__(self, nbr_chip):
        """
        :param nbr_chip: Entier strictement positif. Nombre total de disques dans le jeu.
        """

        self.nbr_chip = nbr_chip
        # Création des trois poteaux du jeu (départ, intermédiaire et arrivée)
        self.mast_start = Mast(MastType.START)
        self.mast_interm = Mast(MastType.INTERM)
        self.mast_end = Mast(MastType.END)

        # Création et empilement des disques sur le poteau de départ.
        # On crée d'abord le disque le plus grand (taille = nbr_chip) et on le met sur le poteau.
        # Puis on crée un disque un peu plus petit et on l'empile, etc.
        # Jusqu'au plus petit disque (taille de 1), qui se retrouve tout en haut.
        for chip_size in range(self.nbr_chip, 0, -1):
            chip = Chip(chip_size)
            self.mast_start.add_chip(chip)

    def move_chip(self, mast_source, mast_dest):
        """
        Déplace un disque du poteau mast_source, vers le poteau mast_dest.
        :param mast_source: un objet Mast, parmi self.mast_start, self.mast_interm, self.mast_end.
        :param mast_dest: même chose.
        La fonction n'effectue aucun contrôle sur la possibilité ou la légalité du mouvement.
        Ce sont les objets Mast qui s'en chargent (en levant des exceptions).
        """
        # Récupération du disque se trouvant tout en haut du poteau source.
        # Et en même temps, suppression de ce disque du poteau source.
        chip_to_move = mast_source.pop_chip()
        # Placement du disque récupéré, sur le poteau de destination.
        mast_dest.add_chip(chip_to_move)

    def get_masts(self):
        """
        :return: un tuple de 3 éléments : les trois objets Mast de la classe.
        """
        return (self.mast_start, self.mast_interm, self.mast_end)


class HanoiSolver():
    """
    Résolveur du jeu des tours de Hanoï. Cette classe analyse la situation présente
    d'un objet hanoi_game et en déduit le prochain coup à jouer (le poteau de source
    et le poteau de destination).
    La classe ne retient aucune information entre deux déductions de coup.
    """

    def __init__(self, hanoi_game):
        """
        :param hanoi_game: Objet de type HanoiGame.
        La classe HanoiSolver ne modifie rien dans hanoi_game.
        Elle se contente de récupérer des infos, en lecture seule.
        """
        self.hanoi_game = hanoi_game

    def _find_chip_in_mast_cursors(self, chip_size_to_find, mast_cursors):
        """
        Retrouve un disque spécifique, parmi les 3 poteaux, à des étages spécifiques.
        (Donc on ne cherche que parmi 3 positions différentes, une par poteau).
        :param chip_size_to_find: Nombre entier strictement positif. Taille du chip recherché
        :param mast_cursors: liste de tuples de deux éléments :
         - un objet Mast,
         - un curseur (entier positif), indiquant l'étage du poteau où on recherche le disque.
        :return: un objet Mast, sur lequel se trouve le disque de taille recherchée,
        à l'étage indiqué par son curseur.
        Lève une exception si le disque est introuvable.
        """
        # On cherche le disque dans la liste des 3 poteaux.
        for mast_cursor in mast_cursors:

            mast, cursor = mast_cursor
            # Pour chaque poteau, on regarde uniquement le disque pointé par son curseur.
            chip = mast.get_chip(cursor)

            if chip is not None and chip.size == chip_size_to_find:
                # Pour le poteau en cours, et pour le curseur en cours, un disque est présent.
                return mast_cursor

        raise Exception("Disque introuvable parmi les 3 positions possibles.")

    def _count_gaps(self):
        """
        Analyse la la situation de jeu de self.hanoi_game et compte le nombre de coupures
        dans l'ordre des disques.
        :return: Nombre entier positif ou nul.
        """

        mast_start, mast_interm, mast_end = self.hanoi_game.get_masts()

        # On compte le nombre de coupures en commençant par le disque le plus grand,
        # et par le bas des poteaux. On remonte progressivement dans les étages des 3 poteaux.
        # Création de 3 listes de 2 éléments chacune :
        #  - un objet Mast,
        #  - un curseur sur l'étage en cours.
        # On commence à l'étage le plus bas (curseur = 0).
        mast_cursors = (
            [mast_start, 0],
            [mast_interm, 0],
            [mast_end, 0],
        )

        # Nombre de coupures actuellement comptées
        nb_gaps = 0
        # référence vers le poteau sur lequel se trouve le disque précédent.
        # On l'initialise sur le poteau de fin, car on considère qu'il y a une coupure
        # si le plus grand disque est à un autre endroit que le poteau de fin.
        # (En fait, c'est comme si y'avait un disque de taille nb_chip+1 sur le poteau de fin,
        # qui ne bouge jamais).
        previous_mast = self.hanoi_game.mast_end

        # chip_size_to_find indique la taille du disque qu'on cherche actuellement.
        # On va du plus grand disque (taille=nbr_chip) au plus petit (taille=1)
        for chip_size_to_find in range(self.hanoi_game.nbr_chip, 0, -1):

            mast_cursor = self._find_chip_in_mast_cursors(
                chip_size_to_find,
                mast_cursors)

            # On a trouvé le poteau et le curseur sur lequel se trouve le disque
            # ayant la taille recherchée.
            # On monte d'un étage le curseur de ce poteau.
            mast_cursor[1] += 1
            # On vérifie si le disque précédent et le disque qu'on vient de trouver
            # sont sur le même poteau.
            if mast_cursor[0] != previous_mast:
                # Pas le même poteau : une coupure de plus, et on change le poteau en cours.
                nb_gaps += 1
                previous_mast = mast_cursor[0]

        return nb_gaps

    def _determine_tiny_chip_movement(self, move_type):
        """
        Détermine le prochain coup à jouer, dans le cas où on doit déplacer le petit disque.
        :param move_type: valeur Movement.TINY_CHIP_FORWARD ou Movement.TINY_CHIP_BACKWARD.
        move_type ne doit pas valoir Movement.OTHER_CHIP, car ça n'aurait aucun sens.
        La fonction lève une exception si jamais le petit disque ne se trouve pas en haut de l'un
        des 3 poteaux de self.hanoi_game. (Ce cas n'est jamais censé arriver).

        :return: un tuple de 2 éléments. Deux références vers des objets Mast :
         - mast_source : le poteau de source, pour le prochain mouvement à jouer,
         - mast_dest : le poteau de destination.
        """

        mast_start, mast_interm, mast_end = self.hanoi_game.get_masts()

        # Définition du dictionnaire permettant de connaître le poteau de destination en fonction
        # du poteau de source.
        if move_type == Movement.TINY_CHIP_FORWARD:
            # Le petit disque doit bouger vers l'avant. Le dictionnaire contient donc la config
            # de mouvement suivante :
            # poteau de départ -> poteau intermédiaire -> poteau de fin -> poteau de départ.
            dict_tiny_chip_movement = {
                mast_start: mast_interm,
                mast_interm: mast_end,
                mast_end: mast_start,
            }
        else:
            # Le petit disque doit bouger vers l'arrière. Le dictionnaire contient donc la config
            # de mouvement suivante :
            # poteau de fin -> poteau intermédiaire -> poteau de départ -> poteau de fin.
            dict_tiny_chip_movement = {
                mast_start: mast_end,
                mast_interm: mast_start,
                mast_end: mast_interm,
            }

        # On recherche le petit disque, parmi les disques en haut de chaque poteau.
        for mast in (mast_start, mast_interm, mast_end):
            chip = mast.get_top_chip()
            if chip is not None and chip.size == 1:
                # On a trouvé le petit disque en haut du poteau en cours.
                # Donc ce poteau est le poteau de source.
                # (vu que c'est le petit disque qu'on doit bouger, haha)
                mast_source = mast
                # Détermination du potau de destination en fonction du poteau de source,
                # et du dictionnaire de config des mouvements.
                mast_dest = dict_tiny_chip_movement[mast]
                return mast_source, mast_dest

        # Après avoir regardé le haut de tous les poteaux, le petit disque est introuvable.
        # On lève une exception. (Ça ne devrait pas arriver)
        raise Exception("Fail. Tiny Chip introuvable.")

    def _index_none_or_highest(self, val_0, val_1):
        """
        Renvoie l'index (0 ou 1) du paramètre qui vaut None parmi val_0 et val_1.
        Si pas de None, renvoie l'index (0 ou 1) de la valeur la plus grande.
        Lève une exception dans tous les autres cas.
        :param val_0: None ou nombre entier.
        :param val_1: None ou nombre entier.
        :return: Nombre entier. 0 ou 1.
        """
        if val_0 is None and val_1 is None:
            raise Exception("Fail. Deux valeurs None.")
        if val_0 is None:
            return 0
        if val_1 is None:
            return 1
        if val_0 > val_1:
            return 0
        if val_0 < val_1:
            return 1
        raise Exception("Fail. Deux valeurs égales.")

    def _determine_other_chip_movement(self):
        """
        Détermine le prochain coup à jouer, dans le cas où on doit déplacer un disque
        autre que le petit disque.
        :return: un tuple de 2 éléments. Deux références vers des objets Mast :
         - mast_source : le poteau de source, pour le prochain mouvement à jouer,
         - mast_dest : le poteau de destination.
        """

        masts = self.hanoi_game.get_masts()

        # Cette liste va contenir 2 éléments, correspondant à 2 poteaux du jeu.
        # Le poteau qu'on éliminera sera celui contenant le petit disque.
        # Chaque élément de cette liste est un tuple de 2 sous-éléments :
        #  - Référence vers le poteau en question.
        #  - Soit une valeur entière (taille du disque se trouvant tout en haut du poteau),
        #    soit None (le poteau ne contient pas de disque)
        masts_with_size = []

        # Initialisation de masts_with_size
        for mast in masts:
            chip = mast.get_top_chip()
            if chip is None:
                # Le poteau en cours ne contient pas de disque. On l'ajoute à masts_with_size,
                # En indiquant None dans le deuxième sous-élément
                masts_with_size.append((mast, None))
            elif chip.size != 1:
                # Le poteau en cours contient un/des disques, et le disque du haut n'est pas
                # le petit disque. On l'ajoute à masts_with_size,
                # en indiquant la taille du disque dans le deuxième sous-élément.
                masts_with_size.append((mast, chip.size))
            # Dans le troisième cas : le poteau en cours contient le petit disque tout en haut,
            # on ne fait rien.

        # On doit maintenant déterminer le poteau source et le poteau de destination,
        # parmi les 2 éléments de cette liste.
        # Si l'un des deux poteau n'a pas de disque (le deuxième sous-elem vaut None),
        # alors c'est forcément le poteau de destination.
        # Si les deux poteaux ont des disques, le poteau de destination est celui
        # ayant le plus grand disque tout en haut. (le duexième sous-elem est le plus grand).
        index_mast_dest = self._index_none_or_highest(
            masts_with_size[0][1],
            masts_with_size[1][1])

        # Et le poteau source, c'est celui qui n'est pas le poteau de destination. Ha ha ha.
        dict_other_index = { 0:1, 1:0 }
        index_mast_source = dict_other_index[index_mast_dest]

        mast_source = masts_with_size[index_mast_source][0]
        mast_dest = masts_with_size[index_mast_dest][0]
        return mast_source, mast_dest

    def determine_next_movement(self):
        """
        Détermine le prochain coup à jouer, en fonction de la situation de jeu
        définie dans self.hanoi_game.
        :return: Soit None, si le jeu est fini et que tous les disques sont sur le poteau de fin,
        soit un tuple de 4 éléments :
         - nb_gaps. Entier positif. Nombre de coupures comptées dans le jeu.
         - move_type. Type de mouvement à faire. Une valeur de type Movement.*.
         - mast_source : Objet Mast. le poteau de source, pour le prochain mouvement à jouer
         - mast_dest : Objet Mast. le poteau de destination, pour le prochain mouvement à jouer.
        """

        #on compte le nombre de coupures
        nb_gaps = self._count_gaps()
        if nb_gaps == 0:
            # 0 coupures. Tout est bien rangé, le jeu est fini, on renvoie None.
            return None

        if nb_gaps & 1 == 0:
            # Le nombre de coupure est pair. Il faut déplacer un disque autre que le petit disque.
            move_type = Movement.OTHER_CHIP
            # Détermination des poteaux de source et destination.
            mast_source, mast_dest = self._determine_other_chip_movement()
        else:
            # Le nombre de coupure est impair. Il faut déplacer le petit disque.
            # Le sens de déplacement de ce disque dépend de la parité du nombre
            # total de disque dans le jeu.
            # Si c'est pair : on le déplace vers l'avant.
            # Si c'est impair : vers l'arrière.
            move_type_from_parity = {
                0:Movement.TINY_CHIP_FORWARD,
                1:Movement.TINY_CHIP_BACKWARD,
            }
            move_type = move_type_from_parity[self.hanoi_game.nbr_chip & 1]
            # Détermination des poteaux de source et de destination.
            mast_source, mast_dest = self._determine_tiny_chip_movement(move_type)

        return (nb_gaps, move_type, mast_source, mast_dest)


# --- Les classes de log/affichage/vue. ---

class MastsDisplayer():
    """
    Affiche sur la sortie standard une situation de jeu des tours de Hanoï.
    Cette classe est assez permissive. On pourrait avoir autant de poteaux qu'on veut,
    plusieurs disques de la même taille, des tailles de disques manquantes, etc.

    Méthode :
     - Les poteaux sont affichés les uns à côté des autres.
     - La hauteur des poteaux dépend du nombre total de disques.
     - La largeur des poteaux dépend de la taille du plus grand disque.
     - Pour afficher un disque de taille X, on affiche X caractères à gauche du poteau, un caractère
       au milieu, et encore X caractère à droite.
       Donc : taille en caractère = 2 * taille du disque + 1
     - Pour plus de clarté, les disques de taille paire et impaire
       ne sont pas affichés avec le même caractère.
     - Après avoir affiché tous les étages de tous les poteaux, on affiche une dernière ligne,
       représentant le sol.
    """

    # Marge de hauteur. Hauteur totale d'un poteau = nombre de disque + cette marge.
    HEIGHT_MAST_MARGIN = 1
    # Nombre d'espace entre 2 poteaux.
    INTERV_SIZE = 3
    # On en déduit la chaîne de caractère à afficher entre les poteaux.
    STR_SPACE_BETWEEN = ' ' * INTERV_SIZE
    # Caractère utilisé pour afficher un étage du poteau sans disque.
    CHAR_MAST = '|'
    # Caractère pour le sol.
    CHAR_GROUND = '.'
    # Caractère pour les disques de taille impaire
    CHAR_CHIP_EVEN = '-'
    # Caractère pour les disques de taille paire
    CHAR_CHIP_ODD = '+'
    # Correspondance entre la parité et le caractère.
    DICT_CHAR_CHIP = { 0: CHAR_CHIP_EVEN, 1: CHAR_CHIP_ODD }

    def __init__(self, masts):
        """
        Constructeur.
        :param masts: liste d'objets Mast, les poteaux à afficher.
        L'ordre d'affichage correspond à l'ordre dans la liste.
        """
        self.masts = masts
        self._determine_dimensions()

    def _determine_dimensions(self):
        """
        À exécuter au début, avant de faire des affichages.
        Permet d'initialiser les valeurs internes : dimension des poteaux,
        taille d'une ligne complète, etc.
        """

        # Nombre total de disque dans le jeu.
        self.nb_total_chips = sum(( mast.get_nb_chips() for mast in self.masts ))
        # Taille du plus gros disque du jeu.
        self.size_max_chip = max(( mast.get_max_size_chips() for mast in self.masts ))
        # Hauteur des poteaux
        self.mast_height = self.nb_total_chips + self.HEIGHT_MAST_MARGIN
        # Largeur des poteaux. Tous les poteaux doivent pouvoir afficher
        # le plus gros disque. Donc largeur = la taille en caractère du plus gros disque.
        self.mast_width = self.size_max_chip*2 + 1
        # Nombre de poteaux
        nb_masts = len(self.masts)
        # Largeur totale d'une ligne affichant tous les poteaux.
        # Il faut tenir compte du nombre de poteaux, de leur largeurs,
        # du nombre d'intervalle entre les poteaux, et de la largeur de ces intervaux.
        # (Je dis intervaux et je vous emmerde).
        total_width = self.mast_width*nb_masts + self.INTERV_SIZE*(nb_masts-1)
        # Chaîne de caracètre à afficher pour l'étage d'un poteau sans disque.
        # Il faut des espaces, avec au milieu le caractère spécifique du poteau sans disque.
        self.str_no_chip = ''.join((
            ' ' * self.size_max_chip,
            self.CHAR_MAST,
            ' ' * self.size_max_chip,
        ))
        # Chaîne de caractère à afficher pour le sol. C'est la largeur totale d'une ligne,
        # avec le caractère idoinement utilisé pour le sol. Ha ha.
        self.str_ground = self.CHAR_GROUND * total_width

    def _get_str_floor(self, chip):
        """
        Renvoie une chaîne de caractère représentant un étage (avec ou sans disque).
        La chaîne renvoyée a une taille fixe, égale à self.mast_width.
        il y a éventuellement des espaces de part et d'autres du disque affiché,
        afin de la compléter pour atteindre la taille fixe.
        :param chip: soit None (absence de disque), soit un objet Chip.
        """

        if chip is None:
            # pas de disque. On renvoie directement la chaîne de caractère correspondant à
            # un étage de poteau sans disque.
            return self.str_no_chip
        else:
            # Y'a un disque. On calcule sa largeur en caractère
            chip_str_width = chip.size*2 + 1
            # Calcul du nombre d'espace à écrire de part et d'autre du disque, pour compléter.
            nb_spaces = (self.mast_width - chip_str_width) // 2
            str_space = ' ' * nb_spaces
            # Caractère à utiliser pour afficher le disque (selon la parité de sa taille).
            chr_chip = self.DICT_CHAR_CHIP[chip.size & 1]
            str_chip = chr_chip * chip_str_width
            # On colle tout : les espaces, le disque, encore les espaces.
            return ''.join((str_space, str_chip, str_space))

    def display(self):
        """
        Affiche les étages des poteaux, côte à côte, avec leurs disques.
        Le texte affiché est envoyé sur la sortie standard.
        """

        # On parcourt tous les étages, depuis le haut (self.mast_height-1) vers le bas (0).
        for index_floor in range(self.mast_height-1, -1, -1):
            # Pour chaque poteau, récupération de la chaîne de caractère de l'étage concerné.
            str_floor_masts = (
                self._get_str_floor(mast.get_chip(index_floor))
                for mast in self.masts
            )
            # Concaténation de ces chaînes de caractère,
            # avec les espaces d'intervaux entre chaque poteau.
            str_floor_complete = self.STR_SPACE_BETWEEN.join(str_floor_masts)
            # Ca fait une grande ligne, affichant un étage pour tous les poteaux.
            print(str_floor_complete)

        # Affichage de la dernière ligne représentant le sol.
        print(self.str_ground)
        # Et un p'tit saut de ligne pour la forme.
        print('')


class TurnDisplayer():
    """
    Affiche sur la sortie standard la description d'un coup joué,
    avec quelques vagues explications indiquant comment le coup a été déduit.
    """

    # Correspondance {type de mouvement} -> {description du type de mouvement}
    DICT_STR_FROM_MOVEMENT_TYPE = {
        Movement.OTHER_CHIP: "Un disque autre que le petit disque",
        Movement.TINY_CHIP_FORWARD: "Le petit disque, vers l'avant",
        Movement.TINY_CHIP_BACKWARD: "Le petit disque, vers l'arriere",
    }

    # Dictionnaire de correspondance {type de poteau} -> {description du type de poteau}
    DICT_STR_FROM_MAST_TYPE = {
        MastType.START: "poteau de depart (a gauche)",
        MastType.INTERM: "poteau intermediaire (au milieu)",
        MastType.END: "poteau de fin (a droite)",
    }

    # Pas de fonction constructeur. Pas besoin.

    def display(self, nb_gaps, move_type, mast_source, mast_dest):
        """
        Envoie sur la sortie standard la description d'un coup joué.
        Les paramètres sont constitués des infos renvoyées
        par la fonction hanoiSolver.determine_next_movement
        :param nb_gaps: int>0. Nombre de coupures comptées dans le jeu.
        :param move_type: Valeur de type Movement.*. Type de mouvement effectué.
        :param mast_source: Objet Mast. Le poteau de source.
        :param mast_dest: Objet Mast. Le poteau de destination.
        """

        labels_and_values = (
            (
                "Nombre de coupures dans l'ordre des disques",
                nb_gaps
            ), (
                "Type de mouvement",
                self.DICT_STR_FROM_MOVEMENT_TYPE[move_type]
            ), (
                # Ajout d'espace pour être au même niveau que la valeur 'poteau de destination'.
                "Poteau source        ",
                self.DICT_STR_FROM_MAST_TYPE[mast_source.mast_type]
            ), (
                "Poteau de destination",
                self.DICT_STR_FROM_MAST_TYPE[mast_dest.mast_type]
            )
        )

        for label, value in labels_and_values:
            print('%s : %s' % (label, value))


# --- Les fonctions qui coordonnent tout l'ensemble. ---

def solve_full_game(nb_chip):
    """
    Résout entièrement un jeu de tour de Hanoï, tout en affichant
    la succession des coups joués, et la situation de jeu entre chaque coup.
    :param nb_chip: int > 0. Nombre de disques présents initialement sur le poteau de départ.
    """

    # Création du jeu, avec les poteaux et les disques dessus.
    hanoi_game = HanoiGame(nb_chip)
    # Initialisation des classes de vue, qui afficheront la situation du jeu et la
    # description des coups joués.
    masts = hanoi_game.get_masts()
    masts_displayer = MastsDisplayer(masts)
    turn_displayer = TurnDisplayer()
    # Booléen indiquant si le jeu est fini ou pas.
    game_in_progress = True

    while game_in_progress:

        # On affiche la situation de jeu actuel. Les 3 poteaux, avec la disposition des disques.
        masts_displayer.display()
        # Création de la classe résolvant le jeu.
        hanoi_solver = HanoiSolver(hanoi_game)
        # Utilisation de cette classe pour déterminer le prochain coup à jouer,
        # en se basant uniquement sur la situation de jeu actuelle.
        movement_info = hanoi_solver.determine_next_movement()

        if movement_info is None:
            # Pas d'info valide concernant le prochain coup à jouer.
            # Ca veut dire que le jeu est fini, les disques sont bien rangés sur le poteau de fin.
            print("C'est fini !!")
            # On peut partir de la boucle.
            game_in_progress = False
        else:
            # Les infos concernant le prochain coup à jouer sont valides. On les décompose.
            (nb_gaps, move_type, mast_source, mast_dest) = movement_info
            # Affichage de la description du coup à jouer.
            turn_displayer.display(nb_gaps, move_type, mast_source, mast_dest)
            # On effectue le déplacement d'un disque, selon ce qu'a déduit le hanoi_solver.
            hanoi_game.move_chip(mast_source, mast_dest)

        # On détruit le hanoi_solver. On en recrééra un autre à la prochaine itération.
        # C'est inutile, mais ça sert à prouver qu'on ne retient aucune info entre deux coups.
        del hanoi_solver


def main():
    """
    Programme principal. Captain Obvious, oui.
    Pour couvrir le plus de cas possible, il faut résoudre un jeu avec un nombre de disque pair,
    et un autre avec un nombre impair. Ces deux cas sont pas tout à fait pareil,
    le mouvement du petit disque n'est pas le même.
    """

    print('=' * 79)
    print('Les tours de Hanoi avec 3 disques')
    print('=' * 79)
    solve_full_game(3)

    print('=' * 79)
    print('Les tours de Hanoi avec 4 disques')
    print('=' * 79)
    solve_full_game(4)


if __name__ == '__main__':
    main()
