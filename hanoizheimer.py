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
    Il reste à déterminer où déplacer ce petit disque.
    Si le nombre total de disque est pair, le petit disque doit se déplacer vers l'avant :
    poteau de départ -> poteau intermédiaire -> poteau de fin -> poteau de départ -> etc.
    Si le nombre total de disque est impair, il doit se déplacer vers l'arrière :
    poteau de fin -> poteau intermédiaire -> poteau de départ -> poteau de fin -> etc.

 * Si le nombre de coupures est pair, il faut déplacer un disque autre que le petit disque.
    Dans ce cas, il n'y a toujours qu'un seul mouvement possible.
     - Parmi les deux poteaux ne contenant pas le petit disque, l'un d'eux est vide.
        Il faut alors déplacer un disque du poteau non vide vers le poteau vide.
     - Parmi les deux poteaux ne contenant pas le petit disque, aucun n'est vide.
        Il faut prendre le plus petit disque parmi les deux poteaux,
        et le déplacer sur l'autre poteau.

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
mast : poteau, mât, l'une des tour de Hanoï.

mast_start : le poteau de départ, celui sur lequel tous les disques sont placés au début du jeu.
mast_interm : le poteau intermédiaire.
mast_end : le poteau de fin, celui sur lequel tous les disques doivent se trouver à la fin du jeu.

mast_source : le poteau de source, pour le coup à jouer en cours.
              (Celui à partir duquel on prend un disque)
