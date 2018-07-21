# -*- coding: ISO-8859-1 -*-

"""
--------------
Algorithme alzheimerien de résolution des tours de Hanoï.
Réchèr. 2011. Licence CC-BY-SA ou Art Libre.
--------------

C'est alzheimerien, car chaque coup à jouer est déterminé uniquement à partir de
la situation actuelle (C'est à dire la position des disques sur les poteaux) Pas besoin de
se souvenir de ce qu'il s'est passé avant. (les coups précédents, un bordel récursif, ...)

--------------
Méthode :
--------------
Il faut d'abord déterminer le nombre de "coupures" dans l'ordre des disques.
Lorsque deux disques de taille (N-1) et N sont empilés sur un même poteau, il n'y a pas
de "coupure" entre eux. Lorsqu'ils sont sur deux poteaux différents, on compte une coupure.
De plus, lorsque le gros disque du bas n'est pas sur le poteau de fin, on compte aussi
une coupure de plus.

Exemple :
disque 1 (le plus petit disque) sur le poteau de départ.
disques 2 et 3 sur le poteau intermédiaire.
disque 4 (le plus gros disque) sur le poteau de départ.

    |           |           |
    |           |           |
    |           |           |
   +++        -----         |
---------    +++++++        |
.................................

On peut compter les coupures dans l'ordre qu'on veut.
Mettons qu'on parte du plus gros disque vers le plus petit.
 - Le 4 n'est pas sur le poteau de fin. +1 coupure
 - Le 4 et le 3 ne sont pas sur le même poteau. +1 coupure
 - Le 3 et le 2 sont sur le même poteau. OK
 - Le 2 et le 1 ne sont pas sur le même poteau. +1 coupure

Ca nous y fait 3 coupures.

 * Si le nombre de coupures est impair, il faut déplacer le disque 1 (le petit).
    On doit ensuite déterminer où déplacer ce petit disque.
    Si le nombre total de disque est pair, le petit disque doit se déplacer vers l'avant :
    poteau de départ -> poteau intermédiaire -> poteau de fin -> poteau de départ -> etc.
    Si le nombre total de disque est impair, le petit disque doit se déplacer vers l'arrière :
    poteau de fin -> poteau intermédiaire -> poteau de départ -> poteau de fin -> etc.

 * Si le nombre de coupures est pair, il faut déplacer un disque autre que le petit disque.
    Dans ce cas, il n'y a toujours qu'un seul mouvement possible.
     - Parmi les deux poteaux ne contenant pas le petit disque, l'un d'eux est vide.
        Il faut alors déplacer un disque du poteau non vide vers le poteau vide.
     - Parmi les deux poteaux ne contenant pas le petit disque, aucun n'est vide.
        Il faut prendre le plus petit disque parmi les deux poteaux,
        et le déplacer sur l'autre poteau.

Lorsque le nombre de coupures est 0, le jeu est terminé. Tous les disques sont
sur le poteau de fin, et dans le bon ordre, bien evidemment.

Il me faudrait une vraie démonstration mathématique pour prouver que cet algo fonctionne, mais je
sais pas la faire. Au feeling, je dirais que ça fonctionne quel que soit le nombre de disques.

--------------
Vocabulaire (pour le nommage des variables et des objets) :
--------------

chip : un disque posé sur l'un des poteaux du jeu. (Oui le nom est pourri, désolé, sproutch)
size : taille d'un disque. La taille varie de 1 jusqu'au nombre total de disque dans le jeu.
tinyChip : le plus petit disque (celui qui a une taille de 1)
mast : poteau, mât, l'une des tour de Hanoï.

mastStart : le poteau de départ, celui sur lequel tous les disques sont placés au début du jeu.
mastInterm : le poteau intermédiaire.
mastEnd : le poteau de fin, celui sur lequel tous les disques doivent se trouver à la fin du jeu.

mastSource : le poteau de source, pour le coup à jouer en cours.
             (Celui à partir duquel on prend un disque)
mastDest : le poteau de destination, pour le coup à jouer en cours.
           (Celui sur lequel on pose le disque qu'on a pris sur le mastSource)

move, turn : un mouvement = un coup = déplacement d'un disque d'un poteau vers un autre.
gap : coupure dans l'ordre des disques
"""

