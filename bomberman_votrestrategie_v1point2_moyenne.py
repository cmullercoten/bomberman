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

CRITERE = 0.5



#ATTENTION LA FONCTION CASE UTILE EST MAL CODÉE : elle n'explore que les cases adjacentes pour voir si il y a un bloc de bois à détruire et explore au delà des blocs pour calculer l'interet des cases à colorier --> il faut fusionner les deux boucles et la faire se stopper si on rencontre un bloc destructible

#NOUVEAU ET MEILLEUR CRITERE : faire la moyenne de l'interet sur toutes les cases puis regarder la case la plus proche telle que son interet est > à 1,5 * moyenne (ou une connerie dans le genre)

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
    print("plateauCouleur")
    print(plateauCouleur)
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
        #On regarde la case sur laquelle il est le plus interessant de poser une bombe 
        meilleure_case = case_utile_atteignable(indiceJoueur, joueurs, plateau, plateauCouleur, bombes)
        print("meilleure_case", meilleure_case)
        #Si on est sur cette case
        if meilleure_case == [i,j] : 
            print("on est sur la meilleure case")
            #Même si normalement c'est déjà vérifié : est-ce que c'est ok de poser une bombe ? 
            bombes_fictives = deepcopy(bombes)
            bombes_fictives.append([i,j,joueurs[indiceJoueur][J_LONGUEURFLAMMES], indiceJoueur])
            #Si oui :
            # print("est-ce safe de poser une bombe ?", closer_safe_case(indiceJoueur,joueurs,plateau, bombes_fictives)[0])
            if closer_safe_case(indiceJoueur,joueurs,plateau, bombes_fictives)[0] == True :
                #Bah pose ta bombe et commence à fuir mon ami
                securite, i_securite, j_securite = closer_safe_case(indiceJoueur,joueurs,plateau, bombes_fictives)
                # print("du coup tu la poses et tu vas en", i_securite, j_securite) 
                trajet = meilleur_chemin(indiceJoueur,joueurs,plateau,bombes_fictives,[i_securite, j_securite])
                # print("trajet", trajet)
                # print("est ce que la case sur laquelle on s'apprête à marcher est dangereuse ?")
                # print("case", trajet[-2][0], trajet[-2][1], "test", est_dangereuse(trajet[-2][0], trajet[-2][1],bombes, plateau))
                if trajet_est_safe(trajet,bombes,plateau) == True :
                    if case_utile(i,j, indiceJoueur, joueurs, plateau, plateauCouleur, bombes) > 0 : 
                        print("RETURN", direction_de_case(indiceJoueur, joueurs, trajet[-2]), True)
                        return direction_de_case(indiceJoueur, joueurs, trajet[-2]), True
        else : 
            #Et si on est pas sur la meilleure case
            print("on est pas sur la meilleure case")
            trajet = meilleur_chemin(indiceJoueur, joueurs, plateau, bombes, meilleure_case)
            print("trajet", trajet)
            if trajet_est_safe(trajet,bombes,plateau) == True :
                print("RETURN", direction_de_case(indiceJoueur, joueurs, trajet[-2]), False)
                return direction_de_case(indiceJoueur, joueurs, trajet[-2]), False
        #Si le trajet jusqu'à la meilleure case est dangereux...
        print("du coup go en mode random")
        #Go vadrouiller au hasard 
        ListeDirectionsPossibles = directions_possibles(i,j,plateau,bombes)
        ListeDirectionsPossibles.append(DIRECTION_ATTENTE)
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
    random.shuffle(D)
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
        # and direction in directions_possibles(i,j,plateau,bombes) : 
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
    # print(" ", "ENTER FRONT SUP", " ")
    front_superieure = []
    # print(map)
    for case in front : 
        liste_direction = directions_possibles(case[0], case[1], plateau, bombes)
        # print("case", case)
        # print("liste direction", liste_direction)
        for direction in liste_direction : 
            front_superieure.append([suivante(case[0], case[1], direction)[0], suivante(case[0], case[1], direction)[1]])
    #ATTENTION, si on fait remove directement les cases de front_superieure alors qu'on fait un for sur les éléments de front_superieure alors on oublie d'en remover la moitié x__x
    front_sans_double = []
    for case in front_superieure : 
        # print("case", case)
        # print(map[case[0]][case[1]])
        if map[case[0]][case[1]] == -1 : 
            if case not in front_sans_double : 
                front_sans_double.append(case)
    random.shuffle(front_sans_double)
    # print("RETURN", front_sans_double)
    return front_sans_double




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
    random.shuffle(D)
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
    # print(map)
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
    """Cette fonction transforme la liste de bombes qui nous est transmise de manière à ce que les bombes qui ont explosées ne soient plus marquées par des none et n'apparaissent tout simplement plus"""
    bombes = deepcopy(bombes_reloues)
    while None in bombes : 
        bombes.remove(None)
    return bombes



