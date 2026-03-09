import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import umap 
import mplcursors

# Carga y Escalado
print("Cargando datos...")
df = pd.read_csv(r'E:\Universidad\ALGORITMOS\tarea pasada de rosca\fashion-mnist_test.csv')
X = df.drop('label', axis=1).values
y = df['label'].values
X_scaled = StandardScaler().fit_transform(X)

#  Reducción (Usando UMAP por compatibilidad con Python 3.13)
print("Proyectando datos...")
reducer = umap.UMAP(n_components=2, random_state=42)
X_2d = reducer.fit_transform(X_scaled)

#  Clustering
kmeans = KMeans(n_clusters=10, random_state=42, n_init=10)
clusters = kmeans.fit_predict(X_scaled)

#  ventana 1: Análisis Global 
fig1, ax1 = plt.subplots(figsize=(9, 7))
scatter = ax1.scatter(X_2d[:, 0], X_2d[:, 1], c=clusters, cmap='tab10', s=2, alpha=0.6)
plt.colorbar(scatter, label='Cluster ID')
ax1.set_title('Análisis Global de Clusters (Fashion-MNIST)')

# Cursor interactivo mlp cursor para mostrar información al pasar el mouse
nombres_ropa = {0: "Camiseta", 1: "Pantalón", 2: "Suéter", 3: "Vestido", 4: "Abrigo",
                5: "Sandalia", 6: "Camisa", 7: "Tenis", 8: "Bolso", 9: "Botines"}
cursor = mplcursors.cursor(scatter, hover=True)
@cursor.connect("add")
def on_add(sel):
    idx = sel.index
    sel.annotation.set_text(f"Prenda: {nombres_ropa[y[idx]]}\nCluster: {clusters[idx]}")

# --- VENTANA 2: ANÁLISIS DE SUBCLUSTERS ---
cluster_obj = 0 # Analizaremos las Camisetas
mask = (clusters == cluster_obj)
X_sub_scaled = X_scaled[mask]
X_sub_raw = X[mask]
X_2d_sub = X_2d[mask]

# Sub-clustering
kmeans_sub = KMeans(n_clusters=3, random_state=42, n_init=10)
sub_labels = kmeans_sub.fit_predict(X_sub_scaled)

fig2, ax2 = plt.subplots(figsize=(7, 5))
ax2.scatter(X_2d_sub[:, 0], X_2d_sub[:, 1], c=sub_labels, cmap='viridis', s=10)
ax2.set_title(f'Distribución de Subclusters (Cluster {cluster_obj})')

# --- VENTANA 3: MUESTRA DE IMÁGENES  ---
fig3, axes = plt.subplots(3, 5, figsize=(10, 6))
fig3.suptitle(f'Prendas Reales encontradas en el Cluster {cluster_obj}', fontsize=14)

for i in range(3): # Filas para cada subcluster
    indices = np.where(sub_labels == i)[0][:5]
    for j in range(5):
        ax_img = axes[i, j]
        if j < len(indices):
            img = X_sub_raw[indices[j]].reshape(28, 28)
            ax_img.imshow(img, cmap='gray')
        ax_img.axis('off')
        if j == 0: ax_img.set_title(f"Sub-C {i}", loc='left', fontsize=10)

plt.tight_layout()
plt.show()