# Les différentes valeurs possibles pour un type de mouvement.
(MOVEMENT_OTHER_CHIP, # on doit bouger un disque autre que le plus petit disque
 MOVEMENT_TINY_CHIP_FORWARD, # on doit bouger le plups petit disque, vers l'avant
 MOVEMENT_TINY_CHIP_BACKWARD, # on doit bouger le plups petit disque, vers l'arrière
) = range(3)

# Les différentes valeurs possibles pour un type de poteau
(MAST_START, # le poteau de départ
 MAST_INTERM, # le poteau intermédiaire
 MAST_END, # le poteau de fin
) = range(3)


class Chip():
    """ un disque du jeu
    Type MVC : Modèle """

    def __init__(self, size):
        """ fonction constructeur.
        size doit être un nombre entier strictement positif. """

        self.size = size


class Mast():
    """ un poteau du jeu. (N'importe lequel des 3).
    Type MVC : Modèle """

    def __init__(self, mastType):
        """ fonction constructeur.
        mastType est le type de poteau : MAST_START, MAST_INTERM ou MAST_END. """

        # Liste des disques empilés sur le poteau. Cette liste ne contient que des objets Chip.
        # l'élément d'indice 0 est le disque tout en bas. L'élément d'indice 1 est le disque
        # empilé dessus, et etc. Le nombre de disque sur le poteau est variable, of course.
        self.listChip = []
        # La variable contenant le type de mât ne sert à rien pour l'algo en lui-même,
        # c'est juste pour différencier les trois mâts, lorsqu'on décrit les coups joués.
        # (voir la classe TurnDisplayer)
        self.mastType = mastType

    def getTopChip(self):
        """ retourne le disque placé tout en haut du poteau.
        C'est à dire : celui qui est accessible et qu'on peut prendre pour déplacer ailleurs.
        Valeurs de retour : un objet Chip,
        Ou bien la valeur None (aucun disque n'a été placé sur ce poteau) """

        if len(self.listChip) != 0:
            # Il y a au moins un disque. On renvoie le dernier élément de la liste de disque,
            # C'est à dire l'élément le plus haut de la tour.
            return self.listChip[-1]
        else:
            # Pas de disque sur ce poteau.
            return None

    def getChip(self, floorIndex):
        """ retourne un disque placé à un certain étage de la tour.
        (C'est juste un accès 'en lecture'. On n'aura pas le droit de déplacer ce disque).
        floorIndex est un entier positif ou nul, indiquant l'étage où se trouve le disque
        qu'on veut récupérer. (étage 0 = tout en bas).
        Valeurs de retour : un objet Chip,
        Ou bien la valeur None (il n'y a pas de disque à l'étage demandé) """

        if floorIndex < len(self.listChip):
            # il y a un disque à l'étage demandé. On le renvoie
            return self.listChip[floorIndex]
        else:
            # pas de disque à l'étage demandé. (La tour est pas assez haute).
            return None

    def popChip(self):
        """ enlève le disque du haut de ce poteau, et le renvoie.
        Valeurs de retour : un objet Chip. (le disque qu'on vient d'enlever)
        Si le poteau n'a pas de disque, cette fonction fait tout planter. (Et c'est fait exprès)
        """
        if len(self.listChip) != 0:
            # Il y a au moins un disque sur ce poteau. On enlève le dernier élément de la liste
            # (le disque du haut), et on le renvoie.
            return self.listChip.pop()
        else:
            # Pas de disque sur ce poteau. On fait tout planter.
            print "!!! ILLEGAL MOVE !!! poteau vide : ", self.mastType
            assert False

    def addChip(self, chipToAdd):
        """ ajoute un nouveau disque en haut de ce poteau.
        chipToAdd doit être un objet Chip.
        La taille des disques est contrôlée. Si le disque qu'on tente d'ajouter est plus
        grand que le disque se trouvant actuellement en haut du poteau, cette fonction
        fait tout planter. (Et c'est fait exprès aussi). """

        # Récupération du disque actuellement en haut du poteau.
        topChip = self.getTopChip()
        if topChip is None:
            # Pas de disque sur ce poteau. Donc on peut ajouter le nouveau disque sans problème.
            # Le nouveau disque va se mettre à l'indice 0 de self.listChip (tout en bas).
            self.listChip.append(chipToAdd)
        elif topChip.size > chipToAdd.size:
            # Il y a un ou des disques sur ce poteau. Le disque a ajouter à une taille plus petite
            # que le disque en haut du poteau. On peut ajouter le nouveau disque.
            self.listChip.append(chipToAdd)
        else:
            # Le disque a ajouter à une taille plus grande que le disque en haut du poteau.
            # On fait tout planter.
            print "!!! ILLEGAL MOVE !!! poteau : ", self.mastType
            print "chip: ", topChip.size, " chip to add : ", chipToAdd.size
            assert False


