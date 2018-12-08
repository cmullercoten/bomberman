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

#ATTENTION, QUAND ON JOUEUR POSE UNE BOMBE ET RESTE SUR PLACE PENDANT LA MÊME DECISION IL ARRÊTE D'ÉVITER LA BOMBE => A CORRIGER

def decision(indiceJoueur, plateau, plateauCouleur, bombes, joueurs, powerups):
    #les bombes qui ont explosées disparaissent de la liste bombe au lieu de devenir des None
    format_bombe(bombes)
    choix = random.choice([True, False, False])
    i = joueurs[indiceJoueur][J_LIGNE]
    j = joueurs[indiceJoueur][J_COLONNE]
    print(" ", "DEBUT TOUR", " ")
    print("plateau")
    print(plateau)
    print("joueur", indiceJoueur, "position", i,j, "bombes", bombes)
    print("choix", choix)
    ListeDirectionsPossibles = directions_possibles(i,j,plateau,bombes)
    print("liste", ListeDirectionsPossibles)
    random.shuffle(ListeDirectionsPossibles)
    for direction in ListeDirectionsPossibles : 
        print("direction", direction)
        print("est dangereuse", est_dangereuse(suivante(i,j,direction)[0], suivante(i,j,direction)[1], bombes, plateau))
        if est_dangereuse(suivante(i,j,direction)[0], suivante(i,j,direction)[1], bombes, plateau) == False : 
            return direction, choix
    print("echec sureté")
    direction = random.choice(ListeDirectionsPossibles)
    print(direction)
    return direction, choix 

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
    PREND EN COMPTE QU'ON NE PEUT MARCHER SUR UNE BOMBE"""
    L = [DIRECTION_NORD, DIRECTION_EST, DIRECTION_SUD, DIRECTION_OUEST]
    D = []
    for direction in L : 
        iprime = suivante(i,j,direction)[0]
        jprime = suivante(i,j,direction)[1]
        if plateau[iprime][jprime] == PLATEAU_VIDE and a_une_bombe(iprime,jprime,bombes)==False:
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
    if bombes == [] : 
        return False
    if a_une_bombe(i,j, bombes) == True : 
        return True
    ListeFlammes = []
    for bomb in bombes : 
        ListeFlammes.append(bomb[B_LONGUEURFLAMMES])
    #print("ListeFlammes", ListeFlammes)
    FlammeMax = max(ListeFlammes)
    #print("FlammeMax", FlammeMax)
    L = [DIRECTION_NORD, DIRECTION_EST, DIRECTION_SUD, DIRECTION_OUEST]
    D = []
    for direction in L : 
        iprime = suivante(i,j,direction)[0]
        jprime = suivante(i,j,direction)[1]
        if plateau[iprime][jprime] == PLATEAU_VIDE :
            D.append(direction)   
    #print("D", D)
    for direction in D :
        k = 0
        while k <= FlammeMax :
        #and direction in directions_possibles(i,j,plateau,bombes) : 
            #print("k", k)
            #print( "suivantes",suivante(i,j,direction)[0], suivante(i,j,direction)[1], "a une bombe ?", a_une_bombe(suivante(i,j,direction)[0], suivante(i,j,direction)[1], bombes))
            if a_une_bombe(suivante(i,j,direction)[0], suivante(i,j,direction)[1], bombes) == True : 
                return True 
            else : 
                #print("else")
                k += 1 
                i,j = suivante(i,j,direction)
    return False

#On définit les frontières sur le modèle suivant : front = [[i1,j1], [i2,j2], [i3,j3]]

def creer_map(plateau,joueur) : 
    """fonction qui crée une copie du labyrinthe dans laquelle on met des ∞ (événtuellement codé par des -1 p. ex) partout, sauf
à l’endroit du personnage où on met un 0."""
    map = deepcopy(plateau)
    for i in range(len(map)):
        for j in range(len(map)[i]):
            map[i][j] = -1
    map[joueur[indiceJoueur][J_LIGNE]][joueur[indiceJoueur][J_COLONNE]] = 0 
    return map

def front_sup(front, map, plateau): 
    front_superieure = []
    for case in front : 
        liste_direction = directions_possibles(case[0], case[1], plateau, bombes)
        for direction in liste_direction : 
            front_superieure.append([suivante(case[0], case[1], direction)[0], suivante(case[0], case[1], direction)[1]])
    for case in front_superieure : 
        if map[case[0]][case[1]] != -1 : 
            front_superieure.remove(case)
    return front_superieure
    
    
#def safe_poser_bombes(joueurs, plateau, bombes):
    #étudier les cases atteignables

#def meilleur_trajet(joueurs, ibut, jbut):
#    i = joueurs[indiceJoueur][J_LIGNE]
#    j = joueurs[indiceJoueur][J_COLONNE]

def format_bombe(bombes):
    while None in bombes : 
        bombes.remove(None)