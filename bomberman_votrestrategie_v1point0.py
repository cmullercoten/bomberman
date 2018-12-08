# -*- coding: utf-8 -*-
"""
Created on Thu Sep 20 10:19:44 2018

@author: Laurent
"""
import random
from copy import deepcopy

PLATEAU_VIDE = 0
PLATEAU_PIERRE = 1
PLATEAU_BOIS = 2

DIRECTION_NORD = 0
DIRECTION_EST = 1
DIRECTION_SUD = 2
DIRECTION_OUEST = 3
DIRECTION_ATTENTE = 4

B_LIGNE = 0
B_COLONNE = 1
B_LONGUEURFLAMMES = 2
B_JOUEUR = 3

J_LIGNE = 0
J_COLONNE = 1
J_DECISION = 2
J_LONGUEURFLAMMES = 3
J_NOMBREBOMBES = 4
J_BOMBESRESTANTES = 5
J_VITESSE = 6

POWERUP_NOMBREBOMBES = 1
POWERUP_LONGUEURFLAMMES = 2
POWERUP_VITESSE = 3

PU_LIGNE = 0
PU_COLONNE = 1
PU_NATURE = 2


#ATTENTION, QUAND LE JOUEUR S'APPRETE A POSER UNE BOMBE ET QU'IL REGARDE LE TRAJET JUSQU'A LA CASE SAFE IL NE VERIFIE PAS SI LES CASES DU TRAJET SONT DANGEREUSES OU NON --> RAJOUTER UN TEST AVEC BOMBE (non fictive sinon les cases seront forcément pas safe) POUR VERIFIER QUE LE TRAJET EST SAFE ? > ATTENTION CAR BOMBES FICTIVE EST RENTRÉ EN ARGUMENT DE MEILLEUR CHEMIN DANS CE CAS, IL FAUT DONC RECRÉER BOMBES VERITABLES EN SUPPRIMANT LA BOMBE DE LA CASE SUR LAQUELLE ON EST DE LA LISTE
# --> Encore mieux, rajouter une notion de temporalité ? Vérifier si les cases du trajet seront safe AU MOMENT OU ON Y SERA ! :D
#   > Déjà il vérifie que la case juste à côté de lui n'est pas dangereuse avant de marcher dessus quand il pose une nouvelle bombe mais bon
#   > Le rapport amélioration de l'efficacité/temps passé à coder n'est clairement pas ouf lorsqu'on rajoute la temporalité, mieux vaut vérifier que toutes les cases du trajet sont safe avant de poser une bombe
#   > PLUS vérifier que la case safe est atteignable avant que la bombe qu'on compte poser n'explose (indice de la carte inférieur à 5 ? --> relou) 

#Une fois ça réglé --> Si personnage pas en danger, avant de vérifier si c'est safe de poser une bombe, vérifier si c'est interessant de poser une bombe (que toutes les cases que la bombe atteindra sont pas déjà coloriées et un plateau vide) 
#Si vraiment je suis déter : créer une carte ou les cases ont un numéro d'interêt --> + 1 point par case coloriée si une bombe est posée là, + 0,5 point par bloc détruit ? 