class HanoiGame():
    """ Le jeu des tour de Hanoï. Avec les trois poteaux, et les disques dessus.
    Type MVC : Modèle """

    def __init__(self, nbrChip):
        """ fonction constructeur. nbrChip est un entier strictement positif,
        indiquant le nombre total de disques dans le jeu.
        """

        self.nbrChip = nbrChip
        # Création des trois poteaux du jeu (départ, intermédiaire et arrivée)
        self.mastStart = Mast(MAST_START)
        self.mastInterm = Mast(MAST_INTERM)
        self.mastEnd = Mast(MAST_END)

        # Création des disques, et empilement de ces disques sur le poteau de départ.
        # On crée d'abord le disque le plus grand (taille = nbrChip) et on le met sur le poteau
        # (tout en bas), puis on crée un disque un peu plus petit, et on l'empile, etc.
        # Jusqu'au plus petit disque (taille de 1), qui se retrouve tout en haut.
        for chipSize in xrange(self.nbrChip, 0, -1):
            chip = Chip(chipSize)
            self.mastStart.addChip(chip)

    def moveChip(self, mastSource, mastDest):
        """ déplace un disque du poteau mastSource, vers le poteau mastDest.
        mastSource et mastDest sont des objets Mast. (au choix parmi les trois poteaux
        déjà définis dans cette classe même).
        Aucun contrôle n'est effectué sur la possibilité et la légalité du mouvement.
        Ca se fait au niveau des objets Mast."""

        # Récupération du disque se trouvant tout en haut du poteau source.
        # Et en même temps, enlevage de ce disque du poteau source.
        chipToMove = mastSource.popChip()
        # Placement du disque récupéré, sur le poteau de destination.
        mastDest.addChip(chipToMove)


