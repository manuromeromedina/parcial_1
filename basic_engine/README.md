TP4 . Manuel Romero Medina 2105277

Algunas cuestiones para aclarar: 

- Se presentan los códigos para que funciono el motor gráfico y una visualización del mismo.
- Además de exponer los cubos propuestos como  trabajo, se le agregó la rotación de los mismos 
    y a su vez, se realizó un cono como tercera figura. 

- Al ejecuta rlos códigos directos del archivo, note que en realidad los cuadrados se dibujaban 
    pero había una de las caras (frente), que simulaba no dibujarse. Por lo que, utilicé la función 
    DEPTH_TEST en mi window.py en la función on_draw() para darle profundidad al objeto.
    Luego le agregé las rotaciones, en mi scene.py en la función render(). 
    Y por útlimo, como bonus, realicé el mismo procedimiento para el cono verde. Mostrandolo, 
    tambien en el main.py