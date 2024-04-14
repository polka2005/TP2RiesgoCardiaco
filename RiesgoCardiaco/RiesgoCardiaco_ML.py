import pandas as pd
import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split
from tensorflow.keras import layers, models
import matplotlib.pyplot as plt
from keras.models import Sequential
from keras.layers import Dense
# Cargar los datos
data = pd.read_csv('datos_de_pacientes_5000.csv', index_col=0)

print("Registros del conjunto de datos:")
print(data)

X = data.drop('riesgo_cardiaco', axis=1)
y = data['riesgo_cardiaco']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

model = Sequential()

model.add(Dense(50, input_shape=(6,), activation='relu', kernel_initializer='uniform'))
model.add(Dense(25, activation='relu', kernel_initializer='random_normal'))
model.add(Dense(35, activation='relu', kernel_initializer='random_normal'))
model.add(Dense(1, activation='relu'))

model.save('modeloRiesgoC.keras')

model.compile(optimizer='adam',
              loss='binary_crossentropy',
              metrics=['accuracy'])



history = model.fit(X_train, y_train, validation_data=(X_test, y_test), verbose=2, batch_size = 1000, epochs=150)

plt.plot(history.history['accuracy'], label='precisión del entrenamiento')
plt.plot(history.history['val_accuracy'], label='Precisión de validación')
plt.xlabel('Épocas')
plt.ylabel('Exactitud')
plt.legend()
plt.show()