class HanoiSolver():
    """ Résolvateur du jeu des tours de Hanoï. Cette classe analyse la situation présente du jeu,
    à partir d'un objet HanoiGame, et elle en déduit le prochain coup à jouer.
    (c'est à dire : le poteau de source et le poteau de destination)
    La classe ne retient aucune information entre deux déductions de coup à jouer.
    Type MVC : Modèle """

    def __init__(self, hanoiGame):
        """ fonction constructeur. le param hanoiGame doit être un objet de type HanoiGame.
        La classe HanoiSolver ne tripote pas dans hanoiGame.
        Elle se contente de récupérer des infos, en 'lecture seule'"""

        self.hanoiGame = hanoiGame

    def _countGap(self):
        """ Analyse la la situation de jeu définie dans self.hanoiGame,
        et compte le nombre de coupures dans l'ordre des disques.
        Valeurs de retour : un nombre entier positif ou nul.
        Cette fonction compte le nombre de coupures en commençant par le disque le plus grand,
        et par le bas des poteaux. Et elle remonte dans les étages des 3 poteaux"""

        #Création de liste de 2 éléments : la référence vers un objet Mast, et un curseur sur l'étage en cours.
        # On commence à l'étage le plus bas (curseur = 0)
        MastCursorStart = [self.hanoiGame.mastStart, 0]
        MastCursorInterm = [self.hanoiGame.mastInterm, 0]
        MastCursorEnd = [self.hanoiGame.mastEnd, 0]

        listMastCursor = (MastCursorStart, MastCursorInterm, MastCursorEnd)

        # Nombre de coupures actuellement comptées
        nbGap = 0
        # référence vers le poteau sur lequel se trouve le disque précédent.
        # On initialise cette référence au poteau de fin. Car on considère qu'il y a une coupure
        # si le plus grand disque est à un autre endroit que le poteau de fin.
        # (En fait, c'est comme si y'avait un disque de taille nbChip + 1, sur le poteau de fin,
        # qui ne bouge jamais.)
        previousMast = self.hanoiGame.mastEnd

        # currentChipSizeToFind indique la taille du disque qu'on cherche actuellement.
        # On va du plus grand disque (nbrChip) jusqu'au plus petit (1)
        for currentChipSizeToFind in xrange(self.hanoiGame.nbrChip, 0, -1):

            # On cherche le disque dans la liste des 3 poteaux.
            for mastCursor in listMastCursor:

                mast, cursor = mastCursor
                # Pour chaque poteau, on regarde uniquement le disque pointé par son curseur.
                chip = mast.getChip(cursor)

                if chip is not None:
                    # Pour le poteau en cours, et pour le curseur en cours, un disque est présent.
                    if chip.size == currentChipSizeToFind:
                        # La taille du disque du poteau en cours correspond
                        # à la taille du disque actuellement recherchée.
                        # On monte d'un étage le curseur du poteau en cours.
                        mastCursor[1] += 1
                        # On vérifie si le disque précédent et le disque actuellement recherché
                        # sont placés sur le même poteau.
                        if mast != previousMast:
                            # Ils ne sont pas sur le même poteau. Ca fait une coupure de plus.
                            nbGap += 1
                            previousMast = mast
                        # Break un peu dégueu pour sortir de la boucle. C'est pas obligé en fait.
                        # Si on continue, ça plantera pas et l'algo fonctionnera toujours.
                        # C'est juste que ça sert plus à rien.
                        # Allez, on dit qu'on a le droit de faire des break
                        break

        return nbGap

    def _determineTinyChipMovement(self, moveType):
        """ détermine le prochain coup à jouer, dans le cas où on doit déplacer le petit disque.
        moveType doit valoir MOVEMENT_TINY_CHIP_FORWARD, ou MOVEMENT_TINY_CHIP_BACKWARD.
        moveType ne doit pas valoir MOVEMENT_OTHER_CHIP, parce que ça n'aurait aucun sens.
        La fonction fait tout planter si jamais le petit disque ne se trouve pas en haut de l'un
        des 3 poteaux de self.hanoiGame. (Mais ce cas débile n'est jamais censé arriver)

        La fonction renvoie un tuple de 2 éléments : 2 référence vers des objets Mast
         - MastSource : le poteau de source, pour le prochain mouvement à jouer
         - MastDest : le poteau de destination, pour le prochain mouvement à jouer. """

        # Définition du dictionnaire permettant de connaître le poteau de destination en fonction
        # du poteau de source.
        if moveType == MOVEMENT_TINY_CHIP_FORWARD:
            # Le petit disque doit bouger vers l'avant. Le dictionnaire contient donc la config
            # de mouvement suivante :
            # poteau de départ -> poteau intermédiaire -> poteau de fin -> poteau de départ.
            dictTinyChipMovement = {
                self.hanoiGame.mastStart: self.hanoiGame.mastInterm,
                self.hanoiGame.mastInterm: self.hanoiGame.mastEnd,
                self.hanoiGame.mastEnd: self.hanoiGame.mastStart,
            }
        else:
            # Le petit disque doit bouger vers l'arrière. Le dictionnaire contient donc la config
            # de mouvement suivante :
            # poteau de fin -> poteau intermédiaire -> poteau de départ -> poteau de fin.
            dictTinyChipMovement = {
                self.hanoiGame.mastStart: self.hanoiGame.mastEnd,
                self.hanoiGame.mastInterm: self.hanoiGame.mastStart,
                self.hanoiGame.mastEnd: self.hanoiGame.mastInterm,
            }

        listMast = (self.hanoiGame.mastStart,
                    self.hanoiGame.mastInterm,
                    self.hanoiGame.mastEnd)

        # On recherche le petit disque, en vérifiant le disque qui se trouve
        # tout en haut de chaque poteau.
        for mast in listMast:
            chip = mast.getTopChip()
            if chip is not None and chip.size == 1:
                # On a trouvé le petit disque en haut du poteau en cours.
                # Donc ce poteau est le poteau de source.
                # (vu que c'est le petit disque qu'on doit bouger, haha)
                mastSource = mast
                # Détermination du potau de destination en fonction du poteau de source,
                # et du dictionnaire de config des mouvements.
                mastDest = dictTinyChipMovement[mast]
                return mastSource, mastDest

        # Après avoir regardé le haut de tous les poteaux, le petit disque est introuvable.
        # On fait tout planter. (Ca arrive jamais)
        print "fail. tiny Chip introuvable"
        assert False

    def _determineOtherChipMovement(self):
        """ détermine le prochain coup à jouer, dans le cas où on doit déplacer un disque
        autre que le petit disque.
        La fonction renvoie un tuple de 2 éléments : 2 référence vers des objets Mast
         - MastSource : le poteau de source, pour le prochain mouvement à jouer
         - MastDest : le poteau de destination, pour le prochain mouvement à jouer. """

        listMast = (self.hanoiGame.mastStart,
                    self.hanoiGame.mastInterm,
                    self.hanoiGame.mastEnd)

        # Cette liste va contenir 2 éléments, correspondant à 2 poteaux du jeu.
        # Le poteau qu'on éliminera sera celui contenant le petit disque.
        # Chaque élément de cette liste est un tuple de 2 sous-éléments :
        #  - Référence vers le poteau en question.
        #  - * Soit une valeur entière (taille du disque se trouvant tout en haut du poteau)
        #    * Soit la valeur None (le poteau ne contient pas de disque)
        listMastWithSize = []

        # on parcourt la liste des 3 poteaux, pour remplir listMastWithSize
        for mast in listMast:
            chip = mast.getTopChip()
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
            mastSource = listMastWithSize[1][0]
            # et le poteau de destination, c'est celui-là. (le 1er)
            mastDest = listMastWithSize[0][0]
        elif listMastWithSize[1][1] is None:
            # Le 2eme élément de listMastWithSize est un poteau sans disque.
            # Donc le poteau de source, c'est l'autre (le 1er)
            mastSource = listMastWithSize[0][0]
            # et le poteau de destination, c'est celui-là. (le 2eme)
            mastDest = listMastWithSize[1][0]
        elif listMastWithSize[0][1] < listMastWithSize[1][1]:
            # Les deux poteaux contiennent des disques. Et le disque du haut du 1er poteau
            # est plus petit que le disque du haut du 2eme poteau.
            # Le poteau de source est celui avec le plus petit disque (le 1er)
            mastSource = listMastWithSize[0][0]
            # Le poteau de destination c'est l'autre (le 2eme)
            mastDest = listMastWithSize[1][0]
        else:
            # Les deux poteaux contiennent des disques. Et le disque du haut du 1er poteau
            # est plus grand que le disque du haut du 2eme poteau.
            # Le poteau de source est celui avec le plus petit disque (le 2eme)
            mastSource = listMastWithSize[1][0]
            # Le poteau de destination c'est l'autre (le 1er)
            mastDest = listMastWithSize[0][0]

        return mastSource, mastDest

    def determineNextChipMovement(self):
        """ Détermine le prochain coup à jouer, en fonction de la situation de jeu
        définie dans self.hanoiGame.
        Valeur de retour :
         - Soit la valeur None. Dans ce cas, le jeu est déjà fini,
           et tous les disques sont correctement rangés sur le poteau de fin.
         - Soit un tuple de 4 éléments :
            * nbGap. Entier positif. Nombre de coupures comptées dans le jeu.
            * moveType. Type de mouvement à faire. Une valeur parmi MOVEMENT_OTHER_CHIP,
              MOVEMENT_TINY_CHIP_FORWARD ou MOVEMENT_TINY_CHIP_BACKWARD.
            * MastSource : le poteau de source, pour le prochain mouvement à jouer
            * MastDest : le poteau de destination, pour le prochain mouvement à jouer. """

        #on compte le nombre de coupures
        nbGap = self._countGap()
        if nbGap == 0:
            # 0 coupures. Tout est bien rangé, le jeu est fini, on renvoie None.
            return None

        if nbGap & 1 == 0:
            # Le nombre de coupure est pair. Il faut déplacer un disque autre que le petit disque.
            moveType = MOVEMENT_OTHER_CHIP
            # On peut déterminer immédiatement les poteaux de source et destination.
            mastSource, mastDest = self._determineOtherChipMovement()
        else:
            # Le nombre de coupure est impair. Il faut déplacer le petit disque.
            # définition du dictionnaire indiquant le sens du mouvement du petit disque,
            # en fonction d'une parité. 0 : paire. 1 : impaire
            DICT_MOVEMENT_TINY_CHIP = {
                0:MOVEMENT_TINY_CHIP_FORWARD,
                1:MOVEMENT_TINY_CHIP_BACKWARD,
            }
            # Le sens du mouvement du petit disque se détermine en fonction de la parité
            # du nombre total de disque dans le jeu.
            moveType = DICT_MOVEMENT_TINY_CHIP[self.hanoiGame.nbrChip & 1]
            # Détermination des poteaux de source et de destination, pour le petit disque.
            mastSource, mastDest = self._determineTinyChipMovement(moveType)

        return (nbGap, moveType, mastSource, mastDest)


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

        # Récupération d'une liste contenant tous les disques présents dans le jeu.
        # (On fait juste une grosse concaténation des listes de disques de chaque poteau.)
        listTotalChip = reduce(lambda x, y: x+y,
                               (mast.listChip for mast in self.listMast))

        # Nombre total de disque dans le jeu
        self.nbTotalChip = len(listTotalChip)
        # Taille du plus gros disque
        self.sizeMaxChip = max( [ chip.size for chip in listTotalChip ] )
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
            nbSpace = (self.mastWidth - chipDisplayWidth) / 2
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
        for floorIndex in xrange(self.mastHeight-1, -1, -1):

            # Pour un étage, on prend tous les poteaux un par un, et on récupère la chaîne
            # de caractère représentant cet étage de ce poteau. (Qui contient un disque, ou pas)
            listStrChip = [ self.strChip(mast.getChip(floorIndex))
                            for mast in self.listMast ]

            # On concatène ces chaînes de caractère, avec quelques espaces entre,
            # pour faire les intervaux. (Voilà)
            strFloor = self.STR_SPACE_BETWEEN.join(listStrChip)
            # Ca fait une grande ligne, affichant un étage pour tous les poteaux.
            print strFloor

        # Affichage de la grande ligne représentant le sol
        print self.strGround
        # Et un p'tit saut de ligne juste pour déconner.
        print ""


