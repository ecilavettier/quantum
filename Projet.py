#                                                                      Projet QUOBLY 
# VETTIER Alice
# BELOURDA Manal
# AIT TAYEB Lyes 
# OKOUMASSOUN Elom
#-----------------------------------------------------Détermination les points critiques sur les images fournis par QUOBLY--------------------------------------------------------


import cv2
import numpy as np
import matplotlib.pyplot as plt
import os
import glob


# path à changer 
dossier_images = r"D:\\me\\QUOBLY"
dossier_images += r"\\Stage_analyse_d'image\\Stage_analyse_d'image\\plot\\Valeur absolu du logarithme\\Good\\"

# Chemin du dossier où vous souhaitez enregistrer les résultats
dossier_resultats = os.path.join(dossier_images, 'resultat')

# Créer le dossier de résultats s'il n'existe pas
if not os.path.exists(dossier_resultats):
    os.makedirs(dossier_resultats)

# Liste pour stocker les noms des images et leurs points critiques associés
resultats = []

# Parcourir toutes les images PNG dans le dossier spécifié
for fichier_image in glob.glob(os.path.join(dossier_images, "*.png")):
    # Charger l'image
    nom_image = os.path.splitext(os.path.basename(fichier_image))[0]
    image = cv2.imread(fichier_image, cv2.IMREAD_GRAYSCALE)

    #Croper l'image afin de travailler uniquement sur le graphe 
    sommets = np.array([
        [153, 709],
        [153, 100],
        [893, 709],
        [893, 100]
    ], dtype=np.float32)

    min_x = int(min(point[0] for point in sommets))
    max_x = int(max(point[0] for point in sommets))
    min_y = int(min(point[1] for point in sommets))
    max_y = int(max(point[1] for point in sommets))

    image = image[min_y:max_y, min_x:max_x]
    #Utiliser une methode de dilatation pour eviter des erreur grossierre lors de la detection des contours
    contours = cv2.dilate(image, kernel=np.ones((1, 1,1), dtype=np.uint8))
    #Decommenter pour affichage
    """
    plt.imshow(contours, cmap='gray')
    plt.title("Image avec les iso-contours")
    plt.axis('off')
    plt.show()"""


    #Les contours ont été uniformiser avec un seuil a 40 déterminer par experimentation (Une moyenne sur les seuils des bonnes images)
    # Binariser l'image en utilisant le seuil calculé
    _, binary_image = cv2.threshold(image, 40, 255, cv2.THRESH_BINARY) 

    """
    plt.imshow(binary_image, cmap='gray')
    plt.title("Image binaire après seuillage standard")
    plt.axis('off')
    plt.show()"""


    """
    Partant de l'image vu precedement on veux en fait ne garder qu'un seul pixel noir par colonne.
    Pour chaque colonne de pixel enregistrer 
    la position de tous les pixels noir puis trouver 
    le pixel median de ce nuage de point
    """
    image = binary_image
    # Initialiser une image vide pour stocker le résultat
    image_resultat = np.copy(image)
    # Parcourir chaque colonne de l'image
    for col in range(0,image_resultat.shape[1]-1):
        # Liste vide pour stocker les positions des pixels noirs dans la colonne actuelle
        positions_pixels_noirs = []
        for lig in range(0,image_resultat.shape[0]-1):
            # Vérifier si le pixel est noir (valeur 0)
            if image[lig,col] == 0:
                # Ajouter la position (x, y) du pixel noir à la liste
                positions_pixels_noirs.append(lig)
                image_resultat[lig,col] = 255
                #passer la valeur du pixel visité à blanc
        

        # Si la liste de positions n'est pas vide
        if positions_pixels_noirs:
            # Calculer la moyenne des coordonnées y des pixels noirs
            somme_l = sum(positions_pixels_noirs)
            moyenne_l = somme_l / len(positions_pixels_noirs)

        # Définir le pixel à la position moyenne calculée comme noir (0) dans l'image résultat
        image_resultat[int(moyenne_l),col] = 0


    # Afficher l'image résultat
    """
    plt.imshow(image_resultat, cmap='gray')
    plt.title("Contours")
    plt.axis('off')
    plt.show()"""

    #cv2.imwrite(nom_im+'1.png', image_resultat)
    #print( image_resultat[:,4])


    #Maintenant qu'on a reussi cette etape on va essayer de combler les incohérences de cette courbe obtenu avec une methode des moindres carrés
    #                                                    Determiner les points d'interets 
    #On va simplifier l'image pour eviter que notre algo de detection des points d'interet soit trop biaisé 
    #On ne va garder qu'un pixel sur 5(Dans le pire des cas on a 5 pixel d'ecart avec notre vrai point d'interêt) 
    #Affinage du nuage de points
    pixels_noirs= []
    image_test = np.copy(image_resultat)
    for col in range(0,image_resultat.shape[1]-1):
        for lig in range(0,image_resultat.shape[0]-1):
            # Vérifier si le pixel est noir (valeur 0)
            image_test[lig,col] = 255
            if (image_resultat[lig,col] == 0) :#"""and (col%5 == 0)"""
            # Ajouter la position (x, y) du pixel noir à la liste
                pixels_noirs.append((lig,col))
                image_test[lig,col] = 0 
    
    etat = "+"
    points_critiques = []
    for i in range (len(pixels_noirs)-6):
        if (etat == "+") and (pixels_noirs[i][0] > pixels_noirs[i+1][0]) and (pixels_noirs[i][0] > pixels_noirs[i+2][0]) and (pixels_noirs[i][0] > pixels_noirs[i+3][0]) and (pixels_noirs[i][0] > pixels_noirs[i+4][0]) and (pixels_noirs[i][0] > pixels_noirs[i+5][0]):
            points_critiques.append((pixels_noirs[i][0],pixels_noirs[i][1]))
            etat = "-"
        if (etat == "-") and (pixels_noirs[i][0] < pixels_noirs[i+1][0]) and (pixels_noirs[i][0] < pixels_noirs[i+2][0]) and (pixels_noirs[i][0] < pixels_noirs[i+3][0]) and (pixels_noirs[i][0] < pixels_noirs[i+4][0]) and (pixels_noirs[i][0] < pixels_noirs[i+5][0]):
            points_critiques.append((pixels_noirs[i][0],pixels_noirs[i][1]))
            etat = "+"
        


    #affichage des points critiques 
    #print(points_critiques)
    #print ( len(points_critiques))

    image_final  = cv2.imread(fichier_image)
    for point in points_critiques :
        # Extraire les coordonnées x et y du point
        x = point[1]
        y = point[0]
        # Vérifier si les coordonnées sont dans les limites de l'image
        if (0 <= x < image_final.shape[1]) and (0 <= y < image_final.shape[0]):
            # Dessiner un cercle vert au point spécifié
            cv2.circle(image_final, (x+153, y+100), 3, (0, 255, 0), -1)


    """plt.imshow(image_final)
    plt.title("Image finale")
    plt.axis('off')
    plt.show()"""
    #cv2.imwrite(nom_im+'_final.png', image_resultat)
    cv2.imwrite(os.path.join(dossier_resultats, f"{nom_image}_final.png"), image_final)
    # Ajouter le nom de l'image et ses points critiques à la liste de résultats
    resultats.append((nom_image, points_critiques))

# Afficher les résultats
print("Résultats traités :")
for nom_image, points_critiques in resultats:
    print(f"{nom_image}: {len(points_critiques)} points critiques détectés")

print("Traitement terminé. Les résultats sont enregistrés dans le dossier de résultats.")

# Chemin du fichier de mesures
chemin_mesures = os.path.join(dossier_images, 'mesures.txt')
# Créer le dossier de résultats s'il n'existe pas
if not os.path.exists(dossier_resultats):
    os.touch(chemin_mesures)
# Écrire les résultats dans le fichier de mesures
with open(chemin_mesures, "w") as f:
    for nom_image, points_critiques in resultats:
        f.write(f"{nom_image}: liste des points critiques pour cette image\n")
        for point in points_critiques:
            f.write(f"({point[1]}, {point[0]})\n")

print("Les mesures ont été enregistrées dans le fichier mesures.txt.")