def closer_safe_case(indiceJoueur, joueurs, plateau, bombes):
    # print(" ", "ENTER CLOSER SAFE CASE", " ")
    map = creer_map(indiceJoueur, plateau,joueurs)
    i = joueurs[indiceJoueur][J_LIGNE]
    j = joueurs[indiceJoueur][J_COLONNE]
    front = front_sup([[i,j]], map, plateau,bombes)
    count = 0
    # print("front", front)
    while front != [] :
        count += 1 
        for case in front :
            # print("count", count)
            # print("i,j", case[0], case[1])
            # print("est dangereuse", est_dangereuse(case[0], case[1], bombes, plateau))
            if est_dangereuse(case[0], case[1], bombes, plateau) == False : 
                map[case[0]][case[1]] = count
                return True, case[0], case[1]
            else : 
                map[case[0]][case[1]] = count
        front = front_sup(front, map, plateau, bombes)
        # print("front", front)
    return False, None, None



def direction_de_case(indiceJoueur, joueurs, destination):
    """permet de trouver la direction à renvoyer à partir de l'indice d'une case adjacente sur laquelle on veut se diriger"""
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

def trajet_est_safe(trajet, bombes, plateau):
    for case in trajet : 
        i = case[0]
        j = case[1]
        if est_dangereuse(i, j, bombes, plateau) == True : 
            return False
    return True


def case_utile(i,j, indiceJoueur, joueurs, plateau, plateauCouleur,bombes):
    """Attribue à la case un nombre représentant son interet sans aucunement prendre en compte les sentiments de la dite case, laquelle est souvent véxée de son score"""
    # print(" ")
    # print("ENTER CASE UTILE")
    # print("case", i, j)
    feu = joueurs[indiceJoueur][J_LONGUEURFLAMMES]
    # print("feu", feu)
    interet = 0
    if plateauCouleur[i][j] != indiceJoueur :
        interet += 2
    L = [DIRECTION_NORD, DIRECTION_EST, DIRECTION_SUD, DIRECTION_OUEST]
     #On enregistre dans les variables iinitial et jinitial les coordonnées de la case dont on mesure l'utilité
    iinitial = i 
    jinitial = j
    #La variable stop s'enclenchera lorsqu'on rencontre un mur de bois ou de pierre (ça ne sert à rien d'explorer plus loin dans cette direction)
    for direction in L : 
        # print("direction", direction)
        i = iinitial
        j = jinitial
        count = 0 
        stop = False
        while count < feu and not stop : 
            # print("ENTER WHILE")
            iprime, jprime = suivante(i,j,direction)
            # print("iprime, jprime", iprime, jprime)
            # print("count", count)
            if 0 < iprime and 0 < jprime and iprime < len(plateau)-1 and jprime < len(plateau[i])-1:
                # print("iprime et jprime dans le plateau")
                # print("iprime jprime correspond à une case de", plateau[iprime][jprime])
                if plateau[iprime][jprime] != PLATEAU_VIDE : 
                    # print("du coup stop = True")
                    stop = True
                    if plateau[iprime][jprime] == PLATEAU_BOIS :
                        # print("et +1 pour l'interet")
                        interet += 1 
                else :
                    # print("donc une case vide")
                    # print(" de plus sa couleur est", plateauCouleur[iprime][jprime])
                    if plateauCouleur[iprime][jprime] != indiceJoueur :
                    # print("interet += 2")
                        # print("donc interet +=2")
                        interet += 2
            i, j = iprime, jprime
            count += 1 
    # print("RETURN interet", interet)
    # print(" ")
    return interet
    
    