class TurnDisplayer():
    """ Classe affichant sur la sortie standard la description d'un coup joué.
    Avec quelques vagues explications indiquant comment on a déduit le coup.
    Type MVC : Vue """

    # Dictionnaire de correspondance <type de mouvement> -> <description du type de mouvement>
    DICT_STR_FROM_MOVEMENT_TYPE = {
        MOVEMENT_OTHER_CHIP: "Un disque autre que le petit disque",
        MOVEMENT_TINY_CHIP_FORWARD: "Le petit disque, vers l'avant",
        MOVEMENT_TINY_CHIP_BACKWARD: "Le petit disque, vers l'arriere",
    }

    # Dictionnaire de correspondance <type de poteau> -> <description du type de poteau>
    DICT_STR_FROM_MAST_TYPE = {
        MAST_START: "poteau de depart (a gauche)",
        MAST_INTERM: "poteau intermediaire (au milieu)",
        MAST_END: "poteau de fin (a droite)",
    }

    # Pas de fonction constructeur. Pas besoin.

    def display(self, nbGap, moveType, mastSource, mastDest):
        """ Affiche la description d'un coup joué. Le blabla est balancé sur la sortie standard.
        Paramètre : c'est les infos renvoyée par la fonction hanoiSolver.determineNextChipMovement
         - nbGap. Entier positif. Nombre de coupures comptées dans le jeu.
         - moveType. Type de mouvement effectué. Une valeur parmi MOVEMENT_OTHER_CHIP,
           MOVEMENT_TINY_CHIP_FORWARD ou MOVEMENT_TINY_CHIP_BACKWARD.
         - MastSource : le poteau de source.
         - MastDest : le poteau de destination. """

        print "Nombre de coupures dans l'ordre des disques :", nbGap
        strMoveType = self.DICT_STR_FROM_MOVEMENT_TYPE[moveType]
        print "Type de mouvement :", strMoveType
        strMastSourceType = self.DICT_STR_FROM_MAST_TYPE[mastSource.mastType]
        print "Poteau source         :", strMastSourceType
        strMastDestType = self.DICT_STR_FROM_MAST_TYPE[mastDest.mastType]
        print "Poteau de destination :", strMastDestType