def decision(indiceJoueur, plateau, plateauCouleur, bombes_reloues, joueurs, powerups):
    #les bombes qui ont explosées disparaissent de la liste bombe au lieu de devenir des None
    bombes = format_bombe(bombes_reloues)
    #Tranquille ça pose les variables
    i = joueurs[indiceJoueur][J_LIGNE]
    j = joueurs[indiceJoueur][J_COLONNE]
    print(" ")
    print(" ", "DEBUT TOUR", " ")
    print("plateau")
    print(plateau)
    print("joueurs", indiceJoueur, "position", i,j, "bombes", bombes)
    print("joueurs complet", joueurs)
    print("plateauCouleur", plateauCouleur)
    #Déjà est-ce que le mec est en sécurité ? 
    #Si c'est dangereux :
    print("est_dangereuse", est_dangereuse(i,j,bombes,plateau))
    if est_dangereuse(i,j,bombes,plateau) == True : 
        destination = [0,0]
        fuite_possible, destination[0], destination[1] = closer_safe_case(indiceJoueur,joueurs,plateau, bombes)
        #Et qu'il peut fuir : 
        print("fuite_possible", fuite_possible)
        if fuite_possible : 
            trajet = meilleur_chemin(indiceJoueur, joueurs, plateau, bombes, destination)
            print("trajet", trajet)
            print("RETURN", direction_de_case(indiceJoueur, joueurs, trajet[-2]), False)
            #Hop hop hop on s'enfuie
            return direction_de_case(indiceJoueur, joueurs, trajet[-2]), False
        #Si tu peux pas fuir... Prie pour ton âme ? 
        else : 
            print("RETURN", DIRECTION_ATTENTE, False)
            return DIRECTION_ATTENTE, False
    #Si c'est pas dangereux : 
    else : 
        #Est-ce que c'est ok de poser une bombe ? 
        bombes_fictives = deepcopy(bombes)
        bombes_fictives.append([i,j,joueurs[indiceJoueur][J_LONGUEURFLAMMES], indiceJoueur])
        # print("bombes_fictives",bombes_fictives)
        # print("closer_safe_case(indiceJoueur,joueurs,plateau, bombes_fictives)", closer_safe_case(indiceJoueur,joueurs,plateau, bombes_fictives))
        # print("closer_safe_case(indiceJoueur,joueurs,plateau, bombes_fictives)[0]", closer_safe_case(indiceJoueur,joueurs,plateau, bombes_fictives)[0])
        #Si oui : 
        print("est-ce safe de poser une bombe ?", closer_safe_case(indiceJoueur,joueurs,plateau, bombes_fictives)[0])
        if closer_safe_case(indiceJoueur,joueurs,plateau, bombes_fictives)[0] == True :
            #Bah pose ta bombe et commence à fuir mon ami
            securite, i_securite, j_securite = closer_safe_case(indiceJoueur,joueurs,plateau, bombes_fictives)
            print("du coup tu la poses et tu vas en", i_securite, j_securite) 
            trajet = meilleur_chemin(indiceJoueur,joueurs,plateau,bombes_fictives,[i_securite, j_securite])
            print("trajet", trajet)
            print("est ce que la case sur laquelle on s'apprête à marcher est dangereuse ?")
            print("case", trajet[-2][0], trajet[-2][1], "test", est_dangereuse(trajet[-2][0], trajet[-2][1],bombes, plateau))
            if est_dangereuse(trajet[-2][0], trajet[-2][1],bombes, plateau) == False : 
                if case_utile(trajet[-2][0], trajet[-2][1], indiceJoueur, joueurs, plateau, plateauCouleur, bombes) > 0 : 
                    print("RETURN", direction_de_case(indiceJoueur, joueurs, trajet[-2]), True)
                    return direction_de_case(indiceJoueur, joueurs, trajet[-2]), True
        #Et si c'est complètement con de poser une bombe :
        print("du coup go en mode random")
        #Go vadrouiller au hasard 
        ListeDirectionsPossibles = directions_possibles(i,j,plateau,bombes)
        ListeDirectionsPossibles.append(DIRECTION_ATTENTE)
        random.shuffle(ListeDirectionsPossibles)
        for direction in ListeDirectionsPossibles : 
            # print("direction", direction)
            # print("est dangereuse", est_dangereuse(suivante(i,j,direction)[0], suivante(i,j,direction)[1], bombes, plateau))
            #Mais toujours dans la sécurité la plus absolue
            if est_dangereuse(suivante(i,j,direction)[0], suivante(i,j,direction)[1], bombes, plateau) == False : 
                print("RETURN", direction, False)
                return direction, False


def suivante(i,j,direction):
    if direction == DIRECTION_NORD:
        return i-1, j
    if direction == DIRECTION_EST:
        return i, j+1
    if direction == DIRECTION_SUD:
        return i+1, j
    if direction == DIRECTION_OUEST:
        return i, j-1
    if direction == DIRECTION_ATTENTE:
        return i, j



