from app.utils import train_model

if __name__ == '__main__':
    print('Relancement de l\'entraînement sur data/diagnostics.csv')
    train_model.train(data_path='data/diagnostics.csv', model_dir='app/models_ia')
    print('Terminé. Artefacts sauvegardés dans app/models_ia')