def solveFullGame(nbChip):
    """ Fonction résolvant entièrement un jeu de tour de Hanoï, tout en affichant
    la succession des coups joués, et la situation de jeu entre chaque coup.
    nbChip est un entier strictement positif, indiquant le nombre de disques présents
    initialement sur le poteau de départ.
    Type MVC : Contrôleur """

    # Création du jeu, avec les poteaux et les disques dessus.
    hanoiGame = HanoiGame(nbChip)

    # Initialisation des classes de Vue, qui afficheront la situation du jeu et la
    # description des coups joués.
    listMast = (hanoiGame.mastStart, hanoiGame.mastInterm, hanoiGame.mastEnd)
    listMastDisplayer = ListMastDisplayer(listMast)
    turnDisplayer = TurnDisplayer()

    # Booléen à la con
    gameNotFinished = True

    while gameNotFinished:

        # On affiche la situation de jeu actuel. Les 3 poteaux, avec la disposition des disques.
        listMastDisplayer.display()
        # Création de la classe résolvant le jeu.
        hanoiSolver = HanoiSolver(hanoiGame)
        # Utilisation de cette classe pour déterminer le prochain coup à jouer,
        # en se basant uniquement sur la situation de jeu actuelle.
        movementInfo = hanoiSolver.determineNextChipMovement()

        if movementInfo is None:
            # Pas d'info valide concernant le prochain coup à jouer.
            # Ca veut dire que le jeu est fini, les disques sont bien rangés sur le poteau de fin.
            print "C'est fini !!"
            # On peut se casser de la boucle.
            gameNotFinished = False

        else:
            # Les infos concernant le prochain coup à jouer sont valides. On les décompose.
            (nbGap, moveType, mastSource, mastDest) = movementInfo
            # Affichage de la description du coup à jouer.
            turnDisplayer.display(nbGap, moveType, mastSource, mastDest)
            # On effectue le déplacement d'un disque, selon ce qu'a déduit le hanoiSolver.
            hanoiGame.moveChip(mastSource, mastDest)

        # On détruit le hanoiSolver. On en recrééra un autre à la prochaine itération.
        # Ca permet d'être vraiment sûr qu'on ne retient aucune info entre deux coups à jouer.
        del hanoiSolver


if __name__ == "__main__":
    # Programme principal, comme son nom l'indique. Captain Obvious, oui.
    # Faut essayer un jeu avec un nombre de disque pair, et un autre avec un nombre impair,
    # car les deux cas sont pas tout à fait pareil. (le mouvement du petit disque est pas le même)

    print "="*79
    print "Les tours de Hanoi avec 3 disques"
    print "="*79
    solveFullGame(3)

    print "="*79
    print "Les tours de Hanoi avec 4 disques"
    print "="*79
    solveFullGame(4)