def directions_possibles(i,j,plateau,bombes):
    """donne les directions dans lesquelles on peut se déplacer à partir de la case i, j
    PREND EN COMPTE QU'ON NE PEUT MARCHER SUR UNE BOMBE
    NE PROPOSE PAS D'ATTENDRE"""
    # print(" ")
    # print(" ", "ENTER DIRECTIONS POSSIBLES", " ")
    L = [DIRECTION_NORD, DIRECTION_EST, DIRECTION_SUD, DIRECTION_OUEST]
    D = []
    for direction in L : 
        # print("ENTER FOR")
        # print("D", D)
        # print("direction", direction)
        iprime = suivante(i,j,direction)[0]
        jprime = suivante(i,j,direction)[1]
        # print("coordonnée primes", iprime, jprime) 
        # print("plateau en coordonnées primes", plateau[iprime][jprime])
        # print("test plateau vide",plateau[iprime][jprime] == PLATEAU_VIDE)
        # print("a une bombe ? ", a_une_bombe(iprime,jprime,bombes))
        if plateau[iprime][jprime] == PLATEAU_VIDE and a_une_bombe(iprime,jprime,bombes)==False:
            # print("if passé")
            D.append(direction)
    return D



def a_une_bombe(i,j,bombes):
    if bombes == []:
        return False
    for bomb in bombes : 
        if bomb[B_LIGNE] == i and bomb[B_COLONNE]==j : 
            return True
    return False



def est_dangereuse(i,j,bombes,plateau):
    # print("ENTER EST DANGEREUSE")
    # print("i,j", i,j)
    iinitial = i 
    jinitial = j 
    if bombes == [] : 
        return False
    if a_une_bombe(i,j, bombes) == True : 
        return True
    ListeFlammes = []
    for bomb in bombes : 
        ListeFlammes.append(bomb[B_LONGUEURFLAMMES])
    # print("ListeFlammes", ListeFlammes)
    FlammeMax = max(ListeFlammes)
    # print("FlammeMax", FlammeMax)
    L = [DIRECTION_NORD, DIRECTION_EST, DIRECTION_SUD, DIRECTION_OUEST]
    D = []
    for direction in L : 
        iprime = suivante(i,j,direction)[0]
        jprime = suivante(i,j,direction)[1]
        if plateau[iprime][jprime] == PLATEAU_VIDE :
            D.append(direction)   
    # print("D", D)
    for direction in D :
        # print("direction", direction)
        k = 0
        i = iinitial
        j = jinitial
        while k <= FlammeMax :
        #and direction in directions_possibles(i,j,plateau,bombes) : 
            # print("k", k)
            # print( "suivantes",suivante(i,j,direction)[0], suivante(i,j,direction)[1], "a une bombe ?", a_une_bombe(suivante(i,j,direction)[0], suivante(i,j,direction)[1], bombes))
            if a_une_bombe(suivante(i,j,direction)[0], suivante(i,j,direction)[1], bombes) == True : 
                return True 
            else : 
                # print("else")
                k += 1 
                i,j = suivante(i,j,direction)
    return False



#On définit les frontières sur le modèle suivant : front = [[i1,j1], [i2,j2], [i3,j3]]

def creer_map(indiceJoueur, plateau,joueurs) : 
    """fonction qui crée une copie du labyrinthe dans laquelle on met des ∞ (événtuellement codé par des -1 p. ex) partout, sauf
à l’endroit du personnage où on met un 0."""
    map = deepcopy(plateau)
    for i in range(len(map)):
        for j in range(len(map[i])):
            map[i][j] = -1
    map[joueurs[indiceJoueur][J_LIGNE]][joueurs[indiceJoueur][J_COLONNE]] = 0 
    return map



def front_sup(front, map, plateau,bombes): 
    front_superieure = []
    # print(map)
    for case in front : 
        liste_direction = directions_possibles(case[0], case[1], plateau, bombes)
        # print("case", case)
        # print("liste direction", liste_direction)
        for direction in liste_direction : 
            front_superieure.append([suivante(case[0], case[1], direction)[0], suivante(case[0], case[1], direction)[1]])
    for case in front_superieure : 
        if map[case[0]][case[1]] != -1 : 
            front_superieure.remove(case)
    return front_superieure