#Ancienne version de case utile : 
# def case_utile(i,j, indiceJoueur, joueurs, plateau, plateauCouleur,bombes):
#     """Attribue à la case un nombre représentant son interet sans aucunement prendre en compte les sentiments de la dite case, laquelle est souvent véxée de son score"""
#     # print(" ")
#     # print("ENTER CASE UTILE")
#     # print("case", i, j)
#     feu = joueurs[indiceJoueur][J_LONGUEURFLAMMES]
#     # print("feu", feu)
#     interet = 0
#     L = [DIRECTION_NORD, DIRECTION_EST, DIRECTION_SUD, DIRECTION_OUEST]
#     for direction in L : 
#         if plateau[suivante(i,j,direction)[0]][suivante(i,j,direction)[1]] == PLATEAU_BOIS : 
#             # print("interet += 1")
#             interet += 1
#     if plateauCouleur[i][j] != indiceJoueur :
#         interet += 2
#     D = directions_possibles(i,j,plateau,bombes)
#     # print("D", D)
#     iinitial = i 
#     jinitial = j
#     for direction in D : 
#         i = iinitial
#         j = jinitial
#         count = 0 
#         while count < feu : 
#             iprime, jprime = suivante(i,j,direction)
#             # print("i, j prime", iprime, jprime)
#             if 0 < iprime and 0 < jprime and iprime < len(plateau)-1 and jprime < len(plateau[i])-1:
#                 if plateauCouleur[iprime][jprime] != indiceJoueur :
#                     # print("interet += 2")
#                     interet += 2
#             i, j = iprime, jprime
#             count += 1 
#     # print("RETURN interet", interet)
#     # print(" ")
#     return interet



    