mast_dest : le poteau de destination, pour le coup à jouer en cours.
            (Celui sur lequel on pose le disque qu'on a pris sur le mast_source)

move, turn : un mouvement = un coup = déplacement d'un disque d'un poteau vers un autre.
gap : une coupure dans l'ordre des disques
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
        TODO bla.
        """
        # On cherche le disque dans la liste des 3 poteaux.
        for mast_cursor in mast_cursors:

            mast, cursor = mast_cursor
            # Pour chaque poteau, on regarde uniquement le disque pointé par son curseur.
            chip = mast.get_chip(cursor)

            if chip is not None and chip.size == chip_size_to_find:
                # Pour le poteau en cours, et pour le curseur en cours, un disque est présent.
                return mast_cursor

        raise Exception("TODO. blabla not supposed to happen.")

    def _count_gaps(self):
        """
        Analyse la la situation de jeu de self.hanoi_game et compte le nombre de coupures
        dans l'ordre des disques.
        :return: Nombre entier positif ou nul.
        """

        # On compte le nombre de coupures en commençant par le disque le plus grand,
        # et par le bas des poteaux. On remonte progressivement dans les étages des 3 poteaux.
        # Création de plusieurs listes de 2 éléments chacune :
        #  - un objet Mast,
        #  - un curseur sur l'étage en cours.
        # On commence à l'étage le plus bas (curseur = 0).
        mast_cursors = (
            [self.hanoi_game.mast_start, 0],
            [self.hanoi_game.mast_interm, 0],
            [self.hanoi_game.mast_end, 0],
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

    def _determineTinyChipMovement(self, moveType):
        """ détermine le prochain coup à jouer, dans le cas où on doit déplacer le petit disque.
        moveType doit valoir Movement.TINY_CHIP_FORWARD, ou Movement.TINY_CHIP_BACKWARD.
        moveType ne doit pas valoir Movement.OTHER_CHIP, parce que ça n'aurait aucun sens.
        La fonction fait tout planter si jamais le petit disque ne se trouve pas en haut de l'un
        des 3 poteaux de self.hanoi_game. (Mais ce cas débile n'est jamais censé arriver)

        La fonction renvoie un tuple de 2 éléments : 2 référence vers des objets Mast
         - Mast_source : le poteau de source, pour le prochain mouvement à jouer
         - Mast_dest : le poteau de destination, pour le prochain mouvement à jouer. """

        # Définition du dictionnaire permettant de connaître le poteau de destination en fonction
        # du poteau de source.
        if moveType == Movement.TINY_CHIP_FORWARD:
            # Le petit disque doit bouger vers l'avant. Le dictionnaire contient donc la config
            # de mouvement suivante :
            # poteau de départ -> poteau intermédiaire -> poteau de fin -> poteau de départ.
            dictTinyChipMovement = {
                self.hanoi_game.mast_start: self.hanoi_game.mast_interm,
                self.hanoi_game.mast_interm: self.hanoi_game.mast_end,
                self.hanoi_game.mast_end: self.hanoi_game.mast_start,
            }
        else:
            # Le petit disque doit bouger vers l'arrière. Le dictionnaire contient donc la config
            # de mouvement suivante :
            # poteau de fin -> poteau intermédiaire -> poteau de départ -> poteau de fin.
            dictTinyChipMovement = {
                self.hanoi_game.mast_start: self.hanoi_game.mast_end,
                self.hanoi_game.mast_interm: self.hanoi_game.mast_start,
                self.hanoi_game.mast_end: self.hanoi_game.mast_interm,
            }

        listMast = (self.hanoi_game.mast_start,
                    self.hanoi_game.mast_interm,
                    self.hanoi_game.mast_end)

        # On recherche le petit disque, en vérifiant le disque qui se trouve
        # tout en haut de chaque poteau.
        for mast in listMast:
            chip = mast.get_top_chip()
            if chip is not None and chip.size == 1:
                # On a trouvé le petit disque en haut du poteau en cours.
                # Donc ce poteau est le poteau de source.
                # (vu que c'est le petit disque qu'on doit bouger, haha)
                mast_source = mast
                # Détermination du potau de destination en fonction du poteau de source,
                # et du dictionnaire de config des mouvements.
                mast_dest = dictTinyChipMovement[mast]
                return mast_source, mast_dest

        # Après avoir regardé le haut de tous les poteaux, le petit disque est introuvable.
        # On fait tout planter. (Ca arrive jamais)
        print("fail. tiny Chip introuvable")
        assert False

    def _determineOtherChipMovement(self):
        """ détermine le prochain coup à jouer, dans le cas où on doit déplacer un disque
        autre que le petit disque.
        La fonction renvoie un tuple de 2 éléments : 2 référence vers des objets Mast
         - Mast_source : le poteau de source, pour le prochain mouvement à jouer
         - Mast_dest : le poteau de destination, pour le prochain mouvement à jouer. """

        listMast = (self.hanoi_game.mast_start,
                    self.hanoi_game.mast_interm,
                    self.hanoi_game.mast_end)

        # Cette liste va contenir 2 éléments, correspondant à 2 poteaux du jeu.
        # Le poteau qu'on éliminera sera celui contenant le petit disque.
        # Chaque élément de cette liste est un tuple de 2 sous-éléments :
        #  - Référence vers le poteau en question.
        #  - * Soit une valeur entière (taille du disque se trouvant tout en haut du poteau)
        #    * Soit la valeur None (le poteau ne contient pas de disque)
        listMastWithSize = []

        # on parcourt la liste des 3 poteaux, pour remplir listMastWithSize
        for mast in listMast:
            chip = mast.get_top_chip()
            if chip is None:
                # Le poteau en cours ne contient pas de disque. On l'ajoute à listMastWithSize,
                # En indiquant None dans le deuxième sous-élément
                listMastWithSize.append((mast, None))
            elif chip.size != 1:
                # Le poteau en cours contient un/des disques, et le disque du haut n'est pas
                # le petit disque. On l'ajoute à listMastWithSize,
                # en indiquant la taille du disque dans le deuxième sous-élément.
                listMastWithSize.append((mast, chip.size))
            # Lorsque le poteau en cours contient un/des disques, et que le disque du haut est
            # le petit disque, on ne fait rien.

        # Maintenant que listMastWithSize est remplie, on doit déterminer quel est le poteau
        # de source, et quelle est le poteau de destination, parmi les 2 éléments de cette liste.
        if listMastWithSize[0][1] is None:
            # Le 1er élément de listMastWithSize est un poteau sans disque.
            # Donc le poteau de source, c'est l'autre (le 2eme)
            mast_source = listMastWithSize[1][0]
            # et le poteau de destination, c'est celui-là. (le 1er)
            mast_dest = listMastWithSize[0][0]
        elif listMastWithSize[1][1] is None:
            # Le 2eme élément de listMastWithSize est un poteau sans disque.
            # Donc le poteau de source, c'est l'autre (le 1er)
            mast_source = listMastWithSize[0][0]
            # et le poteau de destination, c'est celui-là. (le 2eme)
            mast_dest = listMastWithSize[1][0]
        elif listMastWithSize[0][1] < listMastWithSize[1][1]:
            # Les deux poteaux contiennent des disques. Et le disque du haut du 1er poteau
            # est plus petit que le disque du haut du 2eme poteau.
            # Le poteau de source est celui avec le plus petit disque (le 1er)
            mast_source = listMastWithSize[0][0]
            # Le poteau de destination c'est l'autre (le 2eme)
            mast_dest = listMastWithSize[1][0]
        else:
            # Les deux poteaux contiennent des disques. Et le disque du haut du 1er poteau
            # est plus grand que le disque du haut du 2eme poteau.
            # Le poteau de source est celui avec le plus petit disque (le 2eme)
            mast_source = listMastWithSize[1][0]
            # Le poteau de destination c'est l'autre (le 1er)
            mast_dest = listMastWithSize[0][0]

        return mast_source, mast_dest

    def determineNextChipMovement(self):
        """ Détermine le prochain coup à jouer, en fonction de la situation de jeu
        définie dans self.hanoi_game.
        Valeur de retour :
         - Soit la valeur None. Dans ce cas, le jeu est déjà fini,
           et tous les disques sont correctement rangés sur le poteau de fin.
         - Soit un tuple de 4 éléments :
            * nb_gaps. Entier positif. Nombre de coupures comptées dans le jeu.
            * moveType. Type de mouvement à faire. Une valeur de type Movement.*.
            * Mast_source : le poteau de source, pour le prochain mouvement à jouer
            * Mast_dest : le poteau de destination, pour le prochain mouvement à jouer. """

        #on compte le nombre de coupures
        nb_gaps = self._count_gaps()
        if nb_gaps == 0:
            # 0 coupures. Tout est bien rangé, le jeu est fini, on renvoie None.
            return None

        if nb_gaps & 1 == 0:
            # Le nombre de coupure est pair. Il faut déplacer un disque autre que le petit disque.
            moveType = Movement.OTHER_CHIP
            # On peut déterminer immédiatement les poteaux de source et destination.
            mast_source, mast_dest = self._determineOtherChipMovement()
        else:
            # Le nombre de coupure est impair. Il faut déplacer le petit disque.
            # définition du dictionnaire indiquant le sens du mouvement du petit disque,
            # en fonction d'une parité. 0 : paire. 1 : impaire
            move_type_from_parity = {
                0:Movement.TINY_CHIP_FORWARD,
                1:Movement.TINY_CHIP_BACKWARD,
            }
            # Le sens du mouvement du petit disque se détermine en fonction de la parité
            # du nombre total de disque dans le jeu.
            moveType = move_type_from_parity[self.hanoi_game.nbr_chip & 1]
            # Détermination des poteaux de source et de destination, pour le petit disque.
            mast_source, mast_dest = self._determineTinyChipMovement(moveType)

        return (nb_gaps, moveType, mast_source, mast_dest)


# --- Les classes de log/affichage/vue. ---

class ListMastDisplayer():
    """ Classe affichant sur la sortie standard une situation de jeu des tours de Hanoï.
    Cette classe est assez permissive. On pourrait avoir autant de poteaux qu'on veut,
    et on pourrait avoir des disques avec des tailles comme on veut. (plusieurs disques de la
    même taille, des tailles de disques manquantes, ...). En vrai, tout cela n'arrive jamais,
    mais si on a envie, on pourrait l'afficher.

    Méthode :
     - Les poteaux sont affichées les uns à côté des autres.
     - La hauteur des poteaux dépend du nombre total de disque.
     - La largeur des poteaux dépend de la taille du plus grand disque présent dans le jeu.
     - Pour afficher un disque de taille X, on affiche X caractères à gauche du poteau, un caractère
       au milieu, pour le poteau lui-même, et encore X caractère à droite du poteau.
       Donc : taille en caractère = 2 * taille du disque + 1
     - Les disques de taille paire et impaire ne sont pas affichés avec le même caractère. C'est
       juste pour faire joli et un peu plus claire.
     - Après avoir affiché tous les étages de tous les poteaux, on affiche une dernière ligne,
       représentant le sol.

    Type MVC : Vue """

    # Marge de hauteur des poteaux. La hauteur des poteaux est égale au nombre total
    # de disque + la marge.
    HEIGHT_MAST_MARGIN = 1
    # Nombre d'espacement entre 2 poteaux.
    NB_SPACE_BETWEEN = 3
    # Chaîne de caractère à afficher entre les poteaux, donc.
    STR_SPACE_BETWEEN = " " * NB_SPACE_BETWEEN
    # Caractère utilisé pour afficher un étage du poteau, quand y'a pas de disque dessus.
    CHAR_MAST = "|"
    # Caractère pour afficher le sol.
    CHAR_GROUND = "."
    # Caractère pour afficher les disques dont la taille est impaire
    CHAR_CHIP_EVEN = "-"
    # Caractère pour afficher les disques dont la taille est paire
    CHAR_CHIP_ODD = "+"
    # Correspondance entre la parité de la taille d'un disque,
    # et le caractère utilisé pour l'afficher.
    DICT_CHAR_CHIP = { 0:CHAR_CHIP_EVEN, 1:CHAR_CHIP_ODD }

    def __init__(self, listMast):
        """ fonction constructeur. listMast est une liste d'objet Mast, contenant les poteaux
        à afficher. L'ordre d'affichage des poteaux, de gauche à droite, correspond à l'ordre
        dans la liste. Cette liste n'est pas obligée de contenir 3 poteaux. On pourrait en
        avoir plus ou moins que ça. (Mais en vrai on le fait pas). """

        self.listMast = listMast
        self.determineDimensions()

    def determineDimensions(self):
        """ fonction a exécuter au début, avant de faire des affichages de poteaux.
        Elle permet d'initialiser des valeurs internes : dimension des poteaux,
        la taille d'une ligne complète, etc."""

        # Nombre total de disque dans le jeu.
        self.nbTotalChip = sum([ mast.get_nb_chips() for mast in self.listMast ])
        # Taille du plus gros disque dans le jeu.
        self.sizeMaxChip = max([ mast.get_max_size_chips() for mast in self.listMast ])
        # Hauteur des poteaux
        self.mastHeight = self.nbTotalChip + self.HEIGHT_MAST_MARGIN
        # Largeur des poteaux (Tous les poteaux doivent pouvoir afficher le plus gros disque).
        # Donc la largeur d'un poteau, c'est la taille en caractère du plus gros disque.
        self.mastWidth = self.sizeMaxChip*2 + 1
        # Nombre de poteaux
        nbMast = len(self.listMast)
        # Largeur totale d'une ligne, pour afficher tous les poteaux.
        # Il faut tenir compte du nombre de poteaux, de leur largeurs,
        # mais aussi du nombre d'intervalle entre les poteaux, et de la largeur de ces intervaux.
        # (Je dis intervaux et je vous emmerde)
        self.totalWidth = sum((self.mastWidth * nbMast,
                               self.NB_SPACE_BETWEEN * (nbMast-1)))

        # Chaîne de caracètre à afficher pour l'étage d'un poteau ne contenant pas de disque.
        # Il faut des espaces, autant que la taille max d'un disque, avec au milieu le petit
        # caractère montrant que c'est juste un poteau avec rien autour.
        self.strNoChip = "".join((" "*self.sizeMaxChip,
                                  self.CHAR_MAST,
                                  " "*self.sizeMaxChip))

        # Chaîne de caractère à afficher pour le sol. C'est la largeur totale d'une ligne,
        # avec le caractère idoinement utilisé pour le sol. Ha ha.
        self.strGround = self.CHAR_GROUND * self.totalWidth

    def strChip(self, chip):
        """ renvoie une chaîne de caractère représentant un disque (ou une absence de disque).
        La chaîne renvoyée a une taille fixe, égale à self.mastWidth.
        (il y a éventuellement des espaces de part et d'autres du disque, afin de la compléter).
        Ca permet d'utiliser cette chaîne pour afficher directement l'étage d'un poteau.
        Quel que soit le contenu de cet étage.
        Le paramètre chip est soit None (absence de disque), soit un objet Chip.
        """

        if chip is None:
            # pas de disque. On renvoie directement la chaîne de caractère correspondant à
            # un étage de poteau sans disque.
            return self.strNoChip
        else:
            # Y'a un disque. On calcule sa largeur en caractère
            chipDisplayWidth = chip.size*2 + 1
            # Calcul du nombre d'espace à écrire de part et d'autre du disque, pour compléter.
            nbSpace = (self.mastWidth - chipDisplayWidth) // 2
            strSpace = " " * nbSpace
            # Détermination du caractère à utiliser pour afficher le disque (selon qu'il a une
            # taille paire ou impaire)
            charChip = self.DICT_CHAR_CHIP[chip.size & 1]
            strChip = charChip * chipDisplayWidth
            # On colle tout : les espaces, le disque, encore les espaces.
            return "".join((strSpace, strChip, strSpace))

    def display(self):
        """ Affiche la liste des poteaux, côte à côte, avec les disques.
        Le tout est balancé sur la sortie standard."""

        # On parcourt tous les étages, depuis le haut (self.mastHeight - 1) vers le bas (0).
        for floorIndex in range(self.mastHeight-1, -1, -1):

            # Pour un étage, on prend tous les poteaux un par un, et on récupère la chaîne
            # de caractère représentant cet étage de ce poteau. (Qui contient un disque, ou pas)
            listStrChip = [ self.strChip(mast.get_chip(floorIndex))
                            for mast in self.listMast ]

            # On concatène ces chaînes de caractère, avec quelques espaces entre,
            # pour faire les intervaux. (Voilà)
            strFloor = self.STR_SPACE_BETWEEN.join(listStrChip)
            # Ca fait une grande ligne, affichant un étage pour tous les poteaux.
            print(strFloor)

        # Affichage de la grande ligne représentant le sol
        print(self.strGround)
        # Et un p'tit saut de ligne juste pour déconner.
        print("")


class TurnDisplayer():
    """ Classe affichant sur la sortie standard la description d'un coup joué.
    Avec quelques vagues explications indiquant comment on a déduit le coup.
    Type MVC : Vue """

    # Dictionnaire de correspondance <type de mouvement> -> <description du type de mouvement>
    DICT_STR_FROM_MOVEMENT_TYPE = {
        Movement.OTHER_CHIP: "Un disque autre que le petit disque",
        Movement.TINY_CHIP_FORWARD: "Le petit disque, vers l'avant",
        Movement.TINY_CHIP_BACKWARD: "Le petit disque, vers l'arriere",
    }

    # Dictionnaire de correspondance <type de poteau> -> <description du type de poteau>
    DICT_STR_FROM_MAST_TYPE = {
        MastType.START: "poteau de depart (a gauche)",
        MastType.INTERM: "poteau intermediaire (au milieu)",
        MastType.END: "poteau de fin (a droite)",
    }

    # Pas de fonction constructeur. Pas besoin.

    def display(self, nb_gaps, moveType, mast_source, mast_dest):
        """ Affiche la description d'un coup joué. Le blabla est balancé sur la sortie standard.
        Paramètre : c'est les infos renvoyée par la fonction hanoiSolver.determineNextChipMovement
         - nb_gaps. Entier positif. Nombre de coupures comptées dans le jeu.
         - moveType. Type de mouvement effectué. Une valeur de type Movement.*.
         - Mast_source : le poteau de source.
         - Mast_dest : le poteau de destination. """

        print("Nombre de coupures dans l'ordre des disques :", nb_gaps)
        strMoveType = self.DICT_STR_FROM_MOVEMENT_TYPE[moveType]
        print("Type de mouvement :", strMoveType)
        strMast_sourceType = self.DICT_STR_FROM_MAST_TYPE[mast_source.mast_type]
        print("Poteau source         :", strMast_sourceType)
        strMast_destType = self.DICT_STR_FROM_MAST_TYPE[mast_dest.mast_type]
        print("Poteau de destination :", strMast_destType)


# --- Les fonctions qui coordonnent tout l'ensemble. ---

def solveFullGame(nbChip):
    """ Fonction résolvant entièrement un jeu de tour de Hanoï, tout en affichant
    la succession des coups joués, et la situation de jeu entre chaque coup.
    nbChip est un entier strictement positif, indiquant le nombre de disques présents
    initialement sur le poteau de départ.
    Type MVC : Contrôleur """

    # Création du jeu, avec les poteaux et les disques dessus.
    hanoi_game = HanoiGame(nbChip)

    # Initialisation des classes de Vue, qui afficheront la situation du jeu et la
    # description des coups joués.
    listMast = (hanoi_game.mast_start, hanoi_game.mast_interm, hanoi_game.mast_end)
    listMastDisplayer = ListMastDisplayer(listMast)
    turnDisplayer = TurnDisplayer()

    # Booléen à la con
    gameNotFinished = True

    while gameNotFinished:

        # On affiche la situation de jeu actuel. Les 3 poteaux, avec la disposition des disques.
        listMastDisplayer.display()
        # Création de la classe résolvant le jeu.
        hanoiSolver = HanoiSolver(hanoi_game)
        # Utilisation de cette classe pour déterminer le prochain coup à jouer,
        # en se basant uniquement sur la situation de jeu actuelle.
        movementInfo = hanoiSolver.determineNextChipMovement()

        if movementInfo is None:
            # Pas d'info valide concernant le prochain coup à jouer.
            # Ca veut dire que le jeu est fini, les disques sont bien rangés sur le poteau de fin.
            print("C'est fini !!")
            # On peut se casser de la boucle.
            gameNotFinished = False

        else:
            # Les infos concernant le prochain coup à jouer sont valides. On les décompose.
            (nb_gaps, moveType, mast_source, mast_dest) = movementInfo
            # Affichage de la description du coup à jouer.
            turnDisplayer.display(nb_gaps, moveType, mast_source, mast_dest)
            # On effectue le déplacement d'un disque, selon ce qu'a déduit le hanoiSolver.
            hanoi_game.move_chip(mast_source, mast_dest)

        # On détruit le hanoiSolver. On en recrééra un autre à la prochaine itération.
        # Ca permet d'être vraiment sûr qu'on ne retient aucune info entre deux coups à jouer.
        del hanoiSolver


def main():
    """
    Programme principal, comme son nom l'indique. Captain Obvious, oui.
    Faut essayer un jeu avec un nombre de disque pair, et un autre avec un nombre impair,
    car les deux cas sont pas tout à fait pareil. (le mouvement du petit disque est pas le même)
    """

    print("="*79)
    print("Les tours de Hanoi avec 3 disques")
    print("="*79)
    solveFullGame(3)

    print("="*79)
    print("Les tours de Hanoi avec 4 disques")
    print("="*79)
    solveFullGame(4)


if __name__ == "__main__":
    main()