#Cette fonction a été fusionnée avec closer_safe_case :
def safe_poser_bombes(indiceJoueur, joueurs, plateau, bombes):
    map = creer_map(indiceJoueur, plateau,joueurs)
    i = joueurs[indiceJoueur][J_LIGNE]
    j = joueurs[indiceJoueur][J_COLONNE]
    #variable qui prend en compte toutes les bombes posées plus celle qu'on s'apprête éventuellement à poser
    bombes_fictives = deepcopy(bombes)
    bombes_fictives.append([i,j,joueurs[indiceJoueur][J_LONGUEURFLAMMES], indiceJoueur])
    front = front_sup([[i,j]], map, plateau,bombes_fictives)
    count = 0
    # print(front)
    while front != [] :
        for case in front :
            count += 1 
            # print("i,j", case[0], case[1])
            # print("est dangereuse", est_dangereuse(case[0], case[1], bombes_fictives, plateau))
            if est_dangereuse(case[0], case[1], bombes_fictives, plateau) == False : 
                map[case[0]][case[1]] = count
                return True, case[0], case[1]
            else : 
                map[case[0]][case[1]] = count
        front = front_sup(front, map, plateau, bombes_fictives)
        random.shuffle(front)
    return False, None, None


#Cette fonction est utilisée parce qu'au moment ou on essaye de retracer le chemin entre la case safe et la case ou on est une bombe fictive est posée là ou on est donc la case est considérée comme innateignable et le trajet n'abouti jamais
def directions_possibles_fantome(i,j,plateau,bombes):
    """donne les directions dans lesquelles on peut se déplacer à partir de la case i, j
    NE PREND PAS EN COMPTE LE FAIT QU'ON NE PEUT MARCHER SUR UNE BOMBE
    NE PROPOSE PAS D'ATTENDRE"""
    L = [DIRECTION_NORD, DIRECTION_EST, DIRECTION_SUD, DIRECTION_OUEST]
    D = []
    for direction in L : 
        iprime = suivante(i,j,direction)[0]
        jprime = suivante(i,j,direction)[1]
        if plateau[iprime][jprime] == PLATEAU_VIDE :
            D.append(direction)
    return D

#On met destination sous la forme : destination = [ObjectifI, ObjectifJ]
def meilleur_chemin(indiceJoueur, joueurs, plateau, bombes, destination):
    """renvoie None si la destination n'es pas atteignable
    renvoie le trajet jusqu'à la destination sinon
    avec trajet = [[case 0], [case 1], [destination]]"""
    # print(" ")
    # print(" ", "ENTRE MEILLEUR CHEMIN", " ")
    map = creer_map(indiceJoueur, plateau,joueurs)
    # print("map")
    print(map)
    i = joueurs[indiceJoueur][J_LIGNE]
    j = joueurs[indiceJoueur][J_COLONNE]
    # print("position de départ", i, j)
    front = front_sup([[i,j]], map, plateau,bombes)
    # print("front", front)
    count = 0
    # print("count", count)
    # print("destination", destination)
    while destination not in front :
        # print("ENTER 1ST WHILE")
        if front == [] : 
            # print("RETURN NONE")
            return None
        count += 1 
        # print("count", count)
        for case in front :
            # print("ENTER FOR")
            # print("case", case)
            if map[case[0]][case[1]] == -1 :
                map[case[0]][case[1]] = count
            # print("map", map)
        front = front_sup(front, map, plateau, bombes)
        # print("front", front)
    count += 1
    # print("count", count)
    trajet = [destination]
    # print("trajet", trajet)
    # print("map")
    # print(map)
    # print("position départ", [i,j])
    while [i,j] not in trajet : 
        # print("ENTER WHILE")
        # print("trajet", trajet)
        case_étudiée= [trajet[-1][0], trajet[-1][1]]
        # print("case étudiée", case_étudiée)
        D = directions_possibles_fantome(case_étudiée[0], case_étudiée[1], plateau, bombes)
        # print("D", D)
        longueur_trajet = len(trajet)
        indice_direction = 0 
        while len(trajet) == longueur_trajet : 
            direction = D[indice_direction]
            case_suivante_i, case_suivante_j = suivante(trajet[-1][0], trajet[-1][1], direction)
            # print("case suivante", case_suivante_i, case_suivante_j)
            # print("count", count)
            # print("map[case_suivante_i][case_suivante_j]", map[case_suivante_i][case_suivante_j])
            # print("le test qui rate", map[case_suivante_i][case_suivante_j] == count - 1)
            if map[case_suivante_i][case_suivante_j] == count - 1 :
                count -= 1
                trajet.append([case_suivante_i, case_suivante_j])
            indice_direction += 1
    return trajet
    