def case_utile_atteignable(indiceJoueur, joueurs, plateau, plateauCouleur, bombes):
    # # print("ENTER CASE UTILE ATTEIGNABLE")
    map = creer_map(indiceJoueur, plateau,joueurs)
    plateau_utile = deepcopy(map)
    i_joueur = joueurs[indiceJoueur][J_LIGNE]
    j_joueur = joueurs[indiceJoueur][J_COLONNE]
    bombes_fictives = deepcopy(bombes)
    bombes_fictives.append([i_joueur, j_joueur, joueurs[indiceJoueur][J_LONGUEURFLAMMES], indiceJoueur])
    if closer_safe_case(indiceJoueur,joueurs, plateau, bombes_fictives)[0] == True :
        plateau_utile[i_joueur][j_joueur] = case_utile(i_joueur,j_joueur, indiceJoueur, joueurs, plateau, plateauCouleur, bombes)
    front = front_sup([[i_joueur,j_joueur]], plateau_utile, plateau,bombes)
    count = 0
    while front != [] :
        # print("front", front)
        # print("count",count)
        # print("map", map)
        # print("plateau_utile", plateau_utile)
        count += 1 
        for case in front :
            # print("case", case)
            # On crée un "joueur fictif" sur la case à étudier pour vérifier que le joueur peut s'échapper s'il veut poser une bombe là bas
            joueurs_fictif = deepcopy(joueurs)
            joueurs_fictif[indiceJoueur][J_LIGNE] = case[0]
            joueurs_fictif[indiceJoueur][J_COLONNE] = case[1]
            bombes_fictives = deepcopy(bombes)
            bombes_fictives.append([joueurs_fictif[indiceJoueur][J_LIGNE],joueurs_fictif[indiceJoueur][J_COLONNE],joueurs_fictif[indiceJoueur][J_LONGUEURFLAMMES], indiceJoueur])
            # print("joueurs_fictif", joueurs_fictif)
            # print("bombes_fictives", bombes_fictives)
            # print("safe de poser une bombe sur la case ?", closer_safe_case(indiceJoueur,joueurs_fictif,plateau, bombes_fictives)[0])
            if closer_safe_case(indiceJoueur,joueurs_fictif,plateau, bombes_fictives)[0] == True : 
                map[case[0]][case[1]] = count
                plateau_utile[case[0]][case[1]] = case_utile(case[0], case[1], indiceJoueur, joueurs, plateau, plateauCouleur, bombes)
            else : 
                #Permet à la frontière de détecter que la case a déjà été explorée (et n'est juste pas valide)
                plateau_utile[case[0]][case[1]] = -2
        front = front_sup(front, plateau_utile, plateau, bombes)
    meilleure_case = [i_joueur, j_joueur]
    distance_meilleure_case = "infini"
    # print("map", map)
    # print("plateau_utile", plateau_utile)
    moyenne = moyenne_interet(plateau_utile)    
    for i in range(len(map)):
        for j in range(len(map[0])):
            # print("i,j", i, j)
            # print("plateau_utile[i][j]", plateau_utile[i][j])
            if plateau_utile[i][j] != -1 and plateau_utile[i][j] != -2 : 
                # print("i,j", i,j)
                if plateau_utile[i][j] > moyenne :
                    if distance_meilleure_case == "infini" or map[i][j] < distance_meilleure_case : 
                        meilleure_case = [i,j]
                        distance_meilleure_case = map[i][j]
    print("RETURN", meilleure_case, "car son interet est de", plateau_utile[meilleure_case[0]][meilleure_case[1]], "et sa distance", map[meilleure_case[0]][meilleure_case[1]])
    return meilleure_case


def moyenne_interet(plateau_utile):
    somme = 0
    cardinal = 0
    for i in range(len(plateau_utile)):
        for j in range(len(plateau_utile[i])):
            #On ne séléctionne que les cases qui ont un interêt : ni celles qui sont innateignables (-1) ou dangereuses de poser une bombe dessus (-2)
            if plateau_utile[i][j] >= 0 :
                somme += plateau_utile[i][j]
                cardinal += 1 
    return somme/cardinal

##
# Pour mes tests : 
#Début de partie : 
# plateau = [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 1], [1, 0, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 0, 1], [1, 2, 2, 0, 2, 2, 2, 2, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1], [1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1], [1, 2, 2, 2, 2, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 2, 2, 2, 1], [1, 2, 1, 2, 1, 2, 1, 0, 1, 2, 1, 0, 1, 2, 1, 2, 1, 2, 1, 2, 1], [1, 2, 2, 0, 0, 0, 2, 2, 0, 0, 0, 2, 2, 0, 0, 2, 2, 2, 0, 2, 1], [1, 2, 1, 0, 1, 2, 1, 2, 1, 0, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1], [1, 2, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 2, 2, 2, 2, 2, 2, 1], [1, 0, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 0, 1], [1, 0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]
# joueurs = [[1, 1, 0, 2, 1, 1, 0], [11, 19, 0, 2, 1, 1, 0]]
# plateauCouleur = [[-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1], [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1], [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1], [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1], [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1], [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1], [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1], [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1], [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1], [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1], [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1], [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1], [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]]
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


# ((str(plateauCouleur).replace("0", " 0")).replace(" 1", "  1").split("],"))

##
