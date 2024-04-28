import cv2
import numpy as np
import matplotlib.pyplot as plt


# Charger l'image
image = cv2.imread("I_.png", cv2.IMREAD_GRAYSCALE)

# Define the corner coordinates of the figure (ensure data type is float)
sommets = np.array([
    [153, 709],
    [153, 100],
    [893, 709],
    [893, 100]
], dtype=np.float32)

# Calculate bounding box coordinates (convert to integers for slicing)
min_x = int(min(point[0] for point in sommets))
max_x = int(max(point[0] for point in sommets))
min_y = int(min(point[1] for point in sommets))
max_y = int(max(point[1] for point in sommets))

# Extract the bounding box region
image = image[min_y:max_y, min_x:max_x]

# Display the extracted figure
#cv2.imshow('Figure extraite (Bounding Box)', image)


# Charger l'image en niveau de gris

plt.imshow(image, cmap='gray')
plt.title("Image avec les iso-contours")
plt.axis('off')
plt.show()


contours = cv2.dilate(image, kernel=np.ones((1, 1,1), dtype=np.uint8))
# Afficher l'image avec les contours et les rectangles englobants
plt.imshow(contours, cmap='gray')
plt.title("Image avec les iso-contours")
plt.axis('off')
plt.show()



# Sélectionner une ligne de niveaux (par exemple, la ligne médiane)
ligne_niveaux = image[image.shape[0] // 2, :]

# Binariser l'image en utilisant le seuil calculé
_, binary_image = cv2.threshold(image, 39, 255, cv2.THRESH_BINARY) #Pour le type d'image analyser on s'est rendu compte que ces valeurs de seuils correspondait bien pour les bonnes images

plt.imshow(binary_image, cmap='gray')
plt.title("Image binaire après seuillage standard")
plt.axis('off')
plt.show()

"""
Partant de l'image vu precedement on veux en fait ne garder qu'un seul pixel noir par colonne .
Et bien l'idée c'est quoi pour chaque colonne de pixel j'enregistre 
la position de tous mes pixels noir puis de trouver 
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
    #passer la valeur du pixel visité à noir 
    

  # Si la liste de positions n'est pas vide
  if positions_pixels_noirs:
    # Calculer la moyenne des coordonnées y des pixels noirs
    somme_l = sum(positions_pixels_noirs)
    moyenne_l = somme_l / len(positions_pixels_noirs)


    # Définir le pixel à la position moyenne calculée comme noir (0) dans l'image résultat
    image_resultat[int(moyenne_l),col] = 0

    # Marquer tous les pixels noirs de la liste comme blancs (255) pour éviter de les resélectionner
    #for pixel in positions_pixels_noirs:
    #  image[pixel[1], pixel[0]] = 255

# Afficher l'image résultat
plt.imshow(image_resultat, cmap='gray')
plt.title("Image binaire après seuillage standard")
plt.axis('off')
plt.show()
cv2.imwrite('test_fin1.png', image_resultat)  # Remplacez 'image.jpg' par le nom et le format souhaités
#print( image_resultat[:,4])


#Maintenant qu'on a reussi cette etape on va essayer de combler les incohérences de cette courbe obtenu avec une methode des moindres carrés
#Determiner les points d'interets 
#D'abord il faut determiner le premier pixel noir de l'image 
def find_pixel_image(image):
    # Convertir l'image en gris si pas encore fait 
    if len(image.shape) > 2:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    for col in range(0,image.shape[1]-1):
        for lig in range(0,image.shape[0]-1):
            # Vérifier si le pixel est noir (valeur 0)
            if image[lig,col] == 0:
               return ((lig,col))
    # No black pixels found
    return None

"""
# Example usage
image = cv2.imread('test_fin1.png')  # Replace 'image.jpg' with your image path
first_black_pixel_coord = find_pixel_image(image)
if first_black_pixel_coord:
    x, y = first_black_pixel_coord
    print(f"Premier pixel noir trouvé à: ({x}, {y})")
else:
    print("Aucun pixel noir trouvé dans l'image.")"""

#Maintenant qu'on sait determiner le premier pixel de l'image on va definir un robot a deux états qui va nous aider a determiner les point d'interet
#recuperer la position de tous les pixel noir de l'image 
pixels_noirs= []
for col in range(0,image_resultat.shape[1]-1):
  for lig in range(0,image_resultat.shape[0]-1):
    # Vérifier si le pixel est noir (valeur 0)
    if image[lig,col] == 0:
      # Ajouter la position (x, y) du pixel noir à la liste
      pixels_noirs.append((lig,col))
etat = "+"

#tentative d'affinage/interpolation  des points 
"""pixel = pixels_noirs
for i in range (len(pixels_noirs)-2):
   if (etat == "+") and (pixels_noirs[i][0] > pixels_noirs[i+1][0]):
      pixel.remove((pixels_noirs[i+1][0],pixels_noirs[i+1][1]))
      etat = "-"
   if (etat == "-") and (pixels_noirs[i][0] < pixels_noirs[i+1][0]):
      pixel.remove((pixels_noirs[i+1][0],pixels_noirs[i+1][1]))
      etat = "+"

print(pixel)
pixels_noirs = pixel"""
points_critiques_plus = []
points_critiques_moins = []
for i in range (len(pixels_noirs)-1):
   if (etat == "+") and (pixels_noirs[i][0] > pixels_noirs[i+1][0]):
      points_critiques_plus.append((pixels_noirs[i][0],pixels_noirs[i][1]))
      etat = "-"
   if (etat == "-") and (pixels_noirs[i][0] < pixels_noirs[i+1][0]):
      points_critiques_moins.append((pixels_noirs[i][0],pixels_noirs[i][1]))
      etat = "+"

#test
image_test= np.copy(image_resultat)
for col in range(0,image_test.shape[1]-1):
  for lig in range(0,image_test.shape[0]-1):
    image_test[lig,col] = 255

for (x,y) in points_critiques:
   image_test[x,y] = 0

plt.imshow(image_test, cmap='gray')
plt.title("Image binaire après seuillage standard")
plt.axis('off')
plt.show()