def format_bombe(bombes_reloues):
    bombes = deepcopy(bombes_reloues)
    while None in bombes : 
        bombes.remove(None)
    return bombes

def closer_safe_case(indiceJoueur, joueurs, plateau, bombes):
    map = creer_map(indiceJoueur, plateau,joueurs)
    i = joueurs[indiceJoueur][J_LIGNE]
    j = joueurs[indiceJoueur][J_COLONNE]
    #variable qui prend en compte toutes les bombes posées plus celle qu'on s'apprête éventuellement à poser
    front = front_sup([[i,j]], map, plateau,bombes)
    count = 0
    # print(front)
    while front != [] :
        for case in front :
            count += 1 
            # print("i,j", case[0], case[1])
            # print("est dangereuse", est_dangereuse(case[0], case[1], bombes, plateau))
            if est_dangereuse(case[0], case[1], bombes, plateau) == False : 
                map[case[0]][case[1]] = count
                return True, case[0], case[1]
            else : 
                map[case[0]][case[1]] = count
        front = front_sup(front, map, plateau, bombes)
        random.shuffle(front)
    return False, None, None


def direction_de_case(indiceJoueur, joueurs, destination):
    i_joueurs = joueurs[indiceJoueur][J_LIGNE]
    j_joueurs = joueurs[indiceJoueur][J_COLONNE]
    i_destination = destination[0]
    j_destination = destination[1]
    # print("i_joueurs", i_joueurs)
    # print("j_joueurs", j_joueurs)
    # print("i_destination", i_destination)
    # print("j_destination", j_destination)
    direction = None
    if i_joueurs - i_destination == 1 : 
        direction = DIRECTION_NORD
    if i_joueurs - i_destination == -1 : 
        direction = DIRECTION_SUD
    if j_joueurs - j_destination == -1 and direction == None :
        direction = DIRECTION_EST
    if j_joueurs - j_destination == 1 and direction == None :
        direction = DIRECTION_OUEST
    return direction
    
def case_utile(i,j, indiceJoueur, joueurs, plateau, plateauCouleur,bombes):
    feu = joueurs[indiceJoueur][J_LONGUEURFLAMMES]
    print("feu", feu)
    interet = 0
    L = [DIRECTION_NORD, DIRECTION_EST, DIRECTION_SUD, DIRECTION_OUEST]
    for direction in L : 
        if plateau[suivante(i,j,direction)[0]][suivante(i,j,direction)[1]] == PLATEAU_BOIS : 
            interet += 1
    D = directions_possibles(i,j,plateau,bombes)
    iinitial = i 
    jinitial = j
    print("D", D)
    for direction in D : 
        i = iinitial
        j = jinitial
        count = 0 
        while count < feu : 
            iprime, jprime = suivante(i,j,direction)
            print("i, j prime", iprime, jprime)
            if iprime < len(plateau) and jprime < len(plateau[i]) :
                if plateauCouleur[iprime][jprime] != indiceJoueur :
                    interet += 2
            i, j = iprime, jprime
            count += 1 
    return interet
    

