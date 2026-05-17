import librosa
import numpy as np
import os

def extract_audio_features(file_path):
    """
    Load an audio MP3 clip and extract MFCCs and Chroma features.
    Matches the requirements for predicting Valence, Energy, Tension.
    """
    # Load audio, defaulting to librosa's target SR (22050 Hz), mixed to mono
    y, sr = librosa.load(file_path, sr=None)
    
    # 1. MFCCs (Mel-frequency cepstral coefficients)
    # Taking mean and standard dev across time for the 20 coefficients
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=20)
    mfcc_mean = np.mean(mfccs, axis=1)
    mfcc_std = np.std(mfccs, axis=1)
    
    # 2. Chroma features (Captures harmonic / key information)
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    chroma_mean = np.mean(chroma, axis=1)
    chroma_std = np.std(chroma, axis=1)
    
    # 3. Spectral Centroid (measuring 'brightness' of the sound)
    centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
    centroid_mean = np.mean(centroid)
    
    # 4. RMS Energy 
    rms = librosa.feature.rms(y=y)
    rms_mean = np.mean(rms)
    
    # Create feature dictionary
    features = {}
    
    for i in range(20):
        features[f'mfcc_{i+1}_mean'] = mfcc_mean[i]
        features[f'mfcc_{i+1}_std'] = mfcc_std[i]
        
    for i in range(12):
        features[f'chroma_{i+1}_mean'] = chroma_mean[i]
        features[f'chroma_{i+1}_std'] = chroma_std[i]
        
    features['spectral_centroid_mean'] = centroid_mean
    features['rms_energy_mean'] = rms_mean
    
    return features

def batch_extract_audio_features(audio_dir):
    """
    Process all MP3 files in a directory and return a list of feature dictionaries.
    """
    audio_features_list = []
    
    for file_name in os.listdir(audio_dir):
        if file_name.endswith('.mp3'):
            track_idStr = file_name.split('.')[0]
            try:
                track_id = int(track_idStr)
            except ValueError:
                continue
                
            file_path = os.path.join(audio_dir, file_name)
            features = extract_audio_features(file_path)
            features['track_id'] = track_id
            
            audio_features_list.append(features)
            
    return audio_features_list