##
# Pour mes tests : 
# plateau = [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 0, 0, 0, 2, 2, 0, 2, 2, 2, 2, 2, 2, 2, 0, 0, 2, 0, 0, 0, 1],[1, 0, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 0,1, 2, 1, 2, 1, 0, 1],[1, 2, 2, 2, 2, 2, 2, 2, 0, 2, 2, 2, 2, 2, 2, 2, 0, 0, 2, 2, 1],[1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1],[1, 2, 2, 0, 2, 2, 0, 2, 0, 2, 2,2, 2, 2, 2, 0, 2, 0, 2, 2, 1],[1, 2, 1, 0, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1],[1, 2, 2, 2, 2, 2, 2, 2, 0, 2, 2, 2, 0, 2, 2, 2, 2, 2, 2, 2, 1],[1, 0, 1, 2, 1, 2, 1, 2,1, 2, 1, 2, 1, 0, 1, 2, 1, 2, 1, 2, 1],[1, 2, 2, 2, 2, 2, 2, 2, 2, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 1],[1, 0, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 0, 1],[1, 0, 0, 2, 2,2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 1],[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]
# joueurs = [[2, 1, 0, 2]]
# bombes = []


##
#Milieu de partie : 
# plateau = [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0, 0, 0, 0, 0, 1], [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 2, 1, 2, 1, 0, 1, 0, 1], [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 2, 1, 2, 1, 0, 1, 0, 1], [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 2, 1, 2, 1, 0, 1, 0, 1], [1, 2, 2, 0, 2, 0, 2, 0, 2, 0, 2, 0, 2, 2, 2, 2, 0, 0, 0, 0, 1], [1, 2, 1, 0, 1, 0, 1, 2, 1, 0, 1, 2, 1, 2, 1, 2, 1, 0, 1, 0, 1], [1, 2, 2, 0, 2, 2, 2, 0, 2, 0, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 1], [1, 0, 1, 2, 1, 0, 1, 0, 1, 2, 1, 2, 1, 2, 1, 2, 1, 0, 1, 0, 1], [1, 0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]
# plateauCouleur  = [[-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,-1, -1, -1, -1, -1], [-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, -1, -1, 1, 1, 1,1, 1, -1], [-1, 0,-1, 0, -1, 0, -1, 0, -1, 0, -1, 0, -1, -1, -1, -1, -1, 1, -1, 1, -1], [-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, -1], [-1, 0, -1, 0, -1, 0, -1,0, -1, 0, -1, 0, -1, -1, -1, -1, -1, 1, -1, 1, -1], [-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, -1], [-1, -1, -1, 0, -1, 0, -1, 0, -1, 0, -1,0,-1, -1, -1, -1, -1, 1, -1, 1, -1], [-1, -1, -1, 0, -1,0, -1, 0, -1, 0, -1, -1, -1, -1, -1, -1, 1, 1, 1, 1, -1], [-1, -1, -1, 0, -1, -1, -1, -1, -1, 0, -1, -1,-1, -1, -1, -1, -1, 1, -1, 1, -1], [-1, -1, -1, 0, -1,-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 1, 1, 1, 1, 1, -1], [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,-1,-1, -1, -1, -1, -1, 1, -1, 1, -1], [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 1, 1, 1, -1], [-1, -1, -1,-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]]
# joueurs = [[2, 1, 0, 2]]
# bombes = []

#PlateauCouleur lisible : 
# [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1], 
# [-1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0, -1, -1, -1,  1,  1,  1,  1,  1, -1], 
# [-1,  0, -1,  0, -1,  0, -1,  0, -1,  0, -1,  0, -1, -1, -1, -1, -1,  1, -1,  1, -1], 
# [-1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  1,  1,  1,  1, -1], 
# [-1,  0, -1,  0, -1,  0, -1,  0, -1,  0, -1,  0, -1, -1, -1, -1, -1,  1, -1,  1, -1], 
# [-1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  1,  1,  1,  1, -1], 
# [-1, -1, -1,  0, -1,  0, -1,  0, -1,  0, -1,  0, -1, -1, -1, -1, -1,  1, -1,  1, -1],
# [-1, -1, -1,  0, -1,  0, -1,  0, -1,  0, -1, -1, -1, -1, -1, -1,  1,  1,  1,  1, -1], 
# [-1, -1, -1,  0, -1, -1, -1, -1, -1,  0, -1, -1, -1, -1, -1, -1, -1,  1, -1,  1, -1], 
# [-1, -1, -1,  0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  1,  1,  1,  1,  1, -1],
# [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  1, -1,  1, -1], 
# [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  1,  1,  1, -1], 
# [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